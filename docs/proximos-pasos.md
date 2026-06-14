# Próximos pasos (Fase 2)

La Fase 1 dejó listos la pregunta, los antecedentes, la metodología y el denominador. El **flaring →
CO₂ por operador ya está hecho** ([resultado](flaring.md)). Lo que sigue:

## 1. Flaring → CO₂ por operador  ✅ hecho

VIIRS Nightfire 2024 → 113 antorchas → CO₂ por operador e **intensidad por barril**. Ver
[Flaring](flaring.md). Posibles mejoras: **serie temporal** (2012–2024) para ver la tendencia, y afinar
el factor de conversión por composición del gas.

## 2. Metano de cuenca  ✅ hecho (capa de contexto)

- **TROPOMI / Sentinel-5P** XCH₄ medio 2019–2024 sobre el AOI (vía Google Earth Engine) → mapa de
  **cuenca**, contrastado con [Hancock et al. 2025](antecedentes.md) (~5,9 % Argentina). Ver
  [Metano](metano.md).
- **Descartado por diseño:** la inversión **por clúster** (~50 km, ERA5-Land, ±40 %). A esa resolución
  y con concesiones solapadas no distingue operadores → falsa precisión. El número robusto de intensidad
  ya existe (Hancock et al. 2025) y se cita como contexto.

## 3. Plumas puntuales  ✅ hecho (validación)

- Catálogo de plumas de **EMIT** (NASA, `EMITL2BCH4PLM`) consultado sobre el AOI vía CMR: **1 pluma**
  catalogada (2023-01-29 → Río Neuquén / YPF). Ver [Metano](metano.md). Cobertura esporádica → sirve de
  **validación puntual**, no de inventario.
- Pendiente opcional: sumar eventos **Sentinel-2/Landsat** sobre *hot spots* conocidos.

## 4. Cruce final e integración

- Combinar flaring-CO₂ + metano en una **huella de GEI por BOE y por operador** (CO₂e), con su
  incertidumbre.
- Sumar este proyecto como **5º caso** de la [guía de satélites EO](https://mpodeley.github.io/satelites-eo/)
  una vez que haya resultado de emisiones.

!!! note "Dependencias"
    Algunos datos requieren **registro gratuito**: VIIRS Nightfire (EOG), Earthdata/CMR (NASA, EMIT) y
    **Google Earth Engine** (TROPOMI, con un proyecto noncommercial). Nada de esto es de pago.
