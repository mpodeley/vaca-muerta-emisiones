#!/usr/bin/env python3
"""Visualizaciones de flaring (Fase 2).

- `docs/assets/flaring_mapa.html` — antorchas VIIRS en el AOI, tamaño ∝ volumen quemado, color por
  operador, sobre las concesiones.
- `docs/assets/flaring_intensidad.png` — intensidad de flaring por operador (kg CO₂/BOE) y % de su gas
  que se quema.

Uso:
    python docs/pipeline/flaring_visuals.py   (correr antes flaring_operador.py)
"""
from pathlib import Path
import json
import csv
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import folium

ROOT = Path(__file__).resolve().parents[1]
FLARES = ROOT / "data" / "flares_aoi.csv"
OPS = ROOT / "data" / "flaring_por_operador.csv"
GEO = ROOT / "data" / "concesiones_neuquina.geojson"
MAP = ROOT / "assets" / "flaring_mapa.html"
PNG = ROOT / "assets" / "flaring_intensidad.png"

PALETTE = ["#e63946", "#f4a261", "#2a9d8f", "#3a86ff", "#8338ec", "#06d6a0", "#ffd166"]
GREY = "#8a93a3"


def load_csv(p):
    return list(csv.DictReader(p.open(encoding="utf-8")))


def flare_map():
    flares = load_csv(FLARES)
    ops = load_csv(OPS)
    # color por operador: los de mayor CO₂ con color, el resto gris
    top = [r["operador"] for r in ops if r["operador"] != "No asignado"][:6]
    color_of = {op: PALETTE[i] for i, op in enumerate(top)}

    m = folium.Map(location=[-38.3, -69.1], zoom_start=8, tiles="CartoDB dark_matter")
    gj = json.loads(GEO.read_text(encoding="utf-8"))
    folium.GeoJson(gj, style_function=lambda f: {"fillColor": "#222", "color": "#555",
                   "weight": 0.4, "fillOpacity": 0.15}, control=False).add_to(m)

    for fl in flares:
        mm3 = float(fl["mm3"])
        op = fl["operador"]
        color = color_of.get(op, GREY)
        folium.CircleMarker(
            location=[float(fl["lat"]), float(fl["lon"])],
            radius=max(2.5, 2.5 + 1.7 * math.sqrt(mm3)),
            color=color, weight=0.8, fill=True, fillColor=color, fillOpacity=0.75,
            tooltip=(f"<b>{op}</b><br>{fl['concesion'] or '—'}<br>"
                     f"{mm3:,.1f} Mm³/año quemados<br>≈ {mm3*2.0/1000:,.0f} kt CO₂"),
        ).add_to(m)

    items = "".join(f'<div><span style="background:{color_of[op]};width:11px;height:11px;'
                    f'display:inline-block;border-radius:50%;margin-right:6px"></span>'
                    f'{op.replace(" S.A.","").replace(" SAU","").replace(" SL","")}</div>' for op in top)
    items += (f'<div><span style="background:{GREY};width:11px;height:11px;display:inline-block;'
              f'border-radius:50%;margin-right:6px"></span>Otros / sin concesión</div>')
    legend = (f'<div style="position:fixed;bottom:18px;left:18px;z-index:9999;background:#11151c;'
              f'color:#e8e8e8;padding:8px 11px;border-radius:6px;font:12px system-ui;'
              f'box-shadow:0 1px 4px #0006"><b>Antorchas 2024 (tamaño ∝ volumen)</b>{items}</div>')
    m.get_root().html.add_child(folium.Element(legend))
    m.save(str(MAP))
    print(f"OK → {MAP.name} ({len(flares)} antorchas)")


def intensity_png():
    ops = [r for r in load_csv(OPS) if r["operador"] != "No asignado" and r["kg_co2_por_boe"]]
    for r in ops:
        r["kg_co2_por_boe"] = float(r["kg_co2_por_boe"])
        r["pct_gas_quemado"] = float(r["pct_gas_quemado"]) if r["pct_gas_quemado"] else 0
        r["co2_kt"] = float(r["co2_kt"])
    ops = [r for r in ops if r["co2_kt"] >= 5]          # operadores con flaring relevante
    ops.sort(key=lambda r: r["kg_co2_por_boe"])
    names = [r["operador"].replace(" S.A.", "").replace(" SAU", "").replace(" SL", "")
             .replace(" S.R.L.", "") for r in ops]
    vals = [r["kg_co2_por_boe"] for r in ops]
    colors = ["#e63946" if r["pct_gas_quemado"] >= 10 else "#f4a261" if r["pct_gas_quemado"] >= 3
              else "#2a9d8f" for r in ops]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(names, vals, color=colors)
    for i, r in enumerate(ops):
        ax.text(vals[i], i, f"  {vals[i]:.1f}  ({r['pct_gas_quemado']:.0f}% de su gas)",
                va="center", fontsize=8.5)
    ax.set_xlabel("Intensidad de flaring (kg CO₂ por BOE producido, 2024)")
    ax.set_title("Huella de CO₂ por flaring, por operador — Vaca Muerta 2024\n"
                 "Rojo: quema ≥10 % de su gas · naranja: 3–10 % · verde: <3 %")
    ax.margins(x=0.22)
    fig.tight_layout()
    fig.savefig(PNG, dpi=130, facecolor="white")
    print(f"OK → {PNG.name}")


def main():
    flare_map()
    intensity_png()


if __name__ == "__main__":
    main()
