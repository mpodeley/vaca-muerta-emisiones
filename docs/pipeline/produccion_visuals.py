#!/usr/bin/env python3
"""Visualizaciones de producción por operador (Fase 1).

Genera:
- `docs/assets/ranking_operadores.png` — barras de los principales operadores por BOE (2025).
- `docs/assets/mapa_operadores.html` — coroplético Folium de las concesiones de la cuenca Neuquina
  coloreadas por operador (los principales en color, el resto en gris), con la producción 2025 en el
  tooltip. Es la base geográfica para, en la Fase 2, superponer emisiones y calcular intensidad.

Uso:
    python docs/pipeline/produccion_visuals.py
"""
from pathlib import Path
import json
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import folium

ROOT = Path(__file__).resolve().parents[1]
PROD = ROOT / "data" / "produccion_por_operador.csv"
GEO = ROOT / "data" / "concesiones_neuquina.geojson"
PNG = ROOT / "assets" / "ranking_operadores.png"
MAP = ROOT / "assets" / "mapa_operadores.html"

N_TOP = 8
PALETTE = ["#e63946", "#f4a261", "#2a9d8f", "#264653", "#e9c46a",
           "#8338ec", "#3a86ff", "#06d6a0"]
GREY = "#9aa3b2"


def load_prod():
    rows = list(csv.DictReader(PROD.open(encoding="utf-8")))
    for r in rows:
        r["boe"] = float(r["boe"]); r["share_boe_pct"] = float(r["share_boe_pct"])
    rows.sort(key=lambda r: r["boe"], reverse=True)
    return rows


def ranking_png(prod):
    top = prod[:12][::-1]
    names = [r["operador"].replace(" S.A.", "").replace(" SAU", "").replace(" SL", "") for r in top]
    vals = [r["boe"] / 1e6 for r in top]
    colors = [PALETTE[(len(prod[:12]) - 1 - i) % len(PALETTE)] for i in range(len(top))]
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(names, vals, color=colors)
    ax.set_xlabel("Producción 2025 (millones de BOE)")
    ax.set_title("Producción por operador — cuenca Neuquina, 2025\n(el denominador de la huella de emisión)")
    for i, v in enumerate(vals):
        ax.text(v, i, f" {v:,.0f}", va="center", fontsize=9)
    ax.margins(x=0.12)
    fig.tight_layout()
    PNG.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(PNG, dpi=130, facecolor="white")
    print(f"OK → {PNG.name}")


def operador_map(prod):
    share = {r["operador"]: r for r in prod}
    top_ops = [r["operador"] for r in prod[:N_TOP]]
    color_of = {op: PALETTE[i] for i, op in enumerate(top_ops)}

    gj = json.loads(GEO.read_text(encoding="utf-8"))
    matched = 0
    for ft in gj["features"]:
        op = (ft["properties"].get("operador") or "").strip()
        info = share.get(op)
        if op in color_of:
            matched += 1
        ft["properties"]["color"] = color_of.get(op, GREY)
        ft["properties"]["boe_2025"] = (f"{info['boe']/1e6:,.1f} M BOE ({info['share_boe_pct']:.1f} %)"
                                        if info else "sin producción 2025")

    m = folium.Map(location=[-38.4, -69.2], zoom_start=8, tiles="CartoDB positron")
    folium.GeoJson(
        gj, name="Concesiones por operador",
        style_function=lambda f: {"fillColor": f["properties"]["color"], "color": "#555",
                                  "weight": 0.6, "fillOpacity": 0.6},
        highlight_function=lambda f: {"weight": 2, "fillOpacity": 0.85},
        tooltip=folium.GeoJsonTooltip(
            fields=["nombre", "operador", "boe_2025"],
            aliases=["Concesión", "Operador", "Producción 2025"], sticky=True),
    ).add_to(m)

    # Leyenda
    items = "".join(
        f'<div><span style="background:{color_of[op]};width:11px;height:11px;'
        f'display:inline-block;margin-right:6px;border-radius:2px"></span>'
        f'{op.replace(" S.A.", "").replace(" SAU", "").replace(" SL", "")} '
        f'({share[op]["share_boe_pct"]:.0f} %)</div>' for op in top_ops)
    items += (f'<div><span style="background:{GREY};width:11px;height:11px;display:inline-block;'
              f'margin-right:6px;border-radius:2px"></span>Otros</div>')
    legend = (f'<div style="position:fixed;bottom:18px;left:18px;z-index:9999;background:white;'
              f'padding:8px 11px;border-radius:6px;font:12px system-ui;box-shadow:0 1px 4px #0003">'
              f'<b>Operador (% BOE 2025)</b>{items}</div>')
    m.get_root().html.add_child(folium.Element(legend))
    m.save(str(MAP))
    print(f"OK → {MAP.name} ({matched} concesiones de los top {N_TOP} operadores coloreadas)")


def main():
    prod = load_prod()
    ranking_png(prod)
    operador_map(prod)


if __name__ == "__main__":
    main()
