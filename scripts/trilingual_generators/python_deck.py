"""Generador trilingüe para el oficio PYTHON."""

from __future__ import annotations

from scripts.trilingual_generators.base import (
    ClauseData,
    build_clauses_for_lang,
    load_extended_seeds,
)

ALMA = "python"

# --- BANCOS ES ---
SUBJECTS_ES = [
    "El administrador de contexto nativo",
    "El compilador de bytecode de CPython",
    "El recolector de basura generacional",
    "El bucle de eventos asíncrono de asyncio",
    "El despachador de métodos mediante C3 linearization",
    "El decorador de funciones de orden superior",
    "El módulo inspect en tiempo de ejecución",
    "La clase genérica del módulo typing",
    "El protocolo descriptor mediante dunder get y set",
    "La transformación de nodos en el árbol de sintaxis abstracta AST",
    "La estructura de datos deque de collections",
    "El bloqueo global del intérprete GIL",
    "La serialización de objetos mediante pickle seguro",
    "La memoria compartida a través de memoryview",
    "El operador morsa dentro de expresiones de asignación",
]

PREDICATES_ES = [
    "gestiona la liberación determinista de descriptores de archivos",
    "optimiza la pila de ejecución de marcos locales y globales",
    "detecta referencias circulares inalcanzables en el montículo",
    "coordina la ejecución de tareas concurrentes no bloqueantes",
    "resuelve jerarquías complejas de herencia múltiple",
    "inyecta validaciones previas a la invocación de funciones",
    "extrae signaturas de parámetros y metadatos de introspección",
    "valida contratos estáticos mediante comprobadores de tipos",
    "intercepta el acceso a atributos a nivel de clase e instancia",
    "reescribe sentencias antes de la generación del código objeto",
    "provee inserciones y extracciones eficientes en ambos extremos",
    "sincroniza el acceso concorrente a estructuras nativas de C",
    "preserva el estado inmutable de tuplas y conjuntos congelados",
    "permite manipular búferes binarios sin duplicación de memoria",
    "reduce evaluaciones redundantes en ramas condicionales",
]

CONTEXTS_ES = [
    "asegurando un consumo acotado de memoria en servidores de alta concurrencia",
    "garantizando la consistencia del runtime durante excepciones imprevistas",
    "siguiendo las directrices de diseño y estilo de la especificación PEP 8",
    "minimizando la sobrecarga computacional de llamadas a funciones nativas",
    "optimizando el rendimiento del despachador en microservicios backend",
    "evitando fugas de memoria por referencias cíclicas entre módulos",
    "facilitando la depuración estática en canalizaciones de integración continua",
    "asegurando interoperabilidad binaria con bibliotecas compiladas en C",
]

# --- BANCOS EN ---
SUBJECTS_EN = [
    "The CPython bytecode compiler",
    "The generational garbage collection engine",
    "The native asyncio event loop scheduler",
    "The abstract syntax tree transformation pass",
    "The method resolution order resolver using C3",
    "The runtime descriptor protocol mechanism",
    "The global interpreter lock synchronization barrier",
    "The inspect introspection module",
    "The immutable namedtuple data structure",
    "The context manager enter and exit protocol",
    "The higher-order function decorator wrapper",
    "The zero-copy memoryview binary buffer interface",
    "The typing generic protocol checker",
    "The walrus assignment expression operator",
    "The concurrent futures thread pool executor",
]

PREDICATES_EN = [
    "optimizes stack frame allocation during function calls",
    "identifies and purges cyclic object references in heap memory",
    "coordinates cooperative coroutine execution across network sockets",
    "modifies structural code representations prior to compilation",
    "linearizes complex class hierarchies without ambiguity",
    "intercepts attribute retrieval and mutation on instance variables",
    "coordinates thread execution across multi-core processor cores",
    "extracts runtime stack traces and function parameter signatures",
    "maintains compact memory representation with fixed schema",
    "guarantees deterministic cleanup of operating system file handles",
    "enforces pre-condition logging across service boundaries",
    "enables slicing of binary arrays without heap allocations",
    "verifies structural subtyping at static analysis boundaries",
    "simplifies loop termination checks within comprehension pipelines",
    "dispatches CPU-bound worker tasks across background threads",
]

CONTEXTS_EN = [
    "ensuring high-throughput stream processing under low system latency",
    "preserving strict runtime determinism in asynchronous web services",
    "complying with standard python enhancement proposal specifications",
    "minimizing memory footprint in microcontainer execution environments",
    "preventing synchronization deadlocks across concurrent worker pools",
    "enforcing robust exception handling in mission-critical pipelines",
    "accelerating scientific numerical computations with native bindings",
    "maintaining backward compatibility across interpreter release cycles",
]

# --- BANCOS DE ---
SUBJECTS_DE = [
    "Der CPython-Bytecode-Compiler",
    "Der zyklische Garbage-Collector",
    "Die asynchrone Ereignisschleife von asyncio",
    "Der native Kontextmanager mit enter und exit",
    "Die Method-Resolution-Order nach dem C3-Algorithmus",
    "Das Deskriptor-Protokoll auf Klassenebene",
    "Der globale Interpretersperrmechanismus GIL",
    "Die Transformation des abstrakten Syntaxbaums AST",
    "Das Introspektionsmodul inspect",
    "Die typsichere Dataclass-Implementierung",
    "Die funktionalen Generatoren mit yield-Anweisung",
    "Das memoryview-Objekt für Binärpuffer",
    "Der Walrus-Zuweisungsoperator in Bedingungen",
    "Die deque-Doppelenden-Warteschlange",
    "Das Typensystem mit generischen Protokollen",
]

PREDICATES_DE = [
    "optimiert die Speicherverwaltung lokaler Ausführungsrahmen",
    "bereinigt zyklische Referenzen im Objektheap zuverlässig",
    "steuert nicht-blockierende Koroutinen über Netzwerk-Sockets",
    "garantiert die deterministische Freigabe von Dateideskriptoren",
    "linearisiert mehrfache Vererbungshierarchien eindeutig",
    "fängt den lesenden und schreibenden Attributzugriff ab",
    "synchronisiert den threadübergreifenden Zugriff auf C-Strukturen",
    "modifiziert Quellcode-Strukturen vor der Bytecode-Generierung",
    "extrahiert Typsignaturen und Stack-Frames zur Laufzeit",
    "generiert automatische Konstruktor- und Vergleichsmethoden",
    "liefert Werte sequentiell ohne vollständige Listenallokation",
    "erlaubt speichereffiziente Manipulation ohne Pufferkopien",
    "erleichtert kompakte Ausdrücke in komplexen Verzweigungen",
    "ermöglicht schnelles Einfügen und Entfernen an beiden Enden",
    "prüft strukturelle Subtypen während statischer Quelltextanalysen",
]

CONTEXTS_DE = [
    "um einen minimalen Speicherverbrauch im Hochleistungsbetrieb zu sichern",
    "gemäß den Richtlinien offizieller Python Enhancement Proposals",
    "zur Vermeidung unerwarteter Laufzeitfehler bei starker Nebenläufigkeit",
    "unter Beibehaltung hoher Durchsatzraten in Web-Backends",
    "zur Gewährleistung robuster Ausnahmebehandlung in Datenpipelines",
    "während rechenintensiver Operationen auf mehrkernigen Prozessoren",
    "für eine saubere Modularisierung modularer Softwarearchitekturen",
    "zur Beschleunigung automatisierter Testläufe in Continuous-Integration-Systemen",
]


def generate_python_deck() -> list[ClauseData]:
    """Genera 500 cláusulas trilingües (167 ES, 167 EN, 166 DE) para python."""
    seeds_es = load_extended_seeds(ALMA, "es")
    seeds_en = load_extended_seeds(ALMA, "en")

    clauses_es = build_clauses_for_lang(
        ALMA, "es", 167, seeds_es, SUBJECTS_ES, PREDICATES_ES, CONTEXTS_ES
    )
    clauses_en = build_clauses_for_lang(
        ALMA, "en", 167, seeds_en, SUBJECTS_EN, PREDICATES_EN, CONTEXTS_EN
    )
    clauses_de = build_clauses_for_lang(
        ALMA, "de", 166, [], SUBJECTS_DE, PREDICATES_DE, CONTEXTS_DE
    )

    return clauses_es + clauses_en + clauses_de
