#!/usr/bin/env python3
"""Visualización de la capa de metano (contexto).

`docs/assets/metano_mapa.html` — mapa interactivo con:
  · XCH₄ medio de TROPOMI 2019–2024 como overlay semitransparente (señal de cuenca, ~7 km),
  · las concesiones,
  · la(s) pluma(s) de metano de EMIT (polígono + marcador), atribuida(s) a operador.

Correr antes:  metano_tropomi.py  y  metano_emit.py

Uso:
    python docs/pipeline/metano_visuals.py
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
from matplotlib import cm, colors
import folium

ROOT = Path(__file__).resolve().parents[1]
GRID = ROOT / "data" / "metano_tropomi_grid.json"
PLUMES = ROOT / "data" / "metano_emit_plumas.geojson"
GEO = ROOT / "data" / "concesiones_neuquina.geojson"
OUT = ROOT / "assets" / "metano_mapa.html"

LON0, LON1, LAT0, LAT1 = -70.6, -68.2, -39.2, -37.3


def tropomi_overlay_png(grid):
    """Convierte la grilla XCH₄ en una imagen RGBA (inferno) para ImageOverlay."""
    arr = np.array([[np.nan if v is None else v for v in row] for row in grid["xch4"]], dtype=float)
    vmin, vmax = grid["vmin"], grid["vmax"]
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    rgba = cm.inferno(norm(arr))
    rgba[..., 3] = np.where(np.isnan(arr), 0.0, 0.6)  # transparente donde no hay dato
    return rgba


def main():
    grid = json.loads(GRID.read_text())
    m = folium.Map(location=[-38.3, -69.3], zoom_start=8, tiles="CartoDB positron")

    # --- TROPOMI overlay ---
    rgba = tropomi_overlay_png(grid)
    folium.raster_layers.ImageOverlay(
        image=rgba, bounds=[[LAT0, LON0], [LAT1, LON1]], opacity=1.0,
        name="XCH₄ medio TROPOMI 2019–2024", interactive=False, zindex=1,
    ).add_to(m)

    # --- concesiones ---
    gj = json.loads(GEO.read_text(encoding="utf-8"))
    folium.GeoJson(gj, name="Concesiones", style_function=lambda f: {
        "fillColor": "#000", "color": "#3a3a3a", "weight": 0.4, "fillOpacity": 0.0},
        tooltip=folium.GeoJsonTooltip(fields=["nombre", "operador"],
                                      aliases=["Concesión", "Operador"])).add_to(m)

    # --- plumas EMIT ---
    plumes = json.loads(PLUMES.read_text())
    for ft in plumes["features"]:
        p = ft["properties"]
        folium.GeoJson(ft, control=False, style_function=lambda f: {
            "fillColor": "#39ff14", "color": "#1f8f00", "weight": 1.5, "fillOpacity": 0.5}).add_to(m)
        folium.Marker(
            location=[p["lat"], p["lon"]],
            icon=folium.Icon(color="green", icon="cloud"),
            tooltip=(f"<b>Pluma EMIT {p['plume_id']}</b><br>{p['fecha']}<br>"
                     f"{p['concesion'] or '—'} · {p['operador']}"),
        ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)

    # leyenda / colorbar
    n = grid["n_images"]
    vmin, vmax = grid["vmin"], grid["vmax"]
    stops = "".join(
        f'<span style="flex:1;background:{colors.to_hex(cm.inferno(x))}"></span>'
        for x in np.linspace(0, 1, 24))
    legend = (
        f'<div style="position:fixed;bottom:18px;left:18px;z-index:9999;background:#fff;'
        f'color:#222;padding:9px 12px;border-radius:6px;font:12px system-ui;'
        f'box-shadow:0 1px 5px #0003;width:230px">'
        f'<b>XCH₄ medio TROPOMI 2019–2024</b><br>'
        f'<span style="color:#666">{n:,} imágenes Sentinel-5P · ~7 km</span>'
        f'<div style="display:flex;height:11px;margin:6px 0 2px;border-radius:2px;overflow:hidden">{stops}</div>'
        f'<div style="display:flex;justify-content:space-between"><span>{vmin:.0f} ppb</span>'
        f'<span>{vmax:.0f} ppb</span></div>'
        f'<div style="margin-top:6px">★ pluma de metano EMIT (puntual)</div>'
        f'<div style="color:#888;margin-top:3px;font-size:11px">Señal de cuenca, no por operador</div>'
        f'</div>')
    m.get_root().html.add_child(folium.Element(legend))
    m.save(str(OUT))
    print(f"OK → {OUT.name}  (TROPOMI {n:,} img · {len(plumes['features'])} pluma(s) EMIT)")


if __name__ == "__main__":
    main()
