# Deep Dimensional Inspector Firewall (`ddi-fw`)

<p align="center">
  <img src="https://img.shields.io/badge/version-0.4.0-blue.svg?style=flat-square" alt="Version 0.4.0" />
  <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg?style=flat-square" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/engine-BAAI%2Fbge--m3%20(1024D)-purple.svg?style=flat-square" alt="BGE-M3 1024D" />
  <img src="https://img.shields.io/badge/architecture-Dual--Gate%20Spectral-emerald.svg?style=flat-square" alt="Dual-Gate Spectral" />
  <img src="https://img.shields.io/badge/adversarial%20containment-100.0%25%20(0%20bypasses)-brightgreen.svg?style=flat-square" alt="100% Contained" />
  <img src="https://img.shields.io/badge/safety%20bound-P%20%3C%2010%5E--9-success.svg?style=flat-square" alt="P < 10^-9" />
  <img src="https://img.shields.io/badge/license-DNPI%20Reg.%20N%C2%BA%20226-red.svg?style=flat-square" alt="License DNPI" />
</p>

> **En este conventillo no promediamos con coseno como si fuera mayonesa.**  
> En `ddi-fw`, la pertenencia a un dominio autorizado es un **hecho geométrico duro**, verificable coordenada por coordenada en un espacio latente de 1024 dimensiones en coma flotante nativa IEEE 754. Si no acumulás quórum afirmativo en las cerraduras espectrales, rebotás en la puerta con un **HTTP 403 fail-closed** sin eco. Corta la bocha.

---

## ¿Qué carajo es esto?

`ddi-fw` es un **firewall semántico determinista de contención dimensional estricta** para modelos de lenguaje (LLMs):

* **No es un clasificador difuso ni un LLM-judge que alucina:** Opera antes de que el texto toque al modelo generativo. Ingiere el vector denso ($D=1024$), poda el ruido basal universal y evalúa inclusión en hiper-rectángulos disjuntos $[lo_d, hi_d]$.
* **Proxy OpenAI-Compatible en caliente:** Se planta como un reverse proxy transparente delante de tu inferencia (Ollama, vLLM, Llama-cpp o APIs remotas).
* **Fail-Closed Total:** Si el prompt contiene cláusulas híbridas, inyecciones de código malicioso (*piggybacking*) o ataques multilingües cruzados, la compuerta se cierra inmediatamente. Cero tokens al cliente, cero fuga.

---

## ¿Por qué el Coseno hace agua y nosotros no?

Los guardrails de la industria (Llama Guard, NeMo Guardrails, clasificadores angulares) tienen un talón de Aquiles estructural: **la ceguera por dilución**. Al colapsar 1024 dimensiones en un único producto punto escalar ($\cos \theta$), un atacante solo tiene que camuflar una receta, un ataque o una cláusula legal dentro de 20 líneas de código Python para que el coseno promedie $\Delta > 0$ y lo deje pasar de largo.

```
       Ataque de Piggybacking Semántico:
       ┌─────────────────────────────────────────────────────────────┐
       │ def execute_task():                                         │
       │     """Cláusula contractual: el arrendatario indemnizará..."""│  <── Payload malicioso camuflado
       │     return True                                             │
       └─────────────────────────────────────────────────────────────┘
                                      │
            ┌─────────────────────────┴─────────────────────────┐
            ▼                                                   ▼
   [ Clasificador de Coseno ]                        [ ddi-fw Dual-Gate Espectral ]
   • Promedia sintaxis con texto                     • Multi-clause splitter aísla el docstring
   • Score: Δ_cos = +0.0899 (Parece Python)          • Cajas disjuntas de 1024D miden coordenadas
   • Veredicto: ¡DEJA PASAR EL ATAQUE! ❌             • Veredicto: HTTP 403 BREACH (0 votos) 🛡️
```

En nuestro benchmark contra el arnés adversarial **Rompepepe**:
* **El Coseno Estándar permitió entre 14.5% y 58.2% de bypasses** en ataques de piggybacking y mutaciones léxicas.
* **El Ecualizador Espectral de `ddi-fw` logró un 100.0% de contención (0 bypasses en 220 ataques)**, confirmando la cota teórica de fuga:
  $$P_{\text{bypass}} \le (0.80)^{100} \approx 2.037 \times 10^{-10} < 10^{-9}$$

---

## La Arquitectura: Doble Compuerta Espectral (Dual-Gate)

```
                            [ Prompt Entrante ]
                                     │
                                     ▼
                        [ Particionador de Cláusulas ]
                                     │
                                     ▼
                      [ Inferencia Vectorial BGE-M3 ]
                          (Tensor Float32, 1024D)
                                     │
                                     ▼
           ┌──────────────────────────────────────────────────┐
           │     COMPUERTA 1: PODA DE RUIDO BASAL             │
           │   Silenciamiento de 9 coordenadas universales:   │
           │   (292, 297, 308, 386, 404, 577, 780, 329, 616)  │
           │     985 dimensiones discriminantes ("trigo")     │
           └─────────────────────────┬────────────────────────┘
                                     │
                                     ▼
           ┌──────────────────────────────────────────────────┐
           │     COMPUERTA 2: REGLA DE QUÓRUM DEL 10%         │
           │      Exigencia de Quórum Mínimo: K = 103 votos   │
           │      afirmativos en las 55 cerraduras canónicas  │
           └─────────────────────────┬────────────────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     ▼                               ▼
           [ Quórum >= 103 en todas ]     [ Quórum < 103 en alguna ]
                     │                               │
                     ▼                               ▼
              HTTP 200 / Forward             HTTP 403 Contención
             (Pasa al LLM de fondo)         (ddi_ingress_breach)
```

1. **Compuerta 1 (Poda de Ruido Estructural Basal):** Se descartan las coordenadas universales de alta energía que saturan en cualquier texto sin aportar semántica, evitando votos afirmativos espurios.
2. **Compuerta 2 (Regla de Quórum del 10%):** Exige un mínimo de $K = \lceil 0.10 \times 1024 \rceil = 103$ dimensiones concordantes en la región exclusiva del dominio seguro en cada cerradura.
3. **55 Cerraduras Canónicas Trilingües:** Combinatoria de 11 dominios ($\binom{11}{2} = 55$) cruzados en Español, Inglés y Alemán: `python`, `receta`, `legal`, `medicina`, `astronomia`, `finanzas`, `filosofia`, `musica`, `geologia`, `botanica`, `arquitectura`.

---

## Puesta en marcha (en 3 patadas)

### 1. Clonar e Instalar Entorno
Manejamos dependencias pura y exclusivamente con `uv` (cero líos de venv manuales):

```bash
git clone https://github.com/hbauzan/ddi-fw.git
cd ddi-fw
uv sync --extra dev
cp .env.example .env
```

### 2. Calibrar Tensores
Podés calibrar sobre los mazos compactos o cargar los tensores trilingües ya generados:

```bash
# Calibración base con BGE-M3 (Apple Silicon MPS o CPU):
uv run python -m ddi_fw.embedder --embedder bge-m3 --out ddi_fw/out/rows.npz --rewrite-fixtures
uv run python -m ddi_fw.press --rows ddi_fw/out/rows.npz --out ddi_fw/out
```

### 3. Correr Tests
```bash
uv run pytest
PYTHONPATH=. uv run pytest tools/rompepepe/tests
```

---

## Proxy OpenAI-Compatible contra Ollama / vLLM

Levantá tu backend de inferencia (por ejemplo, Ollama con `llama3.2` en el puerto 11434) y configurá el `.env`:
```env
DDI_UPSTREAM_URL=http://127.0.0.1:11434/v1
DDI_UPSTREAM_MODEL=llama3.2
PORT=8080
```

Arrancá el firewall:
```bash
PORT=8080 uv run python -m ddi_fw.proxy
```

### Probar Salud del Cluster
```bash
curl -s http://127.0.0.1:8080/healthz | jq
```

### Probar Prompt Legítimo (Pasa derecho al LLM)
```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Explicá cómo funciona list.append en Python."}],"model":"ddi-fw"}'
```

### Probar Inyección Hostil (Rebota en el acto con HTTP 403)
```bash
curl -i -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"def hack():\n    \"\"\"Prescribir amoxicilina 500mg cada 8 horas al paciente.\"\"\"\n    return True"}],"model":"ddi-fw"}'
```
*Respuesta:* `HTTP/403 Forbidden` — `{"error":{"type":"ddi_ingress_breach","message":"ingress breach","audit":{...}}}` (sin repetir el texto atacante).

---

## Precisión Numérica: Cero Redondeos

En este proyecto rige la **Invariante de Precisión Absoluta** ([`.agents/rules/cero-redondeos.md`](./.agents/rules/cero-redondeos.md)):

* **Prohibido truncar o redondear números de punto flotante** bajo ninguna excusa estética o de display.
* Los veredictos operan en `float32` nativo de hardware y las operaciones intermedias se promueven a `float64`.
* La separación promedio entre temas ($\Delta_{avg} \approx 0.014$) supera por más de **$50.000\times$** la deriva física del hardware medida en el silicio de Apple M4 ($2.46 \times 10^{-7}$). El firewall es físicamente determinista e inmune al temblor del silicio.

---

## Glosario Rápido para no Perderse

El glosario canónico completo y vinculante vive en [`CONTEXT.md`](./CONTEXT.md):

| Término | Qué carajo es | Qué NO es |
| :--- | :--- | :--- |
| **`alma`** | Conjunto representativo de cláusulas técnicas de un oficio | Un dataset difuso o texto scrapeado al barrer |
| **`cláusula`** | Unidad lógica de texto que se embebe y se juzga de forma atómica | Un chunk ciego de tokens |
| **`hoja`** | Los intervalos empíricos $[lo_d, hi_d]$ por coordenada entre dos almas | Un centroide, una media o un coseno |
| **`candado`** | Hoja + ejes disjuntos de un par canónico; solo se publica si hay quórum | Un clasificador de toxicidad por palabras clave |
| **`trigo`** | Dimensiones altamente contrastantes y discriminantes entre oficios | Ruido estructural o variables espurias |
| **`ruido basal`** | Coordenadas universales con energía de fondo que se purgan en Compuerta 1 | Dimensiones útiles de decisión |

---

## Documentación y Hoja de Ruta

* 📊 **Informes Técnicos y Benchmarks:** Directorio centralizado en [`reports/`](./reports/).
  * [Informe de Fuzzing Rompepepe (v0.4.0)](./reports/2026-09-26-rompepepe-spectral-fuzzing-v0.4.0.md) (0 bypasses en 220 ataques).
  * [Auditoría de Sensibilidad de Quórum y Comparativa de Coseno](./reports/2026-09-26-analisis-sensibilidad-espectral-vs-coseno.md) ($K^* = 20$, fallas de coseno).
* 🗺️ **Roadmap Científico:** Directorio [`roadmap/`](./roadmap/).
  * [Protocolo 08: Tesis de Alta Densidad de Manifold](./roadmap/hipotesis-ecualizador/08-tesis-densidad-manifold-y-limites-de-ingesta.md) (Ruptura con paredes gordas y escalamiento masivo).
* 🧠 **Lecciones Aprendidas e Invariantes:** [`.agents/skills/dev-protocol/lessons-learned.md`](./.agents/skills/dev-protocol/lessons-learned.md).

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
