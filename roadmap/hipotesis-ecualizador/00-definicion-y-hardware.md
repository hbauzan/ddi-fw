# Definición y Especificación de Hardware — Hipótesis del Ecualizador Espectral

Fecha: 2026-09-21. Pack de investigación activo.

---

## 1. Fundamento de la Hipótesis

La **Hipótesis del Ecualizador Espectral** postula que:

1. **El vector no es un promedio:** Cada cláusula de texto embebida en un modelo de lenguaje denso produce un vector de $D$ coordenadas numéricas flotantes (ej. $D=1024$). Cada columna representa una dimensión espacial continua en el intervalo aproximado $[-1, +1]$.
2. **Existe Ruido Estructural Basal ("La Paja"):** En cualquier modelo de embedding existen dimensiones que responden con alta magnitud o con valores idénticos en cualquier texto, sin importar la temática (sesgo de entrenamiento, frecuencia de conectores, puntuación o tokens comunes). Esta paja oculta la diferenciación temática real.
3. **Existe una Firma Espectral Temática ("El Trigo"):** Al caracterizar cada corpus por separado y podar sistemáticamente el fondo común de paja, cada oficio (*alma/corpus*) exhibe un perfil distintivo de excitación de coordenadas: ciertas dimensiones tienen centros de gravedad y densidades de valor sistemáticamente diferentes de otros oficios.
4. **Separabilidad Determinista:** Ordenando las dimensiones por su contraste diferencial de valores, emerge un subconjunto nítido de coordenadas discriminantes que permite certificar la pertenencia de un texto a su dominio de forma auditable, coordenada a coordenada, sin recurrir a promedios angulares ni similitud coseno.

---

## 2. Glosario Operativo

* **Dimensión / Coordenada:** Columna $d \in [0, D-1]$ de un vector denso. *(Prohibido usar términos antropomórficos como "neurona")*.
* **Fila:** Vector numérico denso que representa una cláusula de texto única.
* **Perfil Intrínseco:** Distribución de valores (magnitud, centro de gravedad, dispersión) de las 1024 dimensiones de un único corpus analizado en soledad.
* **Paja (Fondo Común / Ruido Basal):** Conjunto de dimensiones descartadas por saturar universalmente en todos los corpus o por no presentar variación entre temas.
* **Trigo (Extracto Puro / Alma):** Conjunto de dimensiones y rangos de valores remanentes en un corpus tras descontar la paja.
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
