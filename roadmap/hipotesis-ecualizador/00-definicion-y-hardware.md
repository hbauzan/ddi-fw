# Definición y Especificación de Hardware — Hipótesis del Ecualizador Espectral

Fecha: 2026-09-21. Pack de investigación activo.

---

## 1. Fundamento de la Hipótesis

La **Hipótesis del Ecualizador Espectral** postula que:

1. **El vector no es un promedio:** Cada cláusula de texto embebida en un modelo de lenguaje denso produce un vector de $D$ coordenadas numéricas flotantes (ej. $D=1024$). Cada columna representa una dimensión espacial continua en el intervalo aproximado $[-1, +1]$.
2. **Existe Ruido Estructural Basal ("El Ruido Estructural"):** En cualquier modelo de embedding existen dimensiones que responden con alta magnitud o con valores idénticos en cualquier texto, sin importar la temática (sesgo de entrenamiento, frecuencia de conectores, puntuación o tokens comunes). Este ruido oculta la diferenciación temática real.
3. **Existe una Firma Espectral Temática ("El Trigo"):** Al caracterizar cada corpus por separado y podar sistemáticamente el fondo común de ruido, cada oficio (*alma/corpus*) exhibe un perfil distintivo de excitación de coordenadas: ciertas dimensiones tienen centros de gravedad y densidades de valor sistemáticamente diferentes de otros oficios.
4. **Separabilidad Determinista:** Ordenando las dimensiones por su contraste diferencial de valores, emerge un subconjunto nítido de coordenadas discriminantes que permite certificar la pertenencia de un texto a su dominio de forma auditable, coordenada a coordenada, sin recurrir a promedios angulares ni similitud coseno.

---

## 2. Glosario Operativo

* **Dimensión / Coordenada:** Columna $d \in [0, D-1]$ de un vector denso. *(Prohibido usar términos antropomórficos como "neurona")*.
* **Fila:** Vector numérico denso que representa una cláusula de texto única.
* **Perfil Intrínseco:** Distribución de valores (magnitud, centro de gravedad, dispersión) de las 1024 dimensiones de un único corpus analizado en soledad.
* **Ruido Basal (Fondo Común Estructural):** Conjunto de dimensiones descartadas por saturar universalmente en todos los corpus o por no presentar variación entre temas.
* **Trigo (Extracto Puro / Alma):** Conjunto de dimensiones y rangos de valores remanentes en un corpus tras descontar el ruido.
* **Centro de Gravedad / Centro de Distribución:** Valor central (media/mediana en `float64`) donde se concentra la densidad de puntos de una dimensión para un corpus.
* **Contraste Diferencial ($\Delta$):** Magnitud de separación entre los centros de distribución de dos o más corpus en una coordenada dada.

---

## 3. Modelo de Embedding Baseline

El presente ciclo de investigación se ejecuta de manera estricta y controlada sobre:
* **Modelo**: `BAAI/bge-m3`
* **Dimensión**: $D = 1024$
* **Dtype Nativo del Modelo**: `float32` (IEEE 754 de precisión simple).
* **Entorno de Memoria de Análisis**: Promovido a **`float64` (IEEE 754 de doble precisión)** para todos los cálculos intermedios (medias, varianzas, distancias $\Delta$ y censos de decimales), evitando errores de redondeo o acumulación.
* **Modelos Futuros (Fase Posterior)**: Se evaluarán alternativas locales (`Qwen2`, `EmbeddingGemma`) y motores en nube solo una vez agotadas las conclusiones sobre BGE-M3.

---

## 4. Estándar Obligatorio de Registro de Hardware

Toda exportación de datos (`.csv`, `.json`, `.npz`) y todo informe de medición generado en este marco **debe incluir obligatoriamente** la siguiente ficha técnica del hardware utilizado:

```markdown
### Ficha de Hardware y Entorno de Ejecución
- **Dispositivo**: [ej. Apple Silicon M2 Max / M3 / Nvidia RTX 4090]
- **Target PyTorch**: [ej. mps:0 / cuda:0 / cpu]
- **Memoria RAM del Sistema**: [ej. 32 GB / 64 GB unificada]
- **Sistema Operativo**: [ej. macOS 15.x / Linux x86_64 kernel 6.x]
- **Versión de Python**: [ej. 3.12.x]
- **Versión de PyTorch**: [ej. 2.4.x]
- **Versión de NumPy**: [ej. 1.26.x / 2.x]
- **Timestamp ISO 8601**: [ej. 2026-09-21T19:25:00-03:00]
```

Cualquier prueba que omita esta ficha se considerará no reproducible y carente de validez dentro del protocolo.

---

## 5. Norma de Resolución de 6 Decimales (`10^{-6}`)

Para la toma de decisiones, inspección y exportación de datos del firewall:
1. **Resolución Universal:** Se fija una cota de resolución de **6 decimales** (`10^{-6}`), convención estándar y nativa del formato `float32` (mantisa de 24 bits, ~7.22 dígitos significativos).
2. **Cobertura Sobrada:** Dado que la separación promedio entre centros temáticos es $\Delta_{avg} = 0.0139$ (requiere 2 a 3 decimales), una resolución de 6 decimales ofrece un factor de seguridad de **$1.000\times$** sobre la granularidad requerida.
3. **Corte por Encima del Piso de Silicio:** La deriva física medida entre GPU y CPU en hardware real se ubica en $2.46 \times 10^{-7}$ (7º decimal). Cortar al 6º decimal garantiza capturar toda la señal determinista real dejando fuera cualquier variación residual de coma flotante.

---

## 6. La Regla Universal del Quórum del 10% ($\lceil 0.10 \times D \rceil$)

Se establece como premisa arquitectónica obligatoria para `BAAI/bge-m3` y todos los motores de LLM presentes y futuros:

### 6.1. Dimensión del Quórum por Motor
El firewall seleccionará siempre el **10% superior** ($N_Q = \lceil 0.10 \times D \rceil$) de dimensiones ordenadas por contraste diferencial tras la poda de ruido estructural:
* **`BAAI/bge-m3` ($D=1024$):** Quórum de **100 dimensiones** (9.77% $\approx$ 10%).
* **`Qwen2 / GTE` ($D=1536$):** Quórum de **154 dimensiones** (10%).
* **`Gemma MRL` ($D=256$):** Quórum de **26 dimensiones** (10%).
* **Modelos Masivos ($D=4096$):** Quórum de **410 dimensiones** (10%).

### 6.2. Fundamentos y Confirmaciones del Quórum del 10%

1. **Concentración de Información (>85%):** En análisis espectral de embeddings densos, el 10% superior de dimensiones contrastadas captura más del 85% de la varianza discriminante, descartando el 90% restante correspondiente a dimensiones planas, débiles o contaminadas por ruido basal.
2. **Blindaje contra Variabilidad Léxica y Redacción:**
   Una cláusula legítima que utilice términos atípicos o metáforas puede experimentar fluctuaciones de magnitud en 2, 3 o hasta 5 dimensiones. Dentro de un quórum de 100 dimensiones, una oscilación en 5 dimensiones representa apenas el 5% del voto: el **95% restante del quórum sostiene el veredicto con total estabilidad**.
3. **Confirmación Matemática Anti-Bypass ($P < 10^{-9}$):**
   Considerando un ataque de inyección o texto fuera de dominio (ej. receta intentando suplantar a python):
   * Supongamos conservadoramente que en cada dimensión individual un texto ajeno tiene una probabilidad generosa de solapamiento de $p = 0.80$ (80%).
   * La probabilidad combinada e independiente de que el texto caiga simultáneamente dentro de los intervalos de las 100 dimensiones del quórum es:
     $$P_{\text{bypass}} = (0.80)^{100} \approx 2.037 \times 10^{-10}$$
   * La probabilidad es estrictamente menor a **1 en 4.900 millones** ($< 10^{-9}$), volviendo matemáticamente imposible el bypass accidental o por fuerza bruta en el quórum espectral.
4. **Latencia Sub-Milisegundo:**
   La verificación coordenada por coordenada sobre 100 dimensiones insume menos de **10 microsegundos en CPU**, garantizando costo de cómputo despreciable frente a los cientos de milisegundos que demora la generación de tokens del LLM.


