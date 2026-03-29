<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# basado en este documento, haz una lista de entidades que podamos usar como target para el app

Basado en los archivos del proyecto, especialmente los logs del ETL y el análisis del audit, la lista de **target institutions** ya está prácticamente definida en el código. Aquí está destilada y priorizada:

***

## Instituciones Target para SICOP Health Intelligence

### Tier 1 — Core (90%+ del volumen médico)

Estas son las que generan el grueso de licitaciones médicas relevantes:[^1]


| Institución | Por qué incluirla |
| :-- | :-- |
| **CAJA COSTARRICENSE DE SEGURO SOCIAL (CCSS)** | Mayor comprador médico del país. Hospitales, EBAIS, clínicas, insumos, medicamentos, equipos. Keyword: `caja costarricense` |
| **INSTITUTO NACIONAL DE SEGUROS (INS)** | Compras de medicamentos de emergencia, insumos, servicios médicos quirúrgicos. Keyword: `ins ` |
| **MINISTERIO DE SALUD** | Rector del sector, compra equipamiento, reactivos, servicios de laboratorio. Keyword: `ministerio de salud` |
| **INCIENSA** | Equipos de laboratorio, reactivos inmunológicos, proyectos JPS-INCIENSA. Keyword: `inciensa`, `instituto costarricense de investigacion` |

### Tier 2 — Relevantes (volumen moderado, compras especializadas)

| Institución | Por qué incluirla |
| :-- | :-- |
| **JUNTA DE PROTECCIÓN SOCIAL (JPS)** | Co-financia proyectos INCIENSA y equipamiento hospitalario. Keyword: `junta de proteccion social` |
| **UNIVERSIDAD DE COSTA RICA (UCR)** | Tiene farmacia institucional y laboratorios clínicos. Keyword: `universidad de costa rica` |
| **CENDEISS** | Centro de desarrollo estratégico e información en salud. Keyword: `cendeiss` |
| **FARMACIA NACIONAL** | Compras de medicamentos de alto volumen. Keyword: `farmacia nacional` |

### Tier 3 — Opcionales (bajo volumen, monitorear post-lanzamiento)

| Institución | Contexto |
| :-- | :-- |
| IAFA | Compras de insumos para atención de adicciones |
| CONAPAM | Insumos y servicios para adultos mayores |
| CONSEJO DE SALUD OCUPACIONAL | Volumen muy bajo, compras ocasionales |
| HOSPITALES PRIVADOS (asociaciones) | Sujetos privados con implementación activa en SICOP [^1] |


***

## Lista final para el ETL (`INSTITUCIONES_TARGET`)

Esta es la lista lista para pegar directo en `fetcher.py`, basada en el audit:[^1]

```python
INSTITUCIONES_TARGET = [
    # Tier 1 — Core
    "CAJA COSTARRICENSE DE SEGURO SOCIAL",
    "INSTITUTO NACIONAL DE SEGUROS",
    "MINISTERIO DE SALUD",
    "INSTITUTO COSTARRICENSE DE INVESTIGACION Y ENSENANZA EN NUTRICION Y SALUD",  # INCIENSA
    # Tier 2
    "JUNTA DE PROTECCION SOCIAL",
    "UNIVERSIDAD DE COSTA RICA",
    "CENDEISS",
    "FARMACIA NACIONAL",
]
```


***

El impacto estimado al filtrar solo estas instituciones desde el origen es pasar de **695 registros → 50-80**, con una tasa de hits médicos del ~80% vs el 3.7% actual. La CCSS sola jala ~90% de las licitaciones médicas relevantes, así que el Tier 1 es lo mínimo viable para arrancar el frontend.[^1]

¿Quieres que ampliemos el Tier 2 con evidencia de volumen real, o arrancamos a integrar esta lista en el `fetcher.py`?
<span style="display:none">[^2]</span>

<div align="center">⁂</div>

[^1]: sicop-health-intelligence-esta-gqfmCUe3TUejQoVkUDmcxg.md

[^2]: ARQUITECTURE.md

