# Metodología

La **huella de emisión** se define como **emisiones / producción**: cuánto CO₂ o CH₄ por cada **barril
equivalente de petróleo (BOE)** producido, por operador. Esta página describe cómo se calcula cada
término. Lo que **ya está hecho** en la Fase 1 es el **denominador** (producción); el **numerador**
(emisiones satelitales) es la Fase 2.

## El denominador: producción por operador  ✅ hecho

A partir de la producción mensual por **pozo / área / empresa** de la Secretaría de Energía argentina
(dataset público "Capítulo IV"), se agrega por operador para el año **2025** (último año calendario
completo) y se convierte a **BOE**:

- **Petróleo:** 1 m³ = **6,2898** barriles (1 barril = 1 BOE por definición).
- **Gas:** 1 BOE ≈ **6.000 pies³ ≈ 169,9 m³** de gas natural (regla volumétrica 6:1).
- **BOE total** = barriles de petróleo + (m³ de gas / 169,9).

El resultado está en [Producción por operador](produccion.md) y en
`docs/data/produccion_por_operador.csv`.

## El numerador A: CO₂ de flaring por operador  ✅ hecho

El camino **más atribuible**, porque las antorchas son infraestructura fija y geolocalizada. **Ya está
calculado** — [ver el resultado](flaring.md). El procedimiento:

1. **VIIRS Nightfire** (Earth Observation Group) → lista de sitios de flaring activos con el **volumen
   de gas quemado** estimado (m³/año) por la radiancia/temperatura del foco.
2. **Atribución:** cada antorcha (lat/lon) cae dentro de una **concesión** → se asigna a su
   **operador** (usando `concesiones_neuquina.geojson`, el mismo cruce espacial del mapa de
   [producción](produccion.md)).
3. **Conversión a CO₂:** volumen quemado × **~2,0 kg CO₂/m³** (combustión de gas natural; el factor
   exacto depende de la composición — se documentará la fuente, p. ej. metodología GGFR del Banco
   Mundial / directrices IPCC). Se suma el **CH₄ no quemado** (*slip*, ~2–5 %) con su GWP.
4. **Intensidad:** CO₂ de flaring del operador / su producción (BOE) → **kg CO₂/BOE** y **% del gas
   producido que se quema**.

## El numerador B: metano por clúster  🔜 Fase 2 (ambicioso)

El metano es lo más relevante climáticamente pero lo **menos atribuible**:

1. **Cuenca:** la intensidad de CH₄ de Neuquén a partir de la inversión TROPOMI publicada
   ([Hancock et al. 2025](antecedentes.md): ~5,9 % para Argentina) — número de referencia, no por
   operador.
2. **Clúster:** dividir Vaca Muerta en **sub-áreas por operador/concesión** (~50 km) y hacer una
   **inversión local** de TROPOMI con viento de **ERA5-Land**, obteniendo flujos por sub-área. Error
   honesto **±40 %**; solo distingue clústers grandes, no operadores solapados.
3. **Plumas:** donde **EMIT** o Sentinel-2 pasen sobre un *hot spot*, cuantificar plumas puntuales para
   validar.

!!! warning "Lo honesto desde el arranque"
    La **intensidad de metano por operador** será una **estimación regional con barras de error
    grandes**, no una medición directa. El flaring sí permite una atribución más limpia. Cualquier
    ranking se publicará con su incertidumbre explícita, siguiendo el espíritu de
    [PermianMAP](antecedentes.md).

## Atribución espacial (común a todo)

El cruce a operador usa las **160 concesiones de la cuenca Neuquina** (`concesiones_neuquina.geojson`,
con el campo `operador`): una detección satelital (antorcha, pluma o píxel) se asigna al operador del
polígono que la contiene. Es el mismo mecanismo que pinta el [mapa de operadores](produccion.md).
