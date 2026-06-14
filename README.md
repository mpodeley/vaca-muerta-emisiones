# Emisiones de CO₂ y metano en Vaca Muerta

Experimento: estimar la **huella de emisión por operador y por barril/m³ producido** en Vaca Muerta,
cruzando **datos satelitales públicos** con la **producción por concesión**.

🌐 **Sitio:** https://mpodeley.github.io/vaca-muerta-emisiones/

**Fase 1 (esta entrega):** la pregunta, los antecedentes y datasets verificados, la metodología, y el
**denominador real** — producción por operador (cuenca Neuquina, 2025). Las corridas satelitales
(flaring VIIRS, inversión TROPOMI de metano, plumas EMIT) quedan documentadas como **Fase 2**.

Suplemento de la familia de proyectos InSAR/DEM/nightlights sobre Vaca Muerta, y de la guía
[satélites EO](https://mpodeley.github.io/satelites-eo/).

## Desarrollo local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve   # http://127.0.0.1:8000
```

## Regenerar datos y visualizaciones

```bash
# Producción por operador (denominador) + visualizaciones
pip install pandas shapely folium matplotlib
python docs/pipeline/produccion_operador.py
python docs/pipeline/produccion_visuals.py
```

Datos de entrada en `docs/data/` (producción mensual por área×empresa y concesiones con operador,
de la Secretaría de Energía / proyecto estado-del-sistema). El push a `main` despliega a GitHub Pages.
