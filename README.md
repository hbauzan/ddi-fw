# Deep Dimensional Inspector (`ddi-fw`)

<p align="center">
  <img src="https://img.shields.io/badge/version-0.4.0-blue.svg?style=flat-square" alt="Version 0.4.0" />
  <img src="https://img.shields.io/badge/python-3.11%2B-blue.svg?style=flat-square" alt="Python 3.11+" />
  <img src="https://img.shields.io/badge/type-experimental%20lab%20%2F%20research-indigo.svg?style=flat-square" alt="Experimental Lab" />
  <img src="https://img.shields.io/badge/engine-BAAI%2Fbge--m3%20(1024D)-purple.svg?style=flat-square" alt="BGE-M3 1024D" />
  <img src="https://img.shields.io/badge/focus-deep%20coordinate%20inspection-teal.svg?style=flat-square" alt="Deep Coordinate Inspection" />
  <img src="https://img.shields.io/badge/validation-empirical%20fuzzing-amber.svg?style=flat-square" alt="Empirical Fuzzing" />
  <img src="https://img.shields.io/badge/license-DNPI%20Reg.%20N%C2%BA%20226-red.svg?style=flat-square" alt="License DNPI" />
</p>

> **Acá no vendemos humo corporativo ni te prometemos una "IA mágica" que soluciona todo.**  
> Este repositorio es mi banco de pruebas: el **Deep Dimensional Inspector (DDI)**, una herramienta de estudio y laboratorio experimental para meter el bisturí en el espacio latente de 1024 dimensiones de BGE-M3.  
> La meta es clara: **inspeccionar profundamente** qué le pasa a los vectores semánticos en cada coordenada, poner a prueba empíricamente mi hipótesis de firewall semántico, y entender por qué la distancia coseno hace agua cuando un atacante camufla texto (*piggybacking*) mientras que una inspección geométrica coordenada por coordenada resiste.

---

## ¿Qué carajo es el DDI?

`ddi-fw` es el arnés de investigación y prototipado del **Deep Dimensional Inspector** aplicado a la seguridad semántica de LLMs:

* **Inspección dimensional profunda (no un clasificador ciego):** La industria suele colapsar 1024 dimensiones en un único número escalar ($\cos \theta$). Acá hacemos lo contrario: diseccionamos el tensor coordenada por coordenada en coma flotante nativa IEEE 754.
* **Laboratorio de prueba de hipótesis:** Implementa la arquitectura de doble compuerta espectral (poda de ruido basal + regla de quórum) para investigar si es posible confinar dominios semánticos en hiper-rectángulos disjuntos $[lo_d, hi_d]$.
* **Proxy experimental OpenAI-Compatible:** Para probar la hipótesis bajo fuego real con clientes e interfaces estándar, se monta como un reverse proxy transparente delante de motores locales de inferencia (Ollama, vLLM, Llama-cpp).
* **Física y precisión del silicio:** Rige la regla de **cero redondeos** ([`.agents/rules/cero-redondeos.md`](./.agents/rules/cero-redondeos.md)): no truncamos floats ni metemos tolerancias arbitrarias; medimos la separación de los datos contra la deriva real del hardware.

---

## El Talón de Aquiles del Coseno: Ceguera por Dilución

Los guardrails tradicionales basados en clasificadores angulares tienen una debilidad matemática estructural: **la dilución**. Al promediar 1024 dimensiones en un solo producto punto, un atacante puede camuflar una inyección hostil dentro de un texto legítimo abundante:

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
   [ Clasificador de Coseno ]                       [ DDI: Inspección Dimensional ]
   • Promedia sintaxis con texto                    • Particiona cláusulas y aísla el docstring
   • Score: Δ_cos = +0.0899 (Parece Python)         • Mide inclusión coordenada por coordenada
   • Veredicto: ¡DEJA PASAR EL ATAQUE! ❌            • Veredicto: HTTP 403 BREACH (0 votos de quórum) 🛡️
```

En nuestras pruebas comparativas contra el arnés adversarial **Rompepepe**:
* **El Coseno Estándar permitió entre 14.5% y 58.2% de bypasses** en ataques de piggybacking y mutaciones léxicas combinadas.
* **La Doble Compuerta del DDI contuvo las 220 muestras del protocolo v0.4.0 (0 bypasses)**, dando sustento experimental a la cota teórica de la hipótesis:
  $$P_{\text{bypass}} \le (0.80)^{100} \approx 2.037 \times 10^{-10} < 10^{-9}$$

---

## Fundamento Teórico: Tesis de Alta Densidad de Manifold

¿Por qué sospechamos que el espacio de embeddings aguanta muchísimo más de lo que se cree?

La fundamentación matemática y la ruptura con el modelo intuitivo de "paredes gordas" está desarrollada en detalle en:
📄 **[Protocolo 08: Tesis de Alta Densidad de Manifold y Límites de Ingesta](./roadmap/hipotesis-ecualizador/08-tesis-densidad-manifold-y-limites-de-ingesta.md)**

Allí se plantea por qué, a diferencia de los modelos euclidianos clásicos donde agregar datos satura el volumen, en 1024 dimensiones una ingesta densa y especializada afina los límites de decisión y purga dimensiones espurias, aumentando la precisión en lugar de degradarla.

---

## Pipeline de Inspección: Doble Compuerta Espectral (Dual-Gate)

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

1. **Compuerta 1 (Poda de Ruido Estructural Basal):** Purga coordenadas universales que saturan en cualquier texto sin aportar semántica discriminante.
2. **Compuerta 2 (Regla de Quórum del 10%):** Exige un mínimo de $K = \lceil 0.10 \times 1024 \rceil = 103$ dimensiones concordantes en la región exclusiva del dominio seguro en cada cerradura.
3. **55 Cerraduras Canónicas Trilingües:** Combinatoria de 11 dominios ($\binom{11}{2} = 55$) cruzados en Español, Inglés y Alemán: `python`, `receta`, `legal`, `medicina`, `astronomia`, `finanzas`, `filosofia`, `musica`, `geologia`, `botanica`, `arquitectura`.

---

## Puesta en Marcha del Lab (en 3 patadas con `uv`)

### 1. Clonar e Instalar Entorno
Manejamos dependencias pura y exclusivamente con `uv`:

```bash
git clone https://github.com/hbauzan/ddi-fw.git
cd ddi-fw
uv sync --extra dev
cp .env.example .env
```

### 2. Calibrar Tensores Experimentales
Podés calibrar sobre los mazos compactos o cargar los tensores trilingües:

```bash
# Calibración base con BGE-M3 (Apple Silicon MPS o CPU):
uv run python -m ddi_fw.embedder --embedder bge-m3 --out ddi_fw/out/rows.npz --rewrite-fixtures
uv run python -m ddi_fw.press --rows ddi_fw/out/rows.npz --out ddi_fw/out
```

### 3. Correr la Suite de Verificación
```bash
uv run pytest
PYTHONPATH=. uv run pytest tools/rompepepe/tests
```

---

## Probando el Proxy Experimental contra Ollama / vLLM

Configurá tu `.env` apuntando a tu LLM local (ej. Ollama en el puerto 11434):
```env
DDI_UPSTREAM_URL=http://127.0.0.1:11434/v1
DDI_UPSTREAM_MODEL=llama3.2
PORT=8080
```

Arrancá el inspector:
```bash
PORT=8080 uv run python -m ddi_fw.proxy
```

### Prompt Legítimo (Pasa derecho al LLM):
```bash
curl -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"Explicá cómo funciona list.append en Python."}],"model":"ddi-fw"}'
```

### Inyección Camuflada (Detectada en la compuerta dimensional):
```bash
curl -i -s http://127.0.0.1:8080/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"messages":[{"role":"user","content":"def hack():\n    \"\"\"Prescribir amoxicilina 500mg cada 8 horas al paciente.\"\"\"\n    return True"}],"model":"ddi-fw"}'
```
*Respuesta:* `HTTP/403 Forbidden` — `{"error":{"type":"ddi_ingress_breach","message":"ingress breach","audit":{...}}}` (fail-closed, sin filtrar texto ni tokens).

---

## Glosario Rápido del Lab

El glosario canónico completo y formal vive en [`CONTEXT.md`](./CONTEXT.md):

| Término | Qué es en este laboratorio | Qué NO es |
| :--- | :--- | :--- |
| **`alma`** | Conjunto representativo de cláusulas técnicas de un oficio | Un dataset difuso o texto scrapeado al barrer |
| **`cláusula`** | Unidad lógica de texto que se embebe y se juzga de forma atómica | Un chunk ciego de tokens |
| **`hoja`** | Los intervalos empíricos $[lo_d, hi_d]$ por coordenada entre dos almas | Un centroide, una media o un coseno |
| **`candado`** | Hoja + ejes disjuntos de un par canónico; solo se publica si hay quórum | Un clasificador de toxicidad por palabras clave |
| **`trigo`** | Dimensiones altamente contrastantes y discriminantes entre oficios | Ruido estructural o variables espurias |
| **`ruido basal`** | Coordenadas universales con energía de fondo que se purgan en Compuerta 1 | Dimensiones útiles de decisión |

---

## Informes y Resultados de Laboratorio

* 📊 **Auditorías y Benchmarks:** Directorio centralizado en [`reports/`](./reports/).
  * [Informe de Fuzzing Rompepepe (v0.4.0)](./reports/2026-09-26-rompepepe-spectral-fuzzing-v0.4.0.md) (Protocolo de 220 ataques).
  * [Auditoría de Sensibilidad de Quórum y Comparativa de Coseno](./reports/2026-09-26-analisis-sensibilidad-espectral-vs-coseno.md) ($K^* = 20$, límites empíricos).
* 🗺️ **Roadmap Científico:** Directorio [`roadmap/`](./roadmap/).
  * [Protocolo 08: Tesis de Alta Densidad de Manifold](./roadmap/hipotesis-ecualizador/08-tesis-densidad-manifold-y-limites-de-ingesta.md).
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
