"""Carga, recorte y persistencia de los tres mazos textuales. Cero embedder."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ddi_fw.classify import classify_clause

ALMA_NAMES = ("python", "legal", "receta")
DATA_DIR = Path(__file__).resolve().parent / "data"


@dataclass(frozen=True)
class Clause:
    id: str
    text: str
    source: str


@dataclass(frozen=True)
class Mazo:
    alma: str
    clauses: tuple[Clause, ...]

    @property
    def n(self) -> int:
        return len(self.clauses)

    def texts(self) -> list[str]:
        return [clause.text for clause in self.clauses]

    def ids(self) -> list[str]:
        return [clause.id for clause in self.clauses]

    def to_json(self) -> dict[str, Any]:
        return {
            "alma": self.alma,
            "n": self.n,
            "clauses": [
                {"id": clause.id, "text": clause.text, "source": clause.source}
                for clause in self.clauses
            ],
        }


# --- Semillas curadas (grano cláusula; vetos aplicados en build_almas) --------

PYTHON_SEEDS: tuple[tuple[str, str, str], ...] = (
    (
        "python-001",
        "En Python una lista es una secuencia mutable; list.append agrega un elemento al final sin copiar la colección.",
        "psf-tutorial",
    ),
    (
        "python-002",
        "El bucle for recorre cualquier iterable: for item in items: procesa cada elemento exactamente una vez.",
        "psf-tutorial",
    ),
    (
        "python-003",
        "Una función se declara con def y puede devolver un valor con return; los parámetros pueden tener valores por defecto.",
        "psf-tutorial",
    ),
    (
        "python-004",
        "Las excepciones se manejan con try, except y finally; Exception es la clase base habitual de los errores recuperables.",
        "psf-tutorial",
    ),
    (
        "python-005",
        "Un diccionario asocia claves inmutables a valores; dict.get(clave, default) evita KeyError cuando la clave no existe.",
        "psf-tutorial",
    ),
    (
        "python-006",
        "El slicing xs[start:stop:step] produce una lista nueva; xs[::-1] invierte la secuencia sin mutar el original.",
        "psf-tutorial",
    ),
    (
        "python-007",
        "import math carga un módulo de la biblioteca estándar; from math import sqrt importa un nombre al espacio local.",
        "psf-tutorial",
    ),
    (
        "python-008",
        "Una tupla es una secuencia inmutable; se usa para registros fijos y para devolver múltiples valores desde una función.",
        "psf-tutorial",
    ),
    (
        "python-009",
        "En Python, if, elif y else eligen una rama de control de flujo según una condición booleana evaluada de arriba hacia abajo.",
        "psf-tutorial",
    ),
    (
        "python-010",
        "while repite un bloque mientras la condición sea verdadera; un break sale del bucle y continue salta a la siguiente iteración.",
        "psf-tutorial",
    ),
    (
        "python-011",
        "En Python los conjuntos set eliminan duplicados y soportan unión, intersección y diferencia en tiempo promedio constante.",
        "psf-tutorial",
    ),
    (
        "python-012",
        'Una f-string de Python interpola expresiones dentro de un literal: f"{nombre}={valor}" produce un str formateado.',
        "psf-tutorial",
    ),
    (
        "python-013",
        "None es el objeto nulo de Python; una función sin return explícito devuelve None.",
        "psf-tutorial",
    ),
    (
        "python-014",
        "En Python class define un tipo; __init__ inicializa la instancia y self referencia al objeto receptor.",
        "psf-tutorial",
    ),
    (
        "python-015",
        "list comprehension [x * 2 for x in xs if x > 0] construye una lista nueva filtrando y transformando en una sola expresión.",
        "psf-tutorial",
    ),
    (
        "python-016",
        "raise ValueError('fuera de rango') lanza una excepción; el llamador puede atraparla con except ValueError.",
        "psf-tutorial",
    ),
    (
        "python-017",
        "Los argumentos *args y **kwargs recogen posicionales extras y palabras clave extras en la firma de la función.",
        "psf-tutorial",
    ),
    (
        "python-018",
        "En Python enumerate(xs) produce pares (índice, valor); zip(a, b) recorre dos iterables en paralelo hasta el más corto.",
        "psf-tutorial",
    ),
    (
        "python-019",
        "En Python, with open(path, encoding='utf-8') as handle: lee un archivo de texto y cierra el descriptor aunque ocurra una excepción.",
        "psf-tutorial",
    ),
    (
        "python-020",
        "En Python isinstance(obj, list) comprueba el tipo en tiempo de ejecución; type(obj) is list es más estricto y suele evitarse.",
        "psf-tutorial",
    ),
    (
        "python-021",
        "Un generador de Python usa yield para producir valores perezosos; next(gen) obtiene el siguiente elemento o lanza StopIteration.",
        "psf-tutorial",
    ),
    (
        "python-022",
        "sorted(xs, key=len, reverse=True) devuelve una lista nueva ordenada; xs.sort() ordena la lista in-place y retorna None.",
        "psf-tutorial",
    ),
    (
        "python-veto-ssl",
        "El módulo ssl envuelve un socket con TLS y expone certificados; no pertenece al tutorial básico de estructuras de datos.",
        "veto-sample",
    ),
    (
        "python-lomo-toc",
        "Table of contents: 1. Introduction 2. Changelog 3. toctree next previous.",
        "veto-sample",
    ),
)

LEGAL_SEEDS: tuple[tuple[str, str, str], ...] = (
    (
        "legal-mit-001",
        'Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.',
        "spdx-MIT",
    ),
    (
        "legal-mit-002",
        "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.",
        "spdx-MIT",
    ),
    (
        "legal-mit-003",
        'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.',
        "spdx-MIT",
    ),
    (
        "legal-mit-004",
        "IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.",
        "spdx-MIT",
    ),
    (
        "legal-apache-001",
        "Apache License Version 2.0: you must give any other recipients of the Work or Derivative Works a copy of this License.",
        "spdx-Apache-2.0",
    ),
    (
        "legal-apache-002",
        "You must cause any modified files to carry prominent notices stating that You changed the files and retain all copyright, patent, trademark, and attribution notices.",
        "spdx-Apache-2.0",
    ),
    (
        "legal-apache-003",
        "If the Work includes a NOTICE text file, any Derivative Works that You distribute must include a readable copy of the attribution notices contained within such NOTICE file.",
        "spdx-Apache-2.0",
    ),
    (
        "legal-apache-004",
        "Subject to the terms and conditions of this License, each Contributor hereby grants to You a perpetual, worldwide, non-exclusive, no-charge, royalty-free, irrevocable copyright license to reproduce the Work.",
        "spdx-Apache-2.0",
    ),
    (
        "legal-apache-005",
        'THIS WORK IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including without limitation any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE.',
        "spdx-Apache-2.0",
    ),
    (
        "legal-apache-006",
        "Unless required by applicable law or agreed to in writing, Licensor provides no disclaimer of liability except as required: You are solely responsible for determining the appropriateness of using or redistributing the Work.",
        "spdx-Apache-2.0",
    ),
    (
        "legal-bsd-001",
        "Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met.",
        "spdx-BSD-3-Clause",
    ),
    (
        "legal-bsd-002",
        "Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.",
        "spdx-BSD-3-Clause",
    ),
    (
        "legal-bsd-003",
        "Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.",
        "spdx-BSD-3-Clause",
    ),
    (
        "legal-bsd-004",
        "Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.",
        "spdx-BSD-3-Clause",
    ),
    (
        "legal-bsd-005",
        'THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.',
        "spdx-BSD-3-Clause",
    ),
    (
        "legal-bsd-006",
        "IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES ARISING FROM THE USE OF THIS SOFTWARE.",
        "spdx-BSD-3-Clause",
    ),
    (
        "legal-spdx-001",
        "An SPDX license identifier such as MIT, Apache-2.0 or BSD-3-Clause names a canonical license text and its standard disclaimer.",
        "spdx-meta",
    ),
    (
        "legal-spdx-002",
        "The grant of rights under these licenses is a copyright license to copy, modify and redistribute, subject to the stated conditions.",
        "spdx-meta",
    ),
    (
        "legal-veto-privacy",
        "This privacy policy explains how we collect cookies and sell personal data under our commercial terms of service.",
        "veto-sample",
    ),
    (
        "legal-lomo-html",
        "SPDX license list | table of contents | previous next | website footer navigation.",
        "veto-sample",
    ),
)

RECETA_SEEDS: tuple[tuple[str, str, str], ...] = (
    (
        "receta-001",
        "Batir las claras a punto nieve durante cuatro minutos hasta que sostengan pico firme.",
        "dominio-publico",
    ),
    (
        "receta-002",
        "Incorporar 200 gramos de harina tamizada en tres tandas, envolviendo la masa con una espátula.",
        "dominio-publico",
    ),
    (
        "receta-003",
        "Precalentar el horno a 180 grados y hornear el bizcochuelo durante treinta y cinco minutos.",
        "dominio-publico",
    ),
    (
        "receta-004",
        "Disolver 7 gramos de levadura seca en agua tibia con una cucharadita de azúcar y esperar diez minutos.",
        "dominio-publico",
    ),
    (
        "receta-005",
        "Amasar la masa de pan hasta que el gluten esté elástico y no se rompa al estirar una membrana fina.",
        "dominio-publico",
    ),
    (
        "receta-006",
        "Dejar levar la masa en un bol aceitado hasta que duplique su volumen, cubierto con un paño húmedo.",
        "dominio-publico",
    ),
    (
        "receta-007",
        "Saltear la cebolla en aceite de oliva a fuego medio hasta que quede transparente, sin tomar color oscuro.",
        "dominio-publico",
    ),
    (
        "receta-008",
        "Reducir la salsa de tomate a fuego bajo durante veinte minutos, removiendo para que no se pegue al fondo.",
        "dominio-publico",
    ),
    (
        "receta-009",
        "Cortar el tomate y la lechuga en juliana; aliñar la ensalada con aceite de oliva, sal y un chorro de vinagre.",
        "dominio-publico",
    ),
    (
        "receta-010",
        "Derretir 80 gramos de manteca e integrarlas a las yemas batidas con 150 gramos de azúcar.",
        "dominio-publico",
    ),
    (
        "receta-011",
        "Engrasar el molde con manteca y enharinarlo antes de volcar la masa del bizcochuelo.",
        "dominio-publico",
    ),
    # receta-012 (almíbar / hebra fina) se podó en vivo: ensanchaba la hoja
    # y dejaba python↔receta sin ejes disjuntos. No reintroducir.
    (
        "receta-013",
        "Tostar el ajo en la sartén diez segundos y apagar el fuego antes de agregar el perejil picado a la salsa.",
        "dominio-publico",
    ),
    (
        "receta-014",
        "Reservar las claras y las yemas en bowls separados; la yema liga la masa y la clara airea el bizcochuelo.",
        "dominio-publico",
    ),
    (
        "receta-015",
        "Hornear el pan a 220 grados los primeros diez minutos y bajar a 190 hasta que suene hueco al golpear la base.",
        "dominio-publico",
    ),
    (
        "receta-016",
        "Pesar 250 gramos de harina, 8 gramos de sal y 40 mililitros de aceite de oliva para la masa de pizza.",
        "dominio-publico",
    ),
    (
        "receta-017",
        "Emulsionar la salsa vinagreta batiendo mostaza, vinagre y aceite de oliva en un hilo fino.",
        "dominio-publico",
    ),
    (
        "receta-018",
        "Dejar reposar la masa de tarta treinta minutos en la heladera antes de estirarla con el palo.",
        "dominio-publico",
    ),
    (
        "receta-veto-mix",
        "Usá list.append para agregar 200 gramos de harina a la lista de ingredientes en Python.",
        "veto-sample",
    ),
    (
        "receta-lomo-nutri",
        "Tabla nutricional: calorías por porción 320, información nutricional completa en el recetario.",
        "veto-sample",
    ),
)

SEEDS: dict[str, tuple[tuple[str, str, str], ...]] = {
    "python": PYTHON_SEEDS,
    "legal": LEGAL_SEEDS,
    "receta": RECETA_SEEDS,
}


def _clause_from_seed(seed: tuple[str, str, str]) -> Clause:
    return Clause(id=seed[0], text=seed[1], source=seed[2])


def filter_mazo(alma: str, seeds: tuple[tuple[str, str, str], ...]) -> Mazo:
    kept: list[Clause] = []
    for seed in seeds:
        clause = _clause_from_seed(seed)
        verdict = classify_clause(clause.text)
        if verdict.label != alma:
            continue
        kept.append(clause)
    if not kept:
        raise ValueError(f"mazo vacío tras recorte y veto: {alma}")
    return Mazo(alma=alma, clauses=tuple(kept))


def build_almas(data_dir: Path | None = None) -> dict[str, Mazo]:
    """Recorta, veta y serializa los tres mazos en JSON auditable."""
    target = data_dir or DATA_DIR
    target.mkdir(parents=True, exist_ok=True)
    mazos: dict[str, Mazo] = {}
    for alma in ALMA_NAMES:
        mazo = filter_mazo(alma, SEEDS[alma])
        path = target / f"{alma}.json"
        path.write_text(
            json.dumps(mazo.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        mazos[alma] = mazo
    return mazos


def load_mazo(alma: str, data_dir: Path | None = None) -> Mazo:
    path = (data_dir or DATA_DIR) / f"{alma}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("alma") != alma:
        raise ValueError(f"alma inconsistente en {path}: {payload.get('alma')}")
    clauses = tuple(
        Clause(id=row["id"], text=row["text"], source=row["source"]) for row in payload["clauses"]
    )
    mazo = Mazo(alma=alma, clauses=clauses)
    if mazo.n != payload.get("n"):
        raise ValueError(f"n inconsistente en {path}: json={payload.get('n')} real={mazo.n}")
    if mazo.n == 0:
        raise ValueError(f"mazo vacío: {path}")
    return mazo


def load_almas(data_dir: Path | None = None) -> dict[str, Mazo]:
    return {alma: load_mazo(alma, data_dir) for alma in ALMA_NAMES}


def drop_clauses(mazo: Mazo, drop_ids: set[str]) -> Mazo:
    kept = tuple(clause for clause in mazo.clauses if clause.id not in drop_ids)
    if not kept:
        raise ValueError(f"poda total del mazo {mazo.alma}")
    return Mazo(alma=mazo.alma, clauses=kept)


def write_mazo(mazo: Mazo, data_dir: Path | None = None) -> Path:
    target = data_dir or DATA_DIR
    target.mkdir(parents=True, exist_ok=True)
    path = target / f"{mazo.alma}.json"
    path.write_text(
        json.dumps(mazo.to_json(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Pinta y serializa los mazos textuales de ddi-fw.")
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR)
    args = parser.parse_args(argv)
    mazos = build_almas(args.data_dir)
    for alma, mazo in mazos.items():
        print(f"{alma}\tn={mazo.n}\t{args.data_dir / f'{alma}.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
