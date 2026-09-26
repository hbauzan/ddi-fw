# Deep Dimensional Inspector (`ddi-fw`)

<p align="center">
  <img src="https://img.shields.io/badge/versi%C3%B3n-0.4.0-slate.svg?style=flat-square" alt="Versión 0.4.0" />
  <img src="https://img.shields.io/badge/entorno-Python%203.11%2B-steelblue.svg?style=flat-square" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/car%C3%A1cter-banco%20de%20pruebas%20experimental-dimgray.svg?style=flat-square" alt="Banco de pruebas" />
  <img src="https://img.shields.io/badge/motor-BAAI%2Fbge--m3%20(1024D)-555555.svg?style=flat-square" alt="BGE-M3 1024D" />
  <img src="https://img.shields.io/badge/enfoque-inspecci%C3%B3n%20por%20coordenadas-334155.svg?style=flat-square" alt="Inspección por coordenadas" />
  <img src="https://img.shields.io/badge/licencia-DNPI%20Reg.%20N%C2%BA%20226-708090.svg?style=flat-square" alt="Licencia DNPI" />
</p>

> **Acá no hay misterio ni aspavientos de Silicon Valley.**  
> Este galpón de código es el **Deep Dimensional Inspector (DDI)**: un banco de pruebas modesto, armado para mirar despacio y por las piedras qué pasa adentro de las 1024 dimensiones de BGE-M3.  
> La idea de fondo es sencilla: en vez de promediar todo a bulto con un coseno y dar por bueno lo que venga, nos sentamos a inspeccionar coordenada por coordenada. Si una cláusula no calza en los límites geométricos de la hipótesis, se frena en seco y no pasa al modelo. Ta, sin más vueltas.

---

## De qué se trata esto: inspeccionar sin apuro

`ddi-fw` es el arnés de investigación y prototipado del **Deep Dimensional Inspector**, pensado como un banco de trabajo para evaluar la hipótesis de contención semántica:

* **Inspección dimensional profunda:** La costumbre generalizada es apretar 1024 dimensiones en un solo número angular ($\cos \theta$). Acá preferimos abrir el tensor y mirar coordenada por coordenada en coma flotante nativa IEEE 754.
* **Comprobación de la hipótesis:** Poner a prueba si una arquitectura de doble compuerta espectral (poda de ruido de fondo más quórum estricto) logra confinar dominios semánticos en hiper-rectángulos disjuntos $[lo_d, hi_d]$.
* **Proxy local para probar en frío:** Para no quedarse en la teoría, funciona como un reverse proxy transparente delante de un motor local (Ollama, vLLM, Llama-cpp), usando el formato estándar de OpenAI.
* **Precisión del silicio:** Rige la regla de **cero redondeos** ([`.agents/rules/cero-redondeos.md`](./.agents/rules/cero-redondeos.md)). En el taller no se redondea a ojo: los números se respetan tal como salen del hardware.

---

## El problema del promedio: por qué el coseno se marea con la mezcla

Los clasificadores basados en similitud coseno tienen una flaqueza conocida: **la dilución**. Cuando se promedian 1024 dimensiones en un solo escalar, un texto intruso bien envuelto en código legítimo pasa desapercibido porque la masa de sintaxis disimula el contenido:

```
       Mezcla de textos (Piggybacking):
       ┌─────────────────────────────────────────────────────────────┐
       │ def execute_task():                                         │
       │     """Cláusula contractual: el arrendatario indemnizará..."""│  <── Párrafo intruso camuflado
       │     return True                                             │
       └─────────────────────────────────────────────────────────────┘
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
   [ Clasificador de Coseno ]                       [ DDI: Inspección por Coordenadas ]
   • Promedia el texto con el código                • Parte las cláusulas y aísla el docstring
   • Da score positivo: Δ_cos = +0.0899             • Mide cada dimensión contra los límites
   • Resultado: lo deja pasar de largo              • Resultado: HTTP 403 (0 votos de quórum)
```

En las corridas con el banco de pruebas **Rompepepe**:
* **El coseno estándar dejó filtrar entre 14.5% y 58.2% de los casos** cuando se mezclaron textos ajenos dentro de funciones o estructuras válidas.
* **La compuerta dimensional del DDI contuvo las 220 muestras del protocolo v0.4.0**, respaldando de forma empírica la cota teórica calculada para la hipótesis:
  $$P_{\text{bypass}} \le (0.80)^{100} \approx 2.037 \times 10^{-10} < 10^{-9}$$

---

## Fundamento Teórico: Tesis de Alta Densidad de Manifold

¿Por qué se sostiene que el espacio latente aguanta mucho más texto del que se supone habitualmente?

El planteo matemático y la ruptura con la intuición euclidiana de "paredes gruesas" está desarrollado en el documento:  
📄 **[Protocolo 08: Tesis de Alta Densidad de Manifold y Límites de Ingesta](./roadmap/hipotesis-ecualizador/08-tesis-densidad-manifold-y-limites-de-ingesta.md)**

Allí se argumenta por qué en 1024 dimensiones el agregado de datos especializados no satura el espacio: al contrario, ayuda a limpiar las dimensiones espurias y afina los bordes de decisión, permitiendo límites más definidos.

---

## El mecanismo de inspección: Doble compuerta espectral

```
                            [ Texto entrante ]
                                     │
                                     ▼
                        [ Particionador de cláusulas ]
                                     │
                                     ▼
                       [ Inferencia Vectorial BGE-M3 ]
                           (Tensor Float32, 1024D)
                                     │
                                     ▼
           ┌──────────────────────────────────────────────────┐
           │     COMPUERTA 1: PODA DE RUIDO DE FONDO          │
           │   Se apagan 9 coordenadas universales de fondo:  │
           │   (292, 297, 308, 386, 404, 577, 780, 329, 616)  │
           │   Quedan 985 dimensiones con señal útil          │
           └─────────────────────────┬────────────────────────┘
                                     │
                                     ▼
           ┌──────────────────────────────────────────────────┐
           │     COMPUERTA 2: REGLA DE QUÓRUM (10%)           │
           │   Exige un mínimo de K = 103 votos afirmativos   │
           │   en las 55 cerraduras canónicas trilingües      │
           └─────────────────────────┬────────────────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
           [ Quórum >= 103 en todas ]     [ Quórum < 103 en alguna ]
                     │                               │
                     ▼                               ▼
              HTTP 200 / Adelante            HTTP 403 Contención
             (Pasa al modelo local)         (ddi_ingress_breach)
```

1. **Compuerta 1 (Poda de ruido de fondo):** Se silencian las coordenadas que tienen energía permanente sin importar el tema, evitando votos afirmativos que no corresponden.
2. **Compuerta 2 (Regla de quórum del 10%):** Se exigen al menos $K = \lceil 0.10 \times 1024 \rceil = 103$ dimensiones dentro de la región segura para cada par de dominios comparados.
3. **55 Cerraduras canónicas trilingües:** Combinaciones entre 11 dominios ($\binom{11}{2} = 55$) en Español, Inglés y Alemán: `python`, `receta`, `legal`, `medicina`, `astronomia`, `finanzas`, `filosofia`, `musica`, `geologia`, `botanica`, `arquitectura`.

---

## Puesta en marcha, sin misterio

El entorno se administra con `uv`, para mantener las cosas simples y ordenadas:

### 1. Descargar y preparar dependencias
```bash
git clone https://github.com/hbauzan/ddi-fw.git
cd ddi-fw
uv sync --extra dev
cp .env.example .env
```

### 2. Calibrar matrices del banco de pruebas
```bash
# Calibración sobre BGE-M3 (Apple Silicon MPS o CPU):
uv run python -m ddi_fw.embedder --embedder bge-m3 --out ddi_fw/out/rows.npz --rewrite-fixtures
uv run python -m ddi_fw.press --rows ddi_fw/out/rows.npz --out ddi_fw/out
```

### 3. Verificar que esté todo en orden
```bash
uv run pytest
PYTHONPATH=. uv run pytest tools/rompepepe/tests
```

---

## Probando el proxy local con Ollama o vLLM

Configurá el archivo `.env` apuntando al motor local que tengas corriendo (por ejemplo, Ollama en el puerto 11434):
```env
DDI_UPSTREAM_URL=http://127.0.0.1:11434/v1
DDI_UPSTREAM_MODEL=llama3.2
PORT=8080
```

Levantá el inspector:
```bash
PORT=8080 uv run python -m ddi_fw.proxy
```

### Caso normal (pasa derecho al modelo):
```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Explicá cómo funciona list.append en Python."}],"model":"ddi-fw"}'
```

### Caso con trampa (se frena en la compuerta dimensional):
```bash
curl -i -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"def hack():\n    \"\"\"Prescribir amoxicilina 500mg cada 8 horas al paciente.\"\"\"\n    return True"}],"model":"ddi-fw"}'
```
*Respuesta:* `HTTP/403 Forbidden` — `{"error":{"type":"ddi_ingress_breach","message":"ingress breach","audit":{...}}}` (corta ahí, sin repetir el texto intruso).

---

## Precisión numérica: cero redondeos

En este trabajo rige la **Invariante de Precisión Absoluta** ([`.agents/rules/cero-redondeos.md`](./.agents/rules/cero-redondeos.md)):

* No se redondea ni se trunca ningún valor de punto flotante por razones estéticas.
* Las comparaciones se resuelven en `float32` nativo y las acumulaciones intermedias van a `float64`.
* La separación media entre dominios ($\Delta_{avg} \approx 0.014$) supera con holgura la deriva física medida en el silicio ($2.46 \times 10^{-7}$). El criterio es estricto: lo que decide es la geometría, no el azar.

---

## Glosario criollo del taller

Para no enredarse con los términos de trabajo (documentados formalmente en [`CONTEXT.md`](./CONTEXT.md)):

| Término | Qué es acá adentro | Qué NO es |
| :--- | :--- | :--- |
| **`alma`** | Conjunto de oraciones o cláusulas que definen un oficio o tema | Un dataset ruidoso bajado de apuro |
| **`cláusula`** | Unidad mínima de texto que se procesa y se evalúa | Un pedazo ciego cortado por tokens |
| **`hoja`** | Los límites medidos $[lo_d, hi_d]$ por coordenada entre dos temas | Un promedio, un centroide o un ángulo |
| **`candado`** | Hoja más los ejes disjuntos; solo vale si alcanza el quórum | Una lista de palabras prohibidas |
| **`trigo`** | Las coordenadas que diferencian con claridad un tema de otro | Dimensiones vacías o con ruido |
| **`ruido basal`** | Coordenadas que prenden en casi cualquier texto y se silencian | Dimensiones con información útil |

---

## Informes y documentación de campo

* 📊 **Registros de pruebas:** Carpeta [`reports/`](./reports/).
  * [Informe de Fuzzing Rompepepe (v0.4.0)](./reports/2026-09-26-rompepepe-spectral-fuzzing-v0.4.0.md) (Lote de 220 casos de prueba).
  * [Auditoría de Sensibilidad de Quórum y Comparativa de Coseno](./reports/2026-09-26-analisis-sensibilidad-espectral-vs-coseno.md) ($K^* = 20$, límites medidos).
* 🗺️ **Roadmap de trabajo:** Carpeta [`roadmap/`](./roadmap/).
  * [Protocolo 08: Tesis de Alta Densidad de Manifold](./roadmap/hipotesis-ecualizador/08-tesis-densidad-manifold-y-limites-de-ingesta.md).
* 🧠 **Notas de trabajo e invariantes:** [`.agents/skills/dev-protocol/lessons-learned.md`](./.agents/skills/dev-protocol/lessons-learned.md).

---

## Licencia y Registro Oficial de Propiedad Intelectual

**Copyright (c) 2026 Héctor Andrés Bauzán Saavedra, AKA "eletor". Todos los derechos reservados.**

El software, algoritmos, arquitectura de hiper-cajas espectrales y documentación contenidos en este repositorio son **propiedad exclusiva del titular**. No se otorga ninguna licencia de uso, copia, modificación o distribución comercial sin previa autorización escrita.

### Declaración de Obra Derivada y Registro Oficial
Todo lo contenido en este repositorio deriva del trabajo y arquitectura registrada en:  
🔗 **[https://github.com/hbauzan/semantic-firewall](https://github.com/hbauzan/semantic-firewall)**

* **Obra / Work:** *Three-Headed Semantic Firewall*
* **Titular / Author:** Héctor Andrés Bauzán Saavedra
* **Número de Inscripción:** Nº 226
* **Fecha de Inscripción:** 04/08/2026 (August 4, 2026)
* **Organismo / Registry:** Dirección Nacional de la Propiedad Industrial (DNPI - MIEM) / Registro de Software, República Oriental del Uruguay
* **Marco Legal:** Ley 9.739 de 17/12/1937 (conforme a Ley N° 20.212 y Decreto N° 39/2025)

*Pursuant to Section 4(d) of the Apache License, Version 2.0, the [NOTICE](./NOTICE) file must be retained and distributed with any reproduction or derivative work.*
