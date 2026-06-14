# Próximos pasos (Fase 2)

La Fase 1 dejó listos **la pregunta, los antecedentes, la metodología y el denominador** (producción
por operador). La Fase 2 suma el **numerador satelital**. En orden de solidez:

## 1. Flaring → CO₂ por operador  (lo más firme)

- Descargar **VIIRS Nightfire** (Earth Observation Group, [eogdata.mines.edu](https://eogdata.mines.edu))
  — requiere una **cuenta gratuita**. Filtrar sitios en el AOI de Vaca Muerta, 2023–2025.
- Asignar cada antorcha a su **concesión/operador** (cruce con `concesiones_neuquina.geojson`).
- Convertir volumen quemado → **CO₂** (+ CH₄ *slip*) y dividir por la producción → **kg CO₂/BOE** y
  **% de gas quemado** por operador.
- Entregable: ranking de operadores por **intensidad de flaring**, mapa de antorchas, serie temporal.

## 2. Metano de cuenca y por clúster  (ambicioso)

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
