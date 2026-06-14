# Próximos pasos (Fase 2)

La Fase 1 dejó listos la pregunta, los antecedentes, la metodología y el denominador. El **flaring →
CO₂ por operador ya está hecho** ([resultado](flaring.md)). Lo que sigue:

## 1. Flaring → CO₂ por operador  ✅ hecho

VIIRS Nightfire 2024 → 113 antorchas → CO₂ por operador e **intensidad por barril**. Ver
[Flaring](flaring.md). Posibles mejoras: **serie temporal** (2012–2024) para ver la tendencia, y afinar
el factor de conversión por composición del gas.

## 2. Metano de cuenca y por clúster  (lo siguiente, ambicioso)

- Traer **TROPOMI / Sentinel-5P** XCH₄ sobre el AOI (Copernicus / GES DISC) y reproducir el número de
  **cuenca** (contrastar con [Hancock et al. 2025](antecedentes.md), ~5,9 % Argentina).
- Inversión **por clúster** (~50 km) con viento **ERA5-Land** → intensidad de CH₄ por sub-área, con
  **barras de error explícitas** (±40 %).
- Entregable: mapa de intensidad de metano por clúster, con caveats.

## 3. Plumas puntuales  (validación)

- Revisar el catálogo de plumas de **EMIT** (NASA) y eventos **Sentinel-2/Landsat** sobre el AOI.
- Donde haya cobertura, cuantificar plumas individuales para **validar** los puntos 1 y 2.

## 4. Cruce final e integración

- Combinar flaring-CO₂ + metano en una **huella de GEI por BOE y por operador** (CO₂e), con su
  incertidumbre.
- Sumar este proyecto como **5º caso** de la [guía de satélites EO](https://mpodeley.github.io/satelites-eo/)
  una vez que haya resultado de emisiones.

!!! note "Dependencias"
    Algunos datos requieren **registro gratuito**: VIIRS Nightfire (EOG), Earthdata (NASA) y Copernicus.
    Nada de esto es de pago.
