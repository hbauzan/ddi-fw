# Insumo y Análisis: Hipótesis "Deletor" (Ecualizador Espectral Dimensional)

**Autor/Origen**: Héctor (`deletor`) — Insumo de análisis y debate arquitectónico.
**Fecha**: 2026-09-19
**Estado**: **Estacionada.** No es la etapa activa de `main`.

> **NOTA PARA EL AGENTE QUE ABRA ESTA RAMA**
>
> Rama: `feat/hipotesis-deletor`. Un solo commit encima del tag `v0.1.0-bge-m3-baseline`. Este archivo es todo el delta.
>
> **Qué está haciendo `main` ahora (2026-09-19):**
> 1. El pack D01–D07 / BGE-M3 quedó archivado en `roadmap/archive/v0.1-bge-m3/` y sellado en el tag `v0.1.0-bge-m3-baseline`. No reabrir esos tickets ni “mejorar” los números de BGE.
> 2. Lo siguiente es **repetir los mismos tests live** con `nomic-ai/nomic-embed-text-v1.5`, `google/embeddinggemma-300m` y `Alibaba-NLP/gte-Qwen2-1.5B-instruct`, sin pisar mazos ni evidencia BGE.
> 3. `feat/spectral-deletor` quedó mezclada (hipótesis + mudanza de tickets). Esta rama es el hogar limpio del Deletor.
>
> **Prohibido** implementar el ecualizador espectral mientras corre la campaña multi-motor. **Prohibido** mergear esta rama a `main` a ciegas: resucitaría `roadmap/tickets/`. Cuando se retome, portar solo este archivo.

---

## 1. Planteo e Intuición de la Hipótesis

El diseño fundacional de `ddi-fw` (v0.1.0) concentra la decisión del corte duro exclusivamente en los **ejes disjuntos** ($gap > 0$, donde los intervalos no se tocan en absoluto). Para el par `python_receta`, este criterio depende de **1 única dimensión** (el eje `891`).

La **Hipótesis Deletor** plantea:
> *"El eje disjunto es un hallazgo hermoso y la 'dimensión diferencial' que marca el abismo más claro. Sin embargo, no debemos descansar todo el control en una sola dimensión cuando el propio censo revela que existen entre **199 y 270 dimensiones** que se mueven exclusivamente cuando hablamos de Python (`solo_a`), y entre **131 y 193 dimensiones** que solo se activan cuando hablamos de Receta (`solo_b`).
> Al igual que un **ecualizador gráfico** separa y escucha rangos específicos de frecuencia, un texto debería evaluarse por la masa de bandas que excita de forma coordinada."*

---

## 2. Desglose Técnico: ¿Por qué existe un rango y no un número fijo?

Durante la discusión se analizó por qué el censo de [`press.json`](../ddi_fw/out/press.json) arroja un rango (`199 a 270`) en vez de una constante exacta (ej. "exactamente 199 dimensiones fijas"):

1. **Representación distribuida y polisemántica**:
   - En un modelo denso (BGE-M3, 1024D), las dimensiones no son canales ortogonales puros de una FFT (donde una frecuencia siempre corresponde a un tono).
   - Cada dimensión es un "acorde" entrelazado que codifica simultáneamente sintaxis, vocabulario, morfología, nivel de abstracción y relaciones contextuales.
2. **Variabilidad por cláusula**:
   - Una oración como `"import math carga un módulo"` excita **199** dimensiones exclusivas de Python.
   - Una oración como `"Las excepciones se manejan con try y except"` excita **270** dimensiones exclusivas.
   - Cada frase del oficio toca una constelación particular de teclas dentro del piano de 1024 dimensiones.
3. **Masa de solapamiento (`ambas`)**:
   - Entre 750 y 890 dimensiones comparten rangos entre ambos dominios porque reflejan estructuras comunes del lenguaje natural humano (conectores, puntuación, longitudes, gramática).

---

## 3. Arquitectura Propuesta: Defensa en Dos Niveles (La Guillotina + El Ecualizador)

La hipótesis no descarta el eje disjunto, sino que propone complementar la decisión binaria con la **firma espectral de votos**:

```
                              VECTOR DENSO (1024D)
                                       │
            ┌──────────────────────────┴──────────────────────────┐
            ▼                                                     ▼
    NIVEL 1: LA GUILLOTINA                                NIVEL 2: EL ECUALIZADOR
 (Ejes Disjuntos / Dimensión Diferencial)              (Quórum Espectral de Votos)
            │                                                     │
   ¿Cae en el abismo del eje 891                          ¿Qué masa de dimensiones
     del lado contrario?                                    exclusivas se activa?
            │                                                     │
     SÍ ──► 403 BREACH INMEDIATO                          solo_a vs solo_b vs ambas
            │                                                     │
     NO ──► Pasa a validar coherencia             Firma espectral: si solo_b >> solo_a
            con el resto del espectro.             incluso sin tocar el eje 891 ──► BREACH
```

### Ventajas de la Hipótesis frente a los límites actuales:
- **Resiliencia ante la fragilidad de 1 solo eje**: Si el mazo se amplía y una cláusula puente elimina el único eje disjunto (haciendo que los disjuntos caigan a 0), el sistema hoy se niega a publicar. Con el modelo espectral, la asimetría masiva de votos (ej. 200 a 0) permite sostener un veredicto de contención robusto sin inventar un gap artificial.
- **Detección de mezclas sutiles**: Cláusulas híbridas o redactadas con astucia que logren cruzar por la orilla del eje 891 no podrán ocultar la excitación anómala de 150 dimensiones del dominio vedado.

---

## 4. Estado de los Componentes en Código

El código actual de `ddi-fw` ya cuenta con los cimientos para implementar esta hipótesis sin reescribir el motor:

1. **Bitácora de votos completa**: [`corte.py`](../ddi_fw/corte.py) ya genera `recuento_votos()` computando los 4 estados (`solo_a`, `solo_b`, `ambas`, `ninguna`) en las 1024 dimensiones.
2. **Persistencia en auditoría**: [`ingress.py`](../ddi_fw/ingress.py) ya incluye `vote_counts` dentro del objeto `Decision` de cada cláusula.
3. **Censo en Press**: [`press.py`](../ddi_fw/press.py) ya calcula los extremos `lo` y `hi` de cada familia para esos votos.

---

## 5. Próximos Pasos para la Ola Siguiente

- [ ] Definir la métrica de **Ratio de Asimetría Espectral**: $R = \frac{solo\_a}{solo\_a + solo\_b}$.
- [ ] Establecer si el Quórum Espectral actúa como condición necesaria o de refuerzo ante la ausencia de ejes disjuntos.
- [ ] Experimentar con la estabilidad de las dimensiones exclusivas al ampliar el tamaño de las almas ($N > 50$).
