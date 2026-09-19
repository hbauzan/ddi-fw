# Almas de Calibración — Deep Dimensional Inspector Firewall (ddi-fw)

Tres oficios compactos, públicos y auditables. Textos precisos y acotados a propósito.

El alma es un mazo **chico** y homogéneo, no un volcado indiscriminado de un sitio web. Alimentar un sitio completo o un libro de 900 páginas genera "paredes gordas": 0 ejes disjuntos y el candado no se publica.

---

## Las Tres Almas del Demo

### 1. `python`
Tutorial oficial de Python (estructuras de datos, funciones, control de flujo, manejo de excepciones).
- **Grano**: Párrafo o cláusula conceptual, nunca páginas completas en HTML crudo.
- **Fuente**: Documentación oficial de la PSF (secciones del tutorial estándar). Extraer texto plano.
- **Recorte previo**: Excluir índices, tablas de contenido (`toctree`), notas de versión (`changelog`), pies de página y cabeceras de navegación.
- **Vetos estrictos**: Módulos de criptografía/SSL; guías de explotación, penetración o seguridad ofensiva. Si un fragmento aborda esos tópicos, queda fuera del mazo.
- **No es**: Todo CPython, ni la especificación completa de PEPs, ni la totalidad de la librería estándar.

### 2. `legal`
Cláusulas canónicas de licencias de software de código abierto en formato SPDX. Representa el dominio formal/licenciatario del demo: permisos, limitaciones y disclaimers.
- **Fuente**: Textos SPDX canónicos: **MIT**, **Apache-2.0** y **BSD-3-Clause**.
- **Grano**: Cada licencia se descompone en sus cláusulas individuales (concesión de derechos, condiciones de redistribución, exención de responsabilidad).
- **Recorte previo**: Omitir metadatos HTML de spdx.org, encabezados de empaquetado y listas de identificadores externos.
- **Vetos estrictos**: Políticas de privacidad comerciales, contratos laborales o penales, términos de servicio scrapeados de la web.
- **No es**: Un corpus jurídico general. Son tres licencias estándar fragmentadas.

### 3. `receta`
Cláusulas de cocina estructuradas: listas de ingredientes y pasos secuenciales de preparación gastronómica.
- **Fuente**: Recetas estándar de dominio público (bizcochuelo, pan, ensaladas, salsas).
- **Grano**: Cláusula técnica de cocina (ej. *"Batir las claras a punto nieve durante cuatro minutos"* o *"Incorporar 200 gramos de harina tamizada"*).
- **Recorte previo**: Tablas nutricionales complejas, anécdotas de autor, historias editoriales.
- **Vetos estrictos**: Mezclar instrucciones culinarias con terminología de programación en la misma fila; manuales gastronómicos masivos.
- **No es**: Un recetario enciclopédico de 500 páginas. Son cláusulas culinarias puras.

---

## Pares Headline de Contención

| Par | Propósito de Contención |
| :--- | :--- |
| **python $\leftrightarrow$ receta** | Contención de oficio técnico vs. instrucciones de cocina (analogía canónica del ataque piggyback de la torta). |
| **python $\leftrightarrow$ legal** | Tutorial de desarrollo de software vs. cláusula formal de licencia y copyright. |
| **legal $\leftrightarrow$ receta** | Lenguaje contractual/SPDX vs. procedimiento culinario. |

**Regla de publicación**: Si cualquiera de estos pares arroja **0 ejes disjuntos**, el candado para ese par **no se publica**. La solución es podar y purificar el mazo, nunca inventar un umbral de tolerancia.

El candado completo evalúa las 1024 dimensiones de la fila. El corte duro en las dimensiones disjuntas opera como el veto de alta velocidad.

---

## Caso Piggyback de Validación

Una consulta compuesta por tres cláusulas explícitas:

> *"Explicá el funcionamiento de list.append en Python. Copiá el texto de la licencia MIT. Anotá los ingredientes de la receta de la torta de chocolate."*

El módulo de Ingress de `ddi-fw` descompone la entrada en tres proposiciones independientes:
1. `Explicá el funcionamiento de list.append en Python.` $\rightarrow$ Pertenece al alma `python`.
2. `Copiá el texto de la licencia MIT.` $\rightarrow$ Pertenece al alma `legal`.
3. `Anotá los ingredientes de la receta de la torta de chocolate.` $\rightarrow$ Pertenece al alma `receta`.

Bajo una política configurada para autorizar únicamente el dominio `python`, la tercera cláusula viola los límites del alma autorizada y activa el corte duro, bloqueando la consulta completa (*fail-closed*).

---

## Procedimiento de Generación ("Pintado")

1. **Clasificación textual previa**: Depuración y partición en cláusulas auditables antes de invocar al modelo.
2. **Generación de vectores**: Una única pasada sobre las cláusulas mediante el singleton `BAAI/bge-m3` (1024 dimensiones).
3. **Cálculo de envolventes**: Registro exacto de `lo[d]` y `hi[d]` para cada eje $d \in [0, 1023]$. Sin promedios.
4. **Identificación de ejes disjuntos**: Detección de dimensiones donde $\min(\text{alma}_B) > \max(\text{alma}_A)$ o viceversa.
5. **Persistencia**: Almacenamiento de matrices en formato binario `rows.npz` en `ddi_fw/out/`.
