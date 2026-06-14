#!/usr/bin/env python3
"""Capa de metano (contexto) — Plumas EMIT sobre Vaca Muerta.

Consulta el catálogo público de **plumas de metano de NASA EMIT** (producto L2B
``EMITL2BCH4PLM``) vía el **CMR de Earthdata** (API REST abierta, sin login) filtrando por el
bbox del AOI. Para cada pluma toma su **polígono** (de la metadata del granule), la atribuye a
una **concesión → operador** (point-in-polygon sobre ``concesiones_neuquina.geojson``) y guarda
un GeoJSON + un CSV resumen.

Framing honesto: EMIT no es un satélite de monitoreo continuo; observa de forma **oportunista**.
La cantidad de plumas catalogadas sobre el AOI es chica → es una capa de **contexto puntual**,
no un inventario por operador. Ausencia de plumas ≠ ausencia de emisiones.

Salidas:
    docs/data/metano_emit_plumas.geojson
    docs/data/metano_emit_plumas.csv

Uso:
    python docs/pipeline/metano_emit.py
"""
from pathlib import Path
import json
import csv
import requests
from shapely.geometry import shape, Polygon

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "concesiones_neuquina.geojson"
OUT_GJ = ROOT / "data" / "metano_emit_plumas.geojson"
OUT_CSV = ROOT / "data" / "metano_emit_plumas.csv"

# AOI Vaca Muerta (igual que el resto del sitio)
LON0, LON1, LAT0, LAT1 = -70.6, -68.2, -39.2, -37.3

CMR = "https://cmr.earthdata.nasa.gov/search/granules.umm_json"
SHORT_NAME = "EMITL2BCH4PLM"  # EMIT L2B Estimated Methane Plume Complexes (catálogo curado de plumas)
ENH_NAME = "EMITL2BCH4ENH"    # EMIT L2B Methane Enhancement (realce de CH₄ por escena → cobertura real)
OUT_COV = ROOT / "data" / "metano_emit_cobertura.json"


def fetch_all(short_name):
    """Devuelve todos los granules (UMM) de una colección que intersectan el AOI (paginado)."""
    bbox = f"{LON0},{LAT0},{LON1},{LAT1}"  # CMR: W,S,E,N
    items, page = [], 1
    while True:
        r = requests.get(CMR, params={"short_name": short_name, "bounding_box": bbox,
                                       "page_size": 200, "page_num": page}, timeout=120)
        r.raise_for_status()
        batch = r.json().get("items", [])
        items += batch
        if len(batch) < 200:
            break
        page += 1
    return items


def granule_date(umm):
    t = umm.get("TemporalExtent", {})
    return (t.get("SingleDateTime") or t.get("RangeDateTime", {}).get("BeginningDateTime", ""))[:10]


def coverage():
    """Cobertura REAL de EMIT sobre el AOI: escenas con producto de metano (CH4ENH) y fechas únicas.
    Esto contextualiza el catálogo de plumas: muchas observaciones → pocas plumas = pocas fuentes
    puntuales grandes, no falta de cobertura."""
    scenes = fetch_all(ENH_NAME)
    dates = sorted({granule_date(s["umm"]) for s in scenes if granule_date(s["umm"])})
    cov = {"escenas": len(scenes), "fechas_unicas": len(dates),
           "desde": dates[0] if dates else "", "hasta": dates[-1] if dates else "",
           "por_anio": {}}
    for d in dates:
        cov["por_anio"][d[:4]] = cov["por_anio"].get(d[:4], 0) + 1
    OUT_COV.write_text(json.dumps(cov, ensure_ascii=False, indent=0), encoding="utf-8")
    return cov


def plume_polygon(umm):
    geom = umm["SpatialExtent"]["HorizontalSpatialDomain"]["Geometry"]
    pts = geom["GPolygons"][0]["Boundary"]["Points"]
    return Polygon([(p["Longitude"], p["Latitude"]) for p in pts])


def attr(name):
    return name


def main():
    polys = [(shape(ft["geometry"]), (ft["properties"].get("operador") or "").strip(),
              ft["properties"].get("nombre", ""))
             for ft in json.loads(GEO.read_text(encoding="utf-8"))["features"]]

    items = fetch_all(SHORT_NAME)
    feats, rows = [], []
    for it in items:
        umm = it["umm"]
        poly = plume_polygon(umm)
        c = poly.centroid
        date = (umm.get("TemporalExtent", {}).get("SingleDateTime")
                or umm.get("TemporalExtent", {}).get("RangeDateTime", {}).get("BeginningDateTime", ""))
        attrs = {a["Name"]: a.get("Values", [None])[0] for a in umm.get("AdditionalAttributes", [])}
        op, conc = "No asignado", ""
        for geom, operador, nombre in polys:
            if geom.contains(c) or geom.intersects(poly):
                op, conc = operador or "No asignado", nombre
                break
        props = {
            "plume_id": attrs.get("PLUME_ID", ""),
            "granule": umm.get("GranuleUR", ""),
            "fecha": (date or "")[:10],
            "lon": round(c.x, 5), "lat": round(c.y, 5),
            "operador": op, "concesion": conc,
        }
        feats.append({"type": "Feature", "geometry": json.loads(json.dumps(poly.__geo_interface__)),
                      "properties": props})
        rows.append(props)

    rows.sort(key=lambda r: r["fecha"])
    OUT_GJ.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False),
                      encoding="utf-8")
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else
                           ["plume_id", "granule", "fecha", "lon", "lat", "operador", "concesion"])
        w.writeheader()
        w.writerows(rows)

    cov = coverage()
    print(f"EMIT cobertura sobre AOI: {cov['escenas']} escenas CH4ENH · {cov['fechas_unicas']} fechas "
          f"únicas ({cov['desde']} → {cov['hasta']})  por año: {cov['por_anio']}")
    print(f"EMIT plumas catalogadas (CH4PLM): {len(rows)}")
    for r in rows:
        print(f"  · pluma {r['plume_id']:>5}  {r['fecha']}  ({r['lat']},{r['lon']})  "
              f"→ {r['concesion'] or '—'} / {r['operador']}")
    print(f"OK → {OUT_GJ.name}, {OUT_CSV.name}, {OUT_COV.name}")


if __name__ == "__main__":
    main()
