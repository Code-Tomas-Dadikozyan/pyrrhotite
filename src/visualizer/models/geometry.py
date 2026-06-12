"""
Procedural geometry generators.

Each function returns (vertices, indices) where:
  vertices  — float32 array shaped (N, 6): [x, y, z, nx, ny, nz]
  indices   — uint32 array of triangle indices

Mirrors the original C++ `schoenflies` gui/models/geometry.h/.cpp (the vendored
reference/ tree was removed in 0.2.0 — see https://gitlab.com/lkkmpn/schoenflies).
"""

from __future__ import annotations

import math

import numpy as np


def sphere(stacks: int = 16, slices: int = 16) -> tuple[np.ndarray, np.ndarray]:
    """Unit sphere centred at origin."""
    verts: list[list[float]] = []
    idxs: list[int] = []

    for i in range(stacks + 1):
        phi = math.pi * i / stacks
        for j in range(slices + 1):
            theta = 2 * math.pi * j / slices
            x = math.sin(phi) * math.cos(theta)
            y = math.cos(phi)
            z = math.sin(phi) * math.sin(theta)
            verts.append([x, y, z, x, y, z])  # pos == normal for unit sphere

    for i in range(stacks):
        for j in range(slices):
            a = i * (slices + 1) + j
            b = a + slices + 1
            idxs.extend([a, a + 1, b, b, a + 1, b + 1])

    return np.array(verts, dtype=np.float32), np.array(idxs, dtype=np.uint32)


def cylinder(segments: int = 16, height: float = 1.0, radius: float = 1.0) -> tuple[np.ndarray, np.ndarray]:
    """Cylinder along +Z from z=0 to z=height, radius=radius."""
    verts: list[list[float]] = []
    idxs: list[int] = []

    # Side wall vertices (two rings)
    for ring in range(2):
        z = ring * height
        for j in range(segments + 1):
            theta = 2 * math.pi * j / segments
            x = radius * math.cos(theta)
            y = radius * math.sin(theta)
            nx, ny = math.cos(theta), math.sin(theta)
            verts.append([x, y, z, nx, ny, 0.0])

    # Side triangles
    for j in range(segments):
        a = j
        b = j + segments + 1
        idxs.extend([a, a + 1, b, b, a + 1, b + 1])

    # Cap centres
    bot_c = len(verts)
    verts.append([0.0, 0.0, 0.0, 0.0, 0.0, -1.0])
    top_c = len(verts)
    verts.append([0.0, 0.0, height, 0.0, 0.0, 1.0])

    # Cap rim vertices
    bot_start = len(verts)
    for j in range(segments):
        theta = 2 * math.pi * j / segments
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        verts.append([x, y, 0.0, 0.0, 0.0, -1.0])

    top_start = len(verts)
    for j in range(segments):
        theta = 2 * math.pi * j / segments
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        verts.append([x, y, height, 0.0, 0.0, 1.0])

    for j in range(segments):
        nxt = (j + 1) % segments
        idxs.extend([bot_c, bot_start + nxt, bot_start + j])
        idxs.extend([top_c, top_start + j, top_start + nxt])

    return np.array(verts, dtype=np.float32), np.array(idxs, dtype=np.uint32)
