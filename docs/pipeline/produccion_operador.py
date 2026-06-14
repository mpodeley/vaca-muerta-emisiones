#!/usr/bin/env python3
"""Producción por operador en la cuenca Neuquina — el DENOMINADOR de la intensidad de emisión.

Agrega `docs/data/produccion_neuquina.csv` (producción mensual por área × empresa, de la Secretaría
de Energía argentina vía el proyecto estado-del-sistema) por **operador** para un año completo, y
convierte a **BOE** (barriles equivalentes de petróleo) con un factor documentado.

Salida: `docs/data/produccion_por_operador.csv`.

Uso:
    python docs/pipeline/produccion_operador.py
"""
from pathlib import Path
from collections import defaultdict
import csv

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "produccion_neuquina.csv"
OUT = ROOT / "data" / "produccion_por_operador.csv"

YEAR = "2025"                 # último año calendario completo del dataset

# Factores de conversión a BOE (documentados en metodologia.md):
BBL_PER_M3_OIL = 6.2898      # 1 m³ de petróleo = 6,2898 barriles
M3_GAS_PER_BOE = 169.9       # 1 BOE ≈ 6.000 pies³ de gas ≈ 169,9 m³ (regla 6:1 volumétrica)


def main():
    rows = list(csv.DictReader(SRC.open(encoding="utf-8-sig")))
    rows = [r for r in rows if r["mes"].startswith(YEAR)]
    meses = sorted({r["mes"] for r in rows})

    gas_mm3 = defaultdict(float)     # millones de m³
    pet_m3 = defaultdict(float)      # m³
    pozos_mes = defaultdict(lambda: defaultdict(float))  # operador -> mes -> pozos_activos

    for r in rows:
        op = r["empresa"].strip()
        gas_mm3[op] += float(r["prod_gas_mm3"] or 0)
        pet_m3[op] += float(r["prod_pet_m3"] or 0)
        pozos_mes[op][r["mes"]] += float(r["pozos_activos"] or 0)

    out = []
    for op in gas_mm3:
        oil_bbl = pet_m3[op] * BBL_PER_M3_OIL
        gas_boe = (gas_mm3[op] * 1e6) / M3_GAS_PER_BOE
        boe = oil_bbl + gas_boe
        pozos = pozos_mes[op]
        pozos_prom = sum(pozos.values()) / len(pozos) if pozos else 0
        out.append({
            "operador": op,
            "gas_mm3": round(gas_mm3[op], 1),
            "petroleo_m3": round(pet_m3[op], 1),
            "petroleo_bbl": round(oil_bbl, 0),
            "gas_boe": round(gas_boe, 0),
            "oil_boe": round(oil_bbl, 0),
            "boe": round(boe, 0),
            "pozos_activos_prom": round(pozos_prom, 0),
        })

    total_boe = sum(r["boe"] for r in out)
    for r in out:
        r["share_boe_pct"] = round(100 * r["boe"] / total_boe, 2) if total_boe else 0
    out.sort(key=lambda r: r["boe"], reverse=True)

    fields = ["operador", "gas_mm3", "petroleo_m3", "petroleo_bbl",
              "gas_boe", "oil_boe", "boe", "share_boe_pct", "pozos_activos_prom"]
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out)

    # Resumen / sanity-check
    tot_gas = sum(r["gas_mm3"] for r in out)
    tot_oil = sum(r["petroleo_m3"] for r in out)
    print(f"Ventana: {YEAR} ({len(meses)} meses) · {len(out)} operadores")
    print(f"Total cuenca {YEAR}: gas {tot_gas:,.0f} Mm³ (~{tot_gas/365:,.0f} Mm³/d) · "
          f"petróleo {tot_oil:,.0f} m³ (~{tot_oil*BBL_PER_M3_OIL/365:,.0f} bbl/d) · "
          f"{total_boe:,.0f} BOE")
    print("Top 8 por BOE:")
    for r in out[:8]:
        print(f"  {r['operador']:<28} {r['boe']:>14,.0f} BOE  ({r['share_boe_pct']:>5.1f} %)")
    print(f"OK → {OUT}")


if __name__ == "__main__":
    main()
