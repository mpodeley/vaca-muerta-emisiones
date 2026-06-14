# Metano: la capa de contexto (cuenca)

El [flaring → CO₂](flaring.md) se atribuye a cada operador porque las antorchas son **puntos fijos y
geolocalizados**. El **metano (CH₄)** —fugas y venteos— es lo más relevante para el clima pero lo
**menos atribuible** desde el espacio: o se lo ve a **escala de cuenca** (TROPOMI, ~7 km) o como
**plumas puntuales y esporádicas** (EMIT, 60 m). Ninguna de las dos reparte el metano por operador.

Por eso esta página es **contexto honesto**, no un numerador por empresa. Mostramos dos cosas: dónde
aparece Vaca Muerta en el mapa de metano de cuenca, y la única pluma puntual que NASA EMIT catalogó
sobre el área.

!!! info "Por qué *no* hacemos la “intensidad de metano por operador”"
    La idea original (Fase 2) era una **inversión por clúster** de TROPOMI con viento ERA5-Land para
    sacar flujos por sub-área. La descartamos: a ~7 km de resolución, con error de **±40 %** y
    concesiones solapadas, el resultado no distingue operadores y daría una falsa precisión. El número
    **robusto** de intensidad de metano de la región ya existe y es de terceros:
    [Hancock et al. 2025](antecedentes.md) lo estima en **~5,9 % para Argentina**, atribuido a la
    expansión de Neuquén.

## 1. Metano de cuenca — XCH₄ medio de TROPOMI

Promediando **29.503 imágenes de Sentinel-5P / TROPOMI (2019–2024)** sobre el área de Vaca Muerta se ve
el campo de **XCH₄** (columna de metano, en ppb) de la cuenca:

<iframe src="../assets/metano_mapa.html" width="100%" height="540" style="border:1px solid #ccc;border-radius:6px"></iframe>

*Overlay: XCH₄ medio TROPOMI 2019–2024 (más claro = más metano). Encima, las concesiones y la pluma de
EMIT. Activá/desactivá capas arriba a la derecha. Fuente: `COPERNICUS/S5P/OFFL/L3_CH4` vía Google Earth
Engine.*

![XCH₄ medio TROPOMI sobre Vaca Muerta, 2019–2024](assets/metano_tropomi.png){ loading=lazy }

Sobre el AOI el XCH₄ medio va de **~1.740 a ~1.860 ppb**, con un realce sobre la franja productiva
central-este. Pero ese contraste hay que leerlo con cuidado:

!!! warning "Cómo (no) leer este mapa"
    - **Es señal de cuenca, no de operador.** Un píxel de ~7 km mezcla muchas concesiones.
    - **El valor absoluto no “prueba” un hotspot por sí solo.** El XCH₄ de TROPOMI tiene sesgos por
      terreno, albedo y ángulo solar; la variación intra-cuenca incluye artefactos de retrieval.
    - **El número robusto es de la inversión de [Hancock et al. 2025](antecedentes.md)** (~5,9 % de
      intensidad de metano para Argentina, atribuida a la expansión de Neuquén): eso sí es un resultado
      científico atribuido, y es el ancla de contexto de esta capa.

## 2. La única pluma puntual — NASA EMIT

EMIT (espectrómetro de imágenes en la ISS) detecta **plumas individuales de metano a 60 m**, con la
contrapartida de una **cobertura oportunista**: solo ve un punto cuando la ISS pasa por encima con buena
geometría. Consultando el catálogo público de plumas de EMIT
([`EMITL2BCH4PLM`](https://www.earthdata.nasa.gov/data/catalog/lpcloud-emitl2bch4plm-002), vía el CMR de
Earthdata) sobre el AOI, el resultado es contundente por lo escueto:

| Pluma | Fecha | Ubicación | Concesión | Operador |
|---|---|---|---|---|
| EMIT #596 | 2023-01-29 | −38,77 ; −68,21 | **Río Neuquén** | **YPF S.A.** |

**Una sola pluma** catalogada en todo el archivo de EMIT sobre Vaca Muerta (en el borde este, concesión
Río Neuquén de YPF). Eso **no significa que haya poco metano**: significa que EMIT pasó pocas veces y con
geometría útil. Es justamente la limitación de las plumas puntuales como inventario.

!!! quote "El resultado honesto"
    Ausencia de plumas **no es** ausencia de emisiones. EMIT confirma que **hay** metano puntual
    detectable en la cuenca (al menos un evento sólido, atribuible a una concesión), pero su cobertura
    esporádica lo vuelve una herramienta de **validación**, no de monitoreo continuo.

## Qué aporta esta capa

- **TROPOMI** pone a Vaca Muerta en el mapa de metano de cuenca y enlaza con el ~5,9 % de
  [Hancock et al. 2025](antecedentes.md): el contexto regional es real.
- **EMIT** aporta un punto de verdad a 60 m (pluma #596 → Río Neuquén / YPF), y de paso demuestra el
  límite de cobertura.
- **Lo que sigue sólido y por operador es el [flaring → CO₂](flaring.md).** El metano queda como capa de
  **contexto de cuenca**, explícitamente no repartida por empresa.

> Reproducible: `python docs/pipeline/metano_tropomi.py --project <tu-proyecto-GEE>` (TROPOMI vía Earth
> Engine), `python docs/pipeline/metano_emit.py` (plumas EMIT vía CMR, sin login) y
> `metano_visuals.py`. Datos en `docs/data/metano_tropomi_grid.json` y `metano_emit_plumas.geojson`.
