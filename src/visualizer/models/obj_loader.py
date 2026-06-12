"""
Minimal OBJ file loader.

Returns (vertices, indices) in the same layout as geometry.py:
  vertices — float32 (N, 6): [x, y, z, nx, ny, nz]
  indices  — uint32 triangle indices

Mirrors the original C++ `schoenflies` gui/models/obj_loader.h/.cpp (the vendored
reference/ tree was removed in 0.2.0 — see https://gitlab.com/lkkmpn/schoenflies).
Only handles 'v', 'vn', and 'f' directives (no materials, no texcoords).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_obj(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load a simple OBJ file and return (vertices, indices)."""
    raw_positions: list[tuple[float, float, float]] = []
    raw_normals: list[tuple[float, float, float]] = []
    # Each face vertex is (pos_idx, norm_idx) — 1-based from OBJ spec
    face_entries: list[tuple[int, int]] = []
    face_index_triples: list[tuple[int, int, int]] = []  # indices into face_entries

    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("vn "):
                parts = line.split()
                raw_normals.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("v "):
                parts = line.split()
                raw_positions.append((float(parts[1]), float(parts[2]), float(parts[3])))
            elif line.startswith("f "):
                parts = line.split()[1:]
                # Fan-triangulate polygon
                poly: list[tuple[int, int]] = []
                for token in parts:
                    sub = token.split("/")
                    pi = int(sub[0]) - 1
                    ni = int(sub[2]) - 1 if len(sub) > 2 and sub[2] else 0
                    poly.append((pi, ni))
                for k in range(1, len(poly) - 1):
                    face_index_triples.append((
                        _get_or_add(face_entries, poly[0]),
                        _get_or_add(face_entries, poly[k]),
                        _get_or_add(face_entries, poly[k + 1]),
                    ))

    verts = []
    for pi, ni in face_entries:
        p = raw_positions[pi]
        n = raw_normals[ni] if raw_normals else (0.0, 0.0, 1.0)
        verts.append([p[0], p[1], p[2], n[0], n[1], n[2]])

    idxs = [i for triple in face_index_triples for i in triple]
    return np.array(verts, dtype=np.float32), np.array(idxs, dtype=np.uint32)


def _get_or_add(lst: list, item: tuple) -> int:
    """Return the index of `item` in `lst`, appending it first if not already present (vertex dedup)."""
    try:
        return lst.index(item)
    except ValueError:
        lst.append(item)
        return len(lst) - 1
