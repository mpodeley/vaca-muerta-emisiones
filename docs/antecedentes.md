# Antecedentes y datos

¿Alguien ya midió emisiones de O&G desde satélite, y con qué datos públicos? Sí. Acá está lo
**verificado** que sostiene este proyecto.

## Antecedentes clave

- **Hancock, Jacob, et al. · 2025.** *Satellite quantification of methane emissions from South American
  countries: a high-resolution inversion of TROPOMI and GOSAT observations.* Atmospheric Chemistry and
  Physics 25, 797–817. [10.5194/acp-25-797-2025](https://doi.org/10.5194/acp-25-797-2025)
  → Estima la **intensidad de metano de Argentina en ~5,9 %** (muy por encima de estimaciones previas
  de ~1,5 %), atribuida explícitamente a la **expansión de la extracción en la cuenca Neuquina**. Es el
  ancla de que "hay señal" sobre Vaca Muerta — aunque a escala de cuenca.
- **Lauvaux et al. · 2022.** *Global assessment of oil and gas methane ultra-emitters.* Science 375,
  557–561. [10.1126/science.abj4351](https://doi.org/10.1126/science.abj4351)
  → Con **TROPOMI** detecta miles de "ultra-emisores" de metano de O&G en el mundo; método de
  referencia para encontrar grandes fugas desde el espacio.
- **PermianMAP (EDF).** [permianmap.org](https://www.permianmap.org/)
  → El **modelo metodológico**: rankear operadores por **intensidad de metano** (% del gas producido)
  cruzando mediciones con producción y geolocalización, en la mayor cuenca de shale de EE.UU.
- **Elvidge et al. · 2016.** *Methods for Global Survey of Natural Gas Flaring from VIIRS Data.*
  Energies 9(1), 14. [10.3390/en9010014](https://doi.org/10.3390/en9010014)
  → La base del producto **VIIRS Nightfire**: estima el **volumen de gas quemado por sitio**, que es lo
  más atribuible por ubicación.

## Datasets públicos utilizables

| Dataset | Qué da | Resolución | Para qué sirve acá | Límite |
|---|---|---|---|---|
| **VIIRS Nightfire** (EOG) | volumen de flaring por sitio, geolocalizado | ~375 m | **CO₂ de flaring por operador** | requiere factor de conversión; solo gas quemado |
| **TROPOMI / Sentinel-5P** | columna de CH₄ (XCH₄) | ~7×5,5 km (efectiva ~25 km) | intensidad de CH₄ de **cuenca** | no atribuye a operador directo |
| **EMIT** (NASA, ISS) | plumas puntuales de CH₄ | 60 m | validar/ubicar grandes fugas | cobertura **esporádica** |
| **Sentinel-2 / Landsat** | plumas muy grandes (SWIR) | 20–30 m | fugas grandes con cielo claro | baja sensibilidad/cadencia |
| **Producción por pozo** (Sec. Energía) | gas/petróleo por pozo, mes, concesión | — | el **denominador** (BOE por operador) | publicado con ~3 meses de lag |

!!! warning "Matriz de confianza (qué se puede afirmar)"
    - **Alta:** "la cuenca tiene intensidad de CH₄ ~5–7 %" (TROPOMI inversión, 2025); "el sitio de
      flaring X quema Q m³/día" (VIIRS, ±30 %).
    - **Media:** "el operador X tiene tal intensidad de CO₂ de flaring por BOE" (VIIRS + producción).
    - **Baja:** "el operador X tiene tal intensidad de **metano**" (TROPOMI a 7 km no resuelve un
      operador; requiere inversión por clúster con error grande, o plumas EMIT puntuales).

Las fuentes completas (portales de descarga y papers) están en [Referencias](referencias.md).
