# ¿Cuánto emite cada barril de Vaca Muerta?

La producción de petróleo y gas emite **gases de efecto invernadero**: **CO₂** (sobre todo por la
**quema de gas en antorcha**, *flaring*) y **metano (CH₄)** (fugas y venteos). La pregunta de este
proyecto es concreta:

> **¿Cuál es la huella de emisión por cada m³ de gas o barril de petróleo producido, y cómo se reparte
> por operador?** ¿Se puede estimar con **datos satelitales públicos**, sin información de las
> empresas?

Es un experimento metodológico —en la línea de los otros proyectos sobre Vaca Muerta
([InSAR](https://mpodeley.github.io/vaca-muerta-insar/),
[nightlights](https://mpodeley.github.io/vaca-muerta-nightlights/))— y un suplemento aplicado de la
[guía de satélites EO](https://mpodeley.github.io/satelites-eo/).

## Los tres caminos (y cuán lejos llega cada uno)

Medir emisiones desde el espacio y atribuirlas a un operador no es igual de fácil para cada gas:

| Camino | Qué mide | ¿Atribuible a operador? |
|---|---|---|
| **Flaring → CO₂** (VIIRS Nightfire) ✅ | volumen de gas quemado por antorcha, geolocalizado | **Sí** — ya **calculado por operador**: ver [Flaring](flaring.md) |
| **Metano de cuenca** (TROPOMI) | intensidad de CH₄ a escala de cuenca (~7 km) | **No directo** — sí da el número de cuenca; por clúster con inversión y error grande |
| **Plumas puntuales** (EMIT, Sentinel-2) | emisiones grandes de un punto | **A veces** — alta resolución pero **cobertura esporádica** |

!!! success "Lo que ya está calculado"
    - **Denominador:** la [producción por operador](produccion.md) (gas, petróleo, BOE).
    - **Flaring → CO₂ por operador:** [el resultado](flaring.md) — **113 antorchas, ~2,4 Mt CO₂ en
      2024**, con la **intensidad por barril** de cada operadora (kg CO₂/BOE).

    Queda pendiente (Fase 2) el **metano** (fugas/venteo): inversión TROPOMI por clúster y plumas EMIT.
    Ver [Próximos pasos](proximos-pasos.md).

## Qué vas a encontrar

- **[Antecedentes y datos](antecedentes.md)** — quién ya midió esto (incluida una estimación satelital
  de **~5,9 % de intensidad de metano para Argentina**) y qué datasets públicos sirven.
- **[Metodología](metodologia.md)** — cómo se calcula la huella: flaring→CO₂ por operador y metano por
  clúster, con los factores de conversión y sus fuentes.
- **[Producción por operador](produccion.md)** — el resultado concreto de la Fase 1: el ranking de
  operadores y su producción (el denominador de toda intensidad).

!!! note "Honestidad metodológica"
    Atribuir emisiones a un operador desde el espacio tiene límites reales (resolución, cobertura,
    factores de conversión). Este proyecto los explicita y separa **lo medible con confianza** de
    **lo estimativo**. Se usó **Claude (Anthropic)** para asistir; el contenido fue revisado por el autor.
