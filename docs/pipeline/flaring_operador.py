#!/usr/bin/env python3
"""Fase 2 — Flaring → CO₂ por operador.

1. Lee los sitios de flaring de **VIIRS Nightfire** (Earth Observation Group, archivo global anual,
   gratuito) y los filtra al AOI de Vaca Muerta.
2. Asigna cada antorcha a su **concesión → operador** (point-in-polygon sobre `concesiones_neuquina.geojson`).
3. Convierte el volumen quemado a **CO₂** y lo cruza con la **producción 2024** por operador (Cap IV,
   Secretaría de Energía, vía streaming) → **intensidad de flaring** (kg CO₂/BOE, % de gas quemado).

Año: 2024 (último año completo común a flaring y producción).

Salidas: `docs/data/flaring_por_operador.csv` y `docs/data/flares_aoi.csv`.

Uso:
    python docs/pipeline/flaring_operador.py
"""
from pathlib import Path
import json
import csv
import requests
import pandas as pd
from shapely.geometry import shape, Point

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "concesiones_neuquina.geojson"
XLSX = next((ROOT / "data" / "flaring").glob("*2024*.xlsx"))
OUT_OP = ROOT / "data" / "flaring_por_operador.csv"
OUT_FL = ROOT / "data" / "flares_aoi.csv"

YEAR = "2024"
PROD_URL = json.loads((ROOT / "data" / "prod_urls.json").read_text())[YEAR]["url"]

# AOI Vaca Muerta (igual que los otros proyectos)
LON0, LON1, LAT0, LAT1 = -70.6, -68.2, -39.2, -37.3

# Factores (ver metodologia.md):
KG_CO2_PER_M3 = 2.0          # combustión de gas natural ≈ 1,9–2,4 kg CO₂/m³ (uso 2,0; ~2 Mt CO₂/BCM)
BBL_PER_M3_OIL = 6.2898
M3_GAS_PER_BOE = 169.9


def produccion_2024_por_operador():
    """Stream del Cap IV 2024, agrega gas (mil m³) y petróleo (m³) por empresa en cuenca Neuquina."""
    url = PROD_URL
    gas_milm3, pet_m3 = {}, {}
    csv.field_size_limit(1 << 24)
    with requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, stream=True, timeout=900) as r:
        r.raise_for_status()
        lines = (ln for ln in r.iter_lines(decode_unicode=True) if ln)
        for row in csv.DictReader(lines):
            if (row.get("cuenca") or "").strip().upper() != "NEUQUINA":
                continue
            op = (row.get("empresa") or "").strip()
            if not op:
                continue
            try:
                gas_milm3[op] = gas_milm3.get(op, 0.0) + float(row.get("prod_gas") or 0)
                pet_m3[op] = pet_m3.get(op, 0.0) + float(row.get("prod_pet") or 0)
            except ValueError:
                pass
    return gas_milm3, pet_m3


def main():
    # --- concesiones → operador ---
    gj = json.loads(GEO.read_text(encoding="utf-8"))
    polys = [(shape(ft["geometry"]), (ft["properties"].get("operador") or "").strip(),
              ft["properties"].get("nombre", "")) for ft in gj["features"]]

    # --- flares en AOI ---
    df = pd.read_excel(XLSX, sheet_name="flare upstream")
    bcm_col = [c for c in df.columns if c.startswith("BCM")][0]
    df = df[(df.Longitude.between(LON0, LON1)) & (df.Latitude.between(LAT0, LAT1))].copy()

    flares = []
    for _, r in df.iterrows():
        pt = Point(r.Longitude, r.Latitude)
        op, conc = "No asignado", ""
        for geom, operador, nombre in polys:
            if geom.contains(pt):
                op, conc = operador or "No asignado", nombre
                break
        flares.append({"lat": round(r.Latitude, 5), "lon": round(r.Longitude, 5),
                       "bcm": float(r[bcm_col]), "mm3": round(float(r[bcm_col]) * 1000, 2),
                       "operador": op, "concesion": conc})

    # --- producción 2024 por operador ---
    print("Bajando producción Cap IV 2024 (streaming)…", flush=True)
    gas_milm3, pet_m3 = produccion_2024_por_operador()

    # --- agregación por operador ---
    ops = {}
    for fl in flares:
        d = ops.setdefault(fl["operador"], {"n": 0, "bcm": 0.0})
        d["n"] += 1
        d["bcm"] += fl["bcm"]

    rows = []
    for op, d in ops.items():
        flared_mm3 = d["bcm"] * 1000                       # Mm³ quemados
        co2_t = d["bcm"] * 1e9 * KG_CO2_PER_M3 / 1000      # toneladas CO₂
        gas_prod_mm3 = gas_milm3.get(op, 0.0) / 1000       # mil m³ → Mm³
        oil_m3 = pet_m3.get(op, 0.0)
        boe = oil_m3 * BBL_PER_M3_OIL + (gas_prod_mm3 * 1e6) / M3_GAS_PER_BOE
        rows.append({
            "operador": op,
            "n_flares": d["n"],
            "gas_quemado_mm3": round(flared_mm3, 1),
            "gas_producido_mm3": round(gas_prod_mm3, 1),
            "pct_gas_quemado": round(100 * flared_mm3 / gas_prod_mm3, 2) if gas_prod_mm3 > 0 else "",
            "co2_kt": round(co2_t / 1000, 1),
            "boe_2024": round(boe, 0),
            "kg_co2_por_boe": round(co2_t * 1000 / boe, 3) if boe > 0 else "",
        })
    rows.sort(key=lambda r: r["co2_kt"], reverse=True)

    with OUT_OP.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    with OUT_FL.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["lat", "lon", "bcm", "mm3", "operador", "concesion"])
        w.writeheader(); w.writerows(flares)

    # --- resumen ---
    tot_bcm = sum(fl["bcm"] for fl in flares)
    tot_co2 = tot_bcm * 1e9 * KG_CO2_PER_M3 / 1e9          # Mt CO₂
    asg = sum(fl["bcm"] for fl in flares if fl["operador"] != "No asignado")
    print(f"\nAOI {YEAR}: {len(flares)} antorchas · {tot_bcm:.3f} BCM ({tot_bcm*1000:,.0f} Mm³) quemados "
          f"→ {tot_co2:.2f} Mt CO₂")
    print(f"Asignado a concesión: {100*asg/tot_bcm:.0f} % del volumen")
    print("Top operadores por CO₂ de flaring:")
    for r in rows[:8]:
        print(f"  {r['operador']:<30} {r['co2_kt']:>8,.0f} kt CO₂ · {r['gas_quemado_mm3']:>7,.0f} Mm³ "
              f"· {r['pct_gas_quemado'] or '—':>5}% gas · {r['kg_co2_por_boe'] or '—'} kgCO₂/BOE")
    print(f"OK → {OUT_OP.name}, {OUT_FL.name}")


if __name__ == "__main__":
    main()
