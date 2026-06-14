#!/usr/bin/env python3
"""Compuesto propio de realce de metano EMIT (60 m) sobre Vaca Muerta.

El catálogo de plumas (`EMITL2BCH4PLM`) es **conservador**: solo lista plumas validadas (1 sobre el
AOI). Este script va al producto crudo de **realce de CH₄ por escena** (`EMITL2BCH4ENH`, 60 m) y
**apila las 421 escenas** que cubren el AOI (2022–2026) sobre una grilla común. La idea física: el
realce del *matched filter* tiene **ruido simétrico** (±cientos de ppm·m por píxel y escena) que **se
cancela al promediar** muchas pasadas, mientras que una **fuente persistente** (o un artefacto de
superficie persistente) queda con media positiva. Así se buscan emisiones **por debajo del umbral** del
catálogo.

Salidas:
    docs/data/metano_emit_composite.json   (grilla media coarse + hotspots atribuidos + metadatos)
    docs/assets/metano_emit_composite.png   (media / máximo / persistencia)

Requiere ~/.netrc con credenciales de Earthdata. Uso:
    python docs/pipeline/metano_emit_composite.py
"""
from pathlib import Path
import json
import os
import netrc
import tempfile
import time
import requests
import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling
from rasterio.transform import from_origin
from shapely.geometry import shape, Point

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "concesiones_neuquina.geojson"
OUT_JSON = ROOT / "data" / "metano_emit_composite.json"
OUT_PNG = ROOT / "assets" / "metano_emit_composite.png"

LON0, LON1, LAT0, LAT1 = -70.6, -68.2, -39.2, -37.3
RES = 0.000542                 # ~60 m, resolución nativa de las escenas EMIT L2B
HI_THRESH = 1000.0             # ppm·m: realce "alto" por píxel/escena (muy por encima del ruido p99~850)
MIN_SAMPLES = 8                # mínimo de escenas válidas por píxel para confiar en la media
CMR = "https://cmr.earthdata.nasa.gov/search/granules.umm_json"


def edl_token():
    auth = netrc.netrc()
    host = next(h for h in auth.hosts if "earthdata" in h)
    user, _, pw = auth.authenticators(host)
    s = requests.Session()
    r = s.get("https://urs.earthdata.nasa.gov/api/users/tokens", auth=(user, pw), timeout=60)
    toks = r.json() if r.ok else []
    if not toks:
        r = s.post("https://urs.earthdata.nasa.gov/api/users/token", auth=(user, pw), timeout=60)
        toks = [r.json()]
    return toks[0]["access_token"]


def scene_urls():
    bbox = f"{LON0},{LAT0},{LON1},{LAT1}"
    urls, page = [], 1
    while True:
        r = requests.get(CMR, params={"short_name": "EMITL2BCH4ENH", "bounding_box": bbox,
                                       "page_size": 200, "page_num": page}, timeout=120)
        r.raise_for_status()
        batch = r.json().get("items", [])
        for it in batch:
            u = [l["URL"] for l in it["umm"]["RelatedUrls"]
                 if l.get("Type") == "GET DATA" and l["URL"].endswith(".tif")]
            if u:
                urls.append(u[0])
        if len(batch) < 200:
            break
        page += 1
    return urls


def main():
    tok = edl_token()
    hdr = {"Authorization": f"Bearer {tok}"}
    urls = scene_urls()
    lim = int(os.environ.get("EMIT_LIMIT", "0"))
    if lim:
        urls = urls[:lim]
    print(f"{len(urls)} escenas CH4ENH a apilar", flush=True)

    nx = int(round((LON1 - LON0) / RES))
    ny = int(round((LAT1 - LAT0) / RES))
    target_t = from_origin(LON0, LAT1, RES, RES)
    ssum = np.zeros((ny, nx), np.float32)
    cnt = np.zeros((ny, nx), np.uint16)
    vmax = np.full((ny, nx), -1e30, np.float32)
    hi = np.zeros((ny, nx), np.uint16)

    ok = 0
    for i, url in enumerate(urls, 1):
        tmp = None
        try:
            with requests.get(url, headers=hdr, stream=True, timeout=300) as r:
                r.raise_for_status()
                fd, tmp = tempfile.mkstemp(suffix=".tif")
                with os.fdopen(fd, "wb") as f:
                    for c in r.iter_content(1 << 20):
                        f.write(c)
            with rasterio.open(tmp) as ds:
                wb, eb = max(LON0, ds.bounds.left), min(LON1, ds.bounds.right)
                sb, nb = max(LAT0, ds.bounds.bottom), min(LAT1, ds.bounds.top)
                if wb >= eb or sb >= nb:
                    continue
                c0, c1 = int(round((wb - LON0) / RES)), int(round((eb - LON0) / RES))
                r0, r1 = int(round((LAT1 - nb) / RES)), int(round((LAT1 - sb) / RES))
                if c1 <= c0 or r1 <= r0:
                    continue
                sub_t = from_origin(LON0 + c0 * RES, LAT1 - r0 * RES, RES, RES)
                dst = np.full((r1 - r0, c1 - c0), -9999.0, np.float32)
                reproject(source=rasterio.band(ds, 1), destination=dst,
                          src_transform=ds.transform, src_crs=ds.crs,
                          dst_transform=sub_t, dst_crs="EPSG:4326",
                          src_nodata=ds.nodata, dst_nodata=-9999.0,
                          resampling=Resampling.nearest)
            valid = np.isfinite(dst) & (dst != -9999.0)
            sl = (slice(r0, r1), slice(c0, c1))
            ssum[sl][valid] += dst[valid]
            cnt[sl][valid] += 1
            sub = vmax[sl]
            np.maximum(sub, np.where(valid, dst, -1e30), out=sub)
            hi[sl][valid & (dst > HI_THRESH)] += 1
            ok += 1
        except Exception as e:
            print(f"  ! escena {i} falló: {str(e)[:80]}", flush=True)
        finally:
            if tmp and os.path.exists(tmp):
                os.remove(tmp)
        if i % 25 == 0:
            print(f"  {i}/{len(urls)} ({ok} ok) · cobertura máx {int(cnt.max())} escenas/píxel", flush=True)

    mean = np.where(cnt > 0, ssum / np.maximum(cnt, 1), np.nan)
    mean_conf = np.where(cnt >= MIN_SAMPLES, mean, np.nan)   # media solo donde hay muestras suficientes
    vmax = np.where(cnt > 0, vmax, np.nan)

    # --- hotspots: píxeles con media persistente alta y muchas muestras ---
    polys = [(shape(ft["geometry"]), (ft["properties"].get("operador") or "").strip(),
              ft["properties"].get("nombre", ""))
             for ft in json.loads(GEO.read_text(encoding="utf-8"))["features"]]
    thr = float(np.nanpercentile(mean_conf, 99.9))
    ys, xs = np.where(np.nan_to_num(mean_conf, nan=-1e30) > thr)
    hotspots = []
    for y, x in zip(ys, xs):
        lon, lat = LON0 + (x + 0.5) * RES, LAT1 - (y + 0.5) * RES
        op, conc = "No asignado", ""
        pt = Point(lon, lat)
        for geom, operador, nombre in polys:
            if geom.contains(pt):
                op, conc = operador or "No asignado", nombre
                break
        hotspots.append({"lon": round(lon, 5), "lat": round(lat, 5),
                         "mean_ppm_m": round(float(mean_conf[y, x]), 1),
                         "n_escenas": int(cnt[y, x]), "n_alto": int(hi[y, x]),
                         "operador": op, "concesion": conc})
    hotspots.sort(key=lambda h: h["mean_ppm_m"], reverse=True)

    # --- guardar grilla coarse (factor 8 ~480 m) para overlay/reproducibilidad ---
    f = 8
    cy, cx = (ny // f) * f, (nx // f) * f
    coarse = np.nanmean(mean_conf[:cy, :cx].reshape(cy // f, f, cx // f, f), axis=(1, 3))
    json_out = {
        "res_deg": RES, "hi_thresh_ppm_m": HI_THRESH, "min_samples": MIN_SAMPLES,
        "escenas_total": len(urls), "escenas_ok": ok,
        "cobertura_max_px": int(cnt.max()), "cobertura_media_px": round(float(cnt[cnt > 0].mean()), 1),
        "lon0": LON0, "lon1": LON1, "lat0": LAT0, "lat1": LAT1, "coarse_factor": f,
        "coarse_mean": [[None if not np.isfinite(v) else round(float(v), 1) for v in row]
                        for row in coarse],
        "hotspots_top": hotspots[:25],
    }
    OUT_JSON.write_text(json.dumps(json_out, ensure_ascii=False), encoding="utf-8")

    # --- PNG de 3 paneles ---
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Polygon as MplPoly
    gj = json.loads(GEO.read_text(encoding="utf-8"))

    def draw_conc(ax):
        for ft in gj["features"]:
            g = ft["geometry"]
            rings = g["coordinates"] if g["type"] == "Polygon" else [c[0] for c in g["coordinates"]]
            for ring in rings:
                ax.add_patch(MplPoly(ring, closed=True, fill=False, edgecolor="#5fd0ff",
                                     lw=0.3, alpha=0.5))
        ax.set_xlim(LON0, LON1); ax.set_ylim(LAT0, LAT1)

    ext = [LON0, LON1, LAT0, LAT1]
    fig, axs = plt.subplots(1, 3, figsize=(20, 7))
    im0 = axs[0].imshow(mean_conf, extent=ext, origin="upper", cmap="RdBu_r",
                        vmin=-300, vmax=300)
    axs[0].set_title(f"Media de realce CH₄ (ppm·m)\n≥{MIN_SAMPLES} escenas/píxel · ruido cancelado")
    fig.colorbar(im0, ax=axs[0], shrink=0.8)
    im1 = axs[1].imshow(vmax, extent=ext, origin="upper", cmap="inferno", vmin=0, vmax=2500)
    axs[1].set_title("Máximo de realce CH₄ por píxel (ppm·m)\nrealce puntual más fuerte visto")
    fig.colorbar(im1, ax=axs[1], shrink=0.8)
    im2 = axs[2].imshow(hi, extent=ext, origin="upper", cmap="viridis", vmin=0,
                        vmax=max(3, int(np.percentile(hi, 99.99))))
    axs[2].set_title(f"Persistencia: nº de escenas con realce > {HI_THRESH:.0f} ppm·m")
    fig.colorbar(im2, ax=axs[2], shrink=0.8)
    for ax in axs:
        draw_conc(ax)
        for h in hotspots[:5]:
            ax.plot(h["lon"], h["lat"], "o", mfc="none", mec="#39ff14", mew=1.4, ms=12)
        ax.set_xlabel("Longitud")
    axs[0].set_ylabel("Latitud")
    fig.suptitle(f"Compuesto EMIT de realce de metano (60 m) — Vaca Muerta · {ok} escenas 2022–2026",
                 fontsize=14)
    fig.tight_layout()
    fig.savefig(OUT_PNG, dpi=120, facecolor="white")
    print(f"\nApiladas {ok}/{len(urls)} escenas · cobertura máx {int(cnt.max())}/píxel", flush=True)
    print(f"Hotspots (media > {thr:.0f} ppm·m, ≥{MIN_SAMPLES} escenas):", flush=True)
    for h in hotspots[:8]:
        print(f"  ({h['lat']},{h['lon']})  media {h['mean_ppm_m']:>6} ppm·m · {h['n_escenas']} esc "
              f"· {h['n_alto']} altas → {h['concesion'] or '—'} / {h['operador']}", flush=True)
    print(f"OK → {OUT_JSON.name}, {OUT_PNG.name}", flush=True)


if __name__ == "__main__":
    main()
