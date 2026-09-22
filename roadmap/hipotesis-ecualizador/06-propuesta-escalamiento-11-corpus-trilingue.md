# Propuesta de Escalamiento: 11 Corpus Trilingües y Análisis de Volumen

**Documento:** Protocolo 06 / Propuesta de Escalamiento  
**Fecha:** 2026-09-21  
**Estado:** `EN STANDBY` (Listo para reanudar tras decisión de volumen)  
**Referencia:** Versión v0.3.0 de `ddi-fw`

---

## 1. Resumen de la Propuesta

Se analizó la expansión del dataset y del pipeline del **Ecualizador Espectral** a **11 corpus canónicos** de alta pureza técnica, incorporando **Alemán (DE)** junto a **Español (ES)** e **Inglés (EN)**, para evaluar el Quórum del 10% y la norma de 6 decimales bajo condiciones multilingües exhaustivas.

---

## 2. Los 11 Dominios Técnicos Propuestos

Para garantizar que el índice Jaccard léxico entre cualquier par se mantenga estrictamente en $J < 0.05$, se preservan los 5 oficios existentes y se seleccionan 6 dominios técnicos complementarios sin solapamiento semántico:

1. **`python`** (Existente): Programación, tipos, introspección, metaprogramación, algoritmos y runtime.
2. **`receta`** (Existente): Gastronomía técnica, pastelería, química culinaria, fermentación y emulsiones.
3. **`legal`** (Existente): Contratos, licencias de propiedad intelectual, derecho procesal y responsabilidad civil.
4. **`medicina`** (Existente): Fisiología clínica, farmacología, anatomía patológica, cardiología y diagnóstico.
5. **`astronomia`** (Existente): Astrofísica estelar, espectrometría, cosmología, mecánica orbital y radioastronomía.
6. **`finanzas`** (Nuevo): Mercados de capitales, renta fija/variable, derivados (swaps, opciones), Basilea III y política monetaria.
7. **`filosofia`** (Nuevo): Epistemología, ontología metafísica, ética kantiana, dialéctica, fenomenología y lógica modal.
8. **`musica`** (Nuevo): Armonía tonal clásica, contrapunto modal, polifonía, acústica instrumental, síncopas y escalas.
9. **`geologia`** (Nuevo): Tectónica de placas, mineralogía silicatada, estratigrafía sedimentaria, petrología y sismología.
10. **`botanica`** (Nuevo): Fisiología vegetal, fotosíntesis C3/C4/CAM, xilema/floema, fitopatología y taxonomía.
11. **`arquitectura`** (Nuevo): Cálculo estructural, hormigón armado, vigas isostáticas, cimentaciones y física de la edificación.

---

## 3. Incorporación del Idioma Alemán (DE)

* **Compatibilidad de Motor:** El modelo base `BAAI/bge-m3` es intrínsecamente multilingüe (>100 idiomas con espacio latente unificado) y cuenta con soporte de primer nivel para Alemán.
* **Aislamiento del "Concepto Puro":** Al distribuir las cláusulas de cada oficio en Español, Inglés y Alemán:
  * Si una coordenada se activa por el oficio (ej. *compilación*, *glaseado*, *jurisdicción*, *fotosíntesis*), responderá en los 3 idiomas simultáneamente (Trigo Puro).
  * Las peculiaridades sintácticas o morfológicas de un idioma particular serán filtradas automáticamente como **Paja Estructural** por el Criterio B.
* **Inmunidad contra Jailbreaks Multilingües:** Neutraliza inyecciones hostiles o ataques de evasión formulados en idiomas secundarios.

---

## 4. Rol de la Herramienta `rompepepe`

Se clarificó la separación de responsabilidades dentro de la arquitectura:
* **Calibración y Ecualización:** **No** utiliza `rompepepe`. Se ejecuta con el pipeline nativo de `ddi_fw` (`generate_decks`, `embedder`, `ecualizador.*`).
* **Fuzzing Adversarial Post-Publicación:** `rompepepe` ([`tools/rompepepe/`](../../tools/rompepepe/)) interviene **después** de calibrar y publicar candados, disparando ataques adaptativos, inyecciones de frontera y mezclas de temas (*piggybacks*) para intentar quebrar el Quórum del 10%.

---

## 5. Análisis del Volumen de Cláusulas y la Invariante Canónica

> [!WARNING]
> **Invariante Canónica de Diseño:** *"Mazos chicos y estereotipados: paredes gordas matan la disyunción."* ([`CONTEXT.md`](../../CONTEXT.md))

En DDI Firewall, los dominios son cajas hiperdimensionales $[lo, hi]$. Un exceso desmedido de cláusulas por tema ensancha los intervalos de las coordenadas en todas direcciones, haciendo que las cajas crezcan hasta tocarse ($gap \le 0$), lo que provocaría el **colapso de los ejes disjuntos a cero**.

### Comparativa de Opciones de Escalamiento

| Métrica | Opción A (500 por Idioma) | Opción B (Punto Dulce Recomendado) |
| :--- | :---: | :---: |
| **Cláusulas por Idioma** | 500 ES / 500 EN / 500 DE | **~165 ES / 165 EN / 165 DE** |
| **Cláusulas por Oficio** | **1.500 cláusulas** | **~500 cláusulas** |
| **Total Global (11 temas)** | **16.500 cláusulas** | **~5.500 cláusulas** |
| **Volumen de Texto Estimado** | $\approx 330.000$ palabras | $\approx 105.000$ palabras |
| **Tiempo de Inferencia (Apple M4)** | $\approx 8,7\text{ minutos}$ continuos de GPU | $\approx 2,8\text{ minutos}$ |
| **Pares Combinatorios** | 55 pares ($\binom{11}{2}$) | 55 pares ($\binom{11}{2}$) |
| **Riesgo de "Engorde de Cajas"** | **Muy Alto** (ensanchamiento excesivo de $[lo, hi]$) | **Bajo / Óptimo** (cajas concentradas) |
| **Aislamiento Léxico (Jaccard)** | Muy difícil de mantener $J < 0.05$ | **Garantizado $J < 0.05$** |
| **Error Estándar de la Media ($\sigma/\sqrt{N}$)** | $\approx 0.0006$ | $\approx 0.0011$ (suficiente para certificar 6 decimales) |

---

## 6. Próximos Pasos al Retomar

1. **Decisión del Usuario:** Confirmar si se procede con la **Opción B** (~500 cláusulas por mazo, ~165 por idioma = ~5.500 cláusulas) o con la **Opción A** (1.500 por mazo = 16.500 cláusulas).
2. **Generación de Mazos:** Implementar el script generador trilingüe en `scripts/generate_11_trilingual_decks.py`.
3. **Calibración:** Ejecutar inferencia en BGE-M3 y correr el pipeline completo del Ecualizador (fases 1 a 4).
4. **Verificación:** Correr suite de tests de disyunción y tests de stress con `rompepepe`.
