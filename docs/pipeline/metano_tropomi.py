#!/usr/bin/env python3
"""Capa de metano (contexto) — XCH₄ medio de TROPOMI sobre Vaca Muerta.

Promedia el producto **Sentinel-5P / TROPOMI L3 CH₄** (``COPERNICUS/S5P/OFFL/L3_CH4``, banda
``CH4_column_volume_mixing_ratio_dry_air``, en ppb) sobre el AOI de Vaca Muerta para un rango
multi-año vía **Google Earth Engine**, lo baja a una grilla y lo guarda como matriz + PNG.

Framing honesto: TROPOMI tiene resolución de ~7 km → es una señal **de cuenca**, no por operador.
Sirve para mostrar que Vaca Muerta aparece como **hotspot** de metano, en línea con Hancock et al.
2025 (intensidad de metano de Argentina ~5,9 %, atribuida a la expansión de Neuquén).

Requiere autenticación GEE una vez:  earthengine authenticate
Proyecto: pasar por --project o env EE_PROJECT.

Salidas:
    docs/data/metano_tropomi_grid.json   (lats, lons, xch4 ppb, metadatos)
    docs/assets/metano_tropomi.png

Uso:
    python docs/pipeline/metano_tropomi.py --project ee-tuusuario
"""
from pathlib import Path
import argparse
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly
import ee

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "concesiones_neuquina.geojson"
PLUMES = ROOT / "data" / "metano_emit_plumas.geojson"
OUT_GRID = ROOT / "data" / "metano_tropomi_grid.json"
OUT_PNG = ROOT / "assets" / "metano_tropomi.png"

LON0, LON1, LAT0, LAT1 = -70.6, -68.2, -39.2, -37.3
BAND = "CH4_column_volume_mixing_ratio_dry_air"
DATE0, DATE1 = "2019-01-01", "2025-01-01"
YR0, YR1 = "2019", "2024"  # rango de años completos cubierto (DATE1 es exclusivo)
SCALE_DEG = 0.05  # ~5 km de grilla para muestrear (TROPOMI nativo ~7 km)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default=os.environ.get("EE_PROJECT"))
    args = ap.parse_args()
    ee.Initialize(project=args.project)

    aoi = ee.Geometry.Rectangle([LON0, LAT0, LON1, LAT1])
    col = (ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_CH4")
           .select(BAND).filterDate(DATE0, DATE1).filterBounds(aoi))
    n = col.size().getInfo()
    mean = col.mean().reproject(crs="EPSG:4326", scale=int(SCALE_DEG * 111320)).clip(aoi)

    rect = mean.sampleRectangle(region=aoi, defaultValue=-9999, properties=[])
    arr = np.array(rect.get(BAND).getInfo(), dtype=float)
    arr[arr <= 0] = np.nan
    ny, nx = arr.shape
    lons = np.linspace(LON0, LON1, nx)
    lats = np.linspace(LAT1, LAT0, ny)  # sampleRectangle: fila 0 = norte

    OUT_GRID.write_text(json.dumps({
        "band": BAND, "unit": "ppb", "date0": DATE0, "date1": DATE1, "n_images": n,
        "lon0": LON0, "lon1": LON1, "lat0": LAT0, "lat1": LAT1,
        "lats": [round(v, 4) for v in lats], "lons": [round(v, 4) for v in lons],
        "xch4": [[None if np.isnan(v) else round(float(v), 1) for v in row] for row in arr],
        "vmin": round(float(np.nanmin(arr)), 1), "vmax": round(float(np.nanmax(arr)), 1),
        "vmean": round(float(np.nanmean(arr)), 1),
    }, ensure_ascii=False), encoding="utf-8")

    # --- PNG ---
    fig, ax = plt.subplots(figsize=(9, 7))
    im = ax.imshow(arr, extent=[LON0, LON1, LAT0, LAT1], origin="upper",
                   cmap="inferno", aspect="auto")
    cb = fig.colorbar(im, ax=ax, shrink=0.85)
    cb.set_label(f"XCH₄ medio TROPOMI {YR0}–{YR1} (ppb)")

    gj = json.loads(GEO.read_text(encoding="utf-8"))
    for ft in gj["features"]:
        g = ft["geometry"]
        rings = g["coordinates"] if g["type"] == "Polygon" else [c[0] for c in g["coordinates"]]
        for ring in rings:
            ax.add_patch(MplPoly(ring, closed=True, fill=False, edgecolor="#5fd0ff",
                                 lw=0.4, alpha=0.5))
    if PLUMES.exists():
        for ft in json.loads(PLUMES.read_text())["features"]:
            p = ft["properties"]
            ax.plot(p["lon"], p["lat"], marker="*", color="#39ff14", ms=16,
                    markeredgecolor="black", mew=0.6,
                    label=f"Pluma EMIT {p['fecha']} ({p['operador'].replace(' S.A.','')})")
        ax.legend(loc="lower left", fontsize=8, framealpha=0.85)

    ax.set_xlim(LON0, LON1); ax.set_ylim(LAT0, LAT1)
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
    ax.set_title(f"Metano de cuenca — XCH₄ medio TROPOMI sobre Vaca Muerta\n"
                 f"{n} imágenes {YR0}–{YR1} · resolución ~7 km (señal de cuenca, no por operador)")
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=130, facecolor="white")
    print(f"TROPOMI L3 CH₄: {n} imágenes · XCH₄ {YR0}–{YR1} "
          f"min/mean/max = {np.nanmin(arr):.0f}/{np.nanmean(arr):.0f}/{np.nanmax(arr):.0f} ppb")
    print(f"OK → {OUT_GRID.name}, {OUT_PNG.name}")


if __name__ == "__main__":
    main()
