#!/usr/bin/env python3
"""Cinco inferencias en frío del mismo texto y varianza máxima bit a bit.

Cada corrida es un intérprete nuevo: carga el embedder, embebe una vez y termina.
Los vectores se pasan como ``.npy`` float32. No hay JSON de coordenadas.

Varianza poblacional de cada bit IEEE-754 de cada coordenada, sobre ``n`` corridas
donde ese bit vale 1 en ``k`` de ellas::

    var = k * (n - k) / n**2

Determinismo absoluto: el máximo de esas varianzas es 0 y los ``tobytes()`` coinciden.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

DEFAULT_TEXT = "Explicá el funcionamiento de list.append en Python."
RUNS = 5


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--embedder", default="bge-m3")
    parser.add_argument("--text", default=DEFAULT_TEXT)
    parser.add_argument("--runs", type=int, default=RUNS)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--out", type=Path, default=None, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def _worker(embedder_name: str, text: str, out_path: Path) -> None:
    from ddi_fw.embedder import get_embedder

    embedder = get_embedder(embedder_name)
    vector = np.asarray(embedder.embed_text(text))
    if vector.dtype != np.float32 or vector.ndim != 1:
        raise SystemExit(f"contrato roto: dtype={vector.dtype} shape={vector.shape}")
    model = embedder._load()
    weight = next(model.parameters())
    np.save(out_path, np.ascontiguousarray(vector))
    digest = hashlib.sha256(vector.tobytes()).hexdigest()
    print(
        f"sha256={digest} dtype={vector.dtype} dim={vector.shape[0]} "
        f"weight_dtype={weight.dtype} weight_device={weight.device}",
        flush=True,
    )


def _bit_population(packed: np.ndarray) -> tuple[np.ndarray, int]:
    """packed: (n, dim) uint32. Devuelve conteo de bits en 1, shape (dim, 32), y n."""
    n = int(packed.shape[0])
    shifts = np.arange(32, dtype=np.uint32)
    ones = ((packed[:, :, None] >> shifts) & np.uint32(1)).sum(axis=0)
    return ones.astype(np.int64, copy=False), n


def _report(paths: list[Path]) -> int:
    vectors = [np.load(path) for path in paths]
    for vector in vectors:
        if vector.dtype != np.float32 or vector.ndim != 1:
            raise SystemExit(f"npy inesperado: dtype={vector.dtype} shape={vector.shape}")
    if any(vector.shape != vectors[0].shape for vector in vectors):
        raise SystemExit("las corridas no comparten dimensión")

    packed = np.stack([np.ascontiguousarray(vector).view(np.uint32) for vector in vectors])
    counts, n = _bit_population(packed)
    numer = counts * (n - counts)
    max_numer = int(numer.max())
    denom = n * n
    identical = bool(
        max_numer == 0 and all(np.array_equal(vectors[0], vector) for vector in vectors)
    )

    print(f"runs={n}")
    print(f"dimension={vectors[0].shape[0]}")
    print(f"dtype={vectors[0].dtype}")
    print(f"bitwise_identical={str(identical).lower()}")
    print(f"max_bit_variance_numer={max_numer}")
    print(f"max_bit_variance_denom={denom}")
    if max_numer == 0:
        print("max_bit_variance=0")
    else:
        print(f"max_bit_variance={max_numer}/{denom}")
        axis, bit = np.unravel_index(int(numer.argmax()), numer.shape)
        print(f"max_bit_axis={int(axis)}")
        print(f"max_bit_index={int(bit)}")
        print(f"max_bit_ones={int(counts[axis, bit])}")
        words = packed[:, axis]
        print("uint32_hex=" + ",".join(f"{int(word):08x}" for word in words))
        print(
            "float32=" + ",".join(f"{float(np.float32(vectors[i][axis])):.17g}" for i in range(n))
        )
    return 0 if identical else 1


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.runs < 2:
        raise SystemExit("--runs debe ser >= 2")
    if args.worker:
        if args.out is None:
            raise SystemExit("--out es obligatorio en --worker")
        _worker(args.embedder, args.text, args.out)
        return 0

    script = str(Path(__file__).resolve())
    with tempfile.TemporaryDirectory(prefix="ddi-cold-embed-") as tmp:
        root = Path(tmp)
        paths: list[Path] = []
        for index in range(args.runs):
            out_path = root / f"run-{index}.npy"
            completed = subprocess.run(
                [
                    sys.executable,
                    script,
                    "--worker",
                    "--embedder",
                    args.embedder,
                    "--text",
                    args.text,
                    "--out",
                    str(out_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                sys.stderr.write(completed.stdout)
                sys.stderr.write(completed.stderr)
                raise SystemExit(completed.returncode or 1)
            print(f"run={index} {completed.stdout.strip()}")
            paths.append(out_path)
        return _report(paths)


if __name__ == "__main__":
    raise SystemExit(main())
