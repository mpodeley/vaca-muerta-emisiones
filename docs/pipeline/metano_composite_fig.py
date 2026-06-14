#!/usr/bin/env python3
"""Figura resumen del compuesto EMIT (lee `metano_emit_composite.json`, no re-descarga).

Muestra la media de realce de CH₄ apilada (~480 m) con la pluma del catálogo y los hotspots
persistentes marcados — para evidenciar que el realce persistente **calca el terreno** (artefactos)
y que la única pluma confirmada **no** aparece como hotspot (era episódica → se promedia a cero).

Uso:  python docs/pipeline/metano_composite_fig.py   (correr antes metano_emit_composite.py)
"""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MplPoly

ROOT = Path(__file__).resolve().parents[1]
COMP = ROOT / "data" / "metano_emit_composite.json"
PLUMES = ROOT / "data" / "metano_emit_plumas.geojson"
GEO = ROOT / "data" / "concesiones_neuquina.geojson"
OUT = ROOT / "assets" / "metano_emit_composite_resumen.png"


def main():
    d = json.loads(COMP.read_text())
    LON0, LON1, LAT0, LAT1 = d["lon0"], d["lon1"], d["lat0"], d["lat1"]
    cm = np.array([[np.nan if v is None else v for v in r] for r in d["coarse_mean"]], float)

    fig, ax = plt.subplots(figsize=(11, 9))
    im = ax.imshow(cm, extent=[LON0, LON1, LAT0, LAT1], origin="upper",
                   cmap="RdBu_r", vmin=-200, vmax=200)
    cb = fig.colorbar(im, ax=ax, shrink=0.85)
    cb.set_label("Media de realce de CH₄ EMIT, apilado 2022–2026 (ppm·m, ~480 m)")

    gj = json.loads(GEO.read_text(encoding="utf-8"))
    for ft in gj["features"]:
        g = ft["geometry"]
        rings = g["coordinates"] if g["type"] == "Polygon" else [c[0] for c in g["coordinates"]]
        for ring in rings:
            ax.add_patch(MplPoly(ring, closed=True, fill=False, edgecolor="#333",
                                 lw=0.3, alpha=0.45))

    # hotspots persistentes (sospechosos de artefacto de superficie)
    hs = d["hotspots_top"]
    ax.scatter([h["lon"] for h in hs], [h["lat"] for h in hs], s=90, facecolors="none",
               edgecolors="#ff7f0e", linewidths=1.6,
               label="Hotspots persistentes (mayormente artefactos de superficie)")
    # pluma del catálogo (NO aparece como hotspot)
    for ft in json.loads(PLUMES.read_text())["features"]:
        p = ft["properties"]
        ax.plot(p["lon"], p["lat"], marker="*", color="#39ff14", ms=20, mec="black", mew=0.7,
                label=f"Pluma catálogo EMIT #{p['plume_id']} ({p['fecha']}) — episódica, no persistente")

    ax.set_xlim(LON0, LON1); ax.set_ylim(LAT0, LAT1)
    ax.set_xlabel("Longitud"); ax.set_ylabel("Latitud")
    ax.set_title(f"Compuesto EMIT de metano (60 m, {d['escenas_ok']} escenas) — Vaca Muerta\n"
                 "El realce persistente calca el terreno (artefactos); la pluma real no persiste",
                 fontsize=12)
    ax.legend(loc="lower left", fontsize=8.5, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(OUT, dpi=130, facecolor="white")
    print(f"OK → {OUT.name}")


if __name__ == "__main__":
    main()
