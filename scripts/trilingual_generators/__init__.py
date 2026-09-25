"""Paquete de generadores para los 11 mazos trilingües (Opción B)."""

from __future__ import annotations

from scripts.trilingual_generators.arquitectura_deck import generate_arquitectura_deck
from scripts.trilingual_generators.astronomia_deck import generate_astronomia_deck
from scripts.trilingual_generators.botanica_deck import generate_botanica_deck
from scripts.trilingual_generators.filosofia_deck import generate_filosofia_deck
from scripts.trilingual_generators.finanzas_deck import generate_finanzas_deck
from scripts.trilingual_generators.geologia_deck import generate_geologia_deck
from scripts.trilingual_generators.legal_deck import generate_legal_deck
from scripts.trilingual_generators.medicina_deck import generate_medicina_deck
from scripts.trilingual_generators.musica_deck import generate_musica_deck
from scripts.trilingual_generators.python_deck import generate_python_deck
from scripts.trilingual_generators.receta_deck import generate_receta_deck

DECK_GENERATORS = {
    "python": generate_python_deck,
    "receta": generate_receta_deck,
    "legal": generate_legal_deck,
    "medicina": generate_medicina_deck,
    "astronomia": generate_astronomia_deck,
    "finanzas": generate_finanzas_deck,
    "filosofia": generate_filosofia_deck,
    "musica": generate_musica_deck,
    "geologia": generate_geologia_deck,
    "botanica": generate_botanica_deck,
    "arquitectura": generate_arquitectura_deck,
}

ALMAS_11 = tuple(DECK_GENERATORS.keys())
