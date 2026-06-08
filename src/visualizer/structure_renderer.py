"""
High-level renderer that turns a Structure into lists of draw calls.

Mirrors reference/src/structure_renderer.h/.cpp.

Responsibilities
----------------
- Compute bond pairs and structure span from a Structure
- Maintain camera / arcball rotation matrices (pyrr)
- Expose get_structure_model_instances() → list[ModelInstance]
- Expose arcball helpers for mouse interaction
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pyrr

from ..structure import Structure
from ..periodic_table import element as get_element


@dataclass
class ModelInstance:
    """Single renderable object — mirrors reference ModelInstance."""
    model_name: str           # "sphere" | "cylinder" | "arrow"
    transform: np.ndarray     # 4×4 float32 model matrix
    color: tuple[float, float, float, float]  # RGBA [0-1]


_CYLINDER_RADIUS = 0.05   # world-space bond radius (matches reference)


class StructureRenderer:
    """Converts a Structure to per-frame ModelInstance lists."""

    def __init__(self) -> None:
        self._structure: Structure | None = None
        self._bond_pairs: list[tuple[int, int]] = []
        self._span: float = 1.0
        self._camera_rotation: np.ndarray = np.eye(4, dtype=np.float32)
        self._reset_camera()

    # ------------------------------------------------------------------
    # Public setters
    # ------------------------------------------------------------------

    def set_structure(self, structure: Structure) -> None:
        self._structure = structure
        self._bond_pairs = structure.calculate_bond_pairs()
        self._calculate_span()
        self._reset_camera()

    def reset_camera(self) -> None:
        self._reset_camera()

    # ------------------------------------------------------------------
    # Camera / arcball
    # ------------------------------------------------------------------

    def accumulate_arcball_delta(self, angle: float, axis: np.ndarray) -> None:
        """Apply one incremental drag step directly into the camera rotation."""
        if np.linalg.norm(axis) < 1e-6:
            return
        delta = pyrr.matrix44.create_from_axis_rotation(
            axis / np.linalg.norm(axis), angle, dtype=np.float32
        )
        # Post-multiply keeps delta in eye/screen space so dragging always
        # rotates around screen axes, not world axes.
        self._camera_rotation = self._camera_rotation @ delta

    def get_view_matrix(self) -> np.ndarray:
        """Camera view matrix: translate back by 4 × span, then rotate."""
        dist = 4.0 * self._span
        translate = pyrr.matrix44.create_from_translation(
            np.array([0.0, 0.0, -dist], dtype=np.float32)
        )
        # pyrr row-vector: GLSL sees (rotation @ translate).T = translate_cv @ rotation_cv
        return self._camera_rotation @ translate

    def get_span(self) -> float:
        return self._span

    # ------------------------------------------------------------------
    # ModelInstance generation
    # ------------------------------------------------------------------

    def get_structure_model_instances(self) -> list[ModelInstance]:
        """Return atom spheres + bond cylinders for the current structure."""
        if self._structure is None:
            return []

        instances: list[ModelInstance] = []
        coords = self._structure.coordinates  # (N, 3) COM-centred

        # Atom spheres
        for i, z in enumerate(self._structure.atomic_numbers):
            el = get_element(int(z))
            r = el.radius
            pos = coords[i]
            scale = pyrr.matrix44.create_from_scale(
                np.array([r, r, r], dtype=np.float32)
            )
            trans = pyrr.matrix44.create_from_translation(
                pos.astype(np.float32)
            )
            # pyrr row-vector: GLSL sees (A@B).T = B_cv @ A_cv, so reverse order
            transform = scale @ trans
            c = el.colour
            instances.append(ModelInstance("sphere", transform, (c[0], c[1], c[2], 1.0)))

        # Bond cylinders
        for a, b in self._bond_pairs:
            el_a = get_element(int(self._structure.atomic_numbers[a]))
            el_b = get_element(int(self._structure.atomic_numbers[b]))
            instances.extend(self._bond_instances(coords[a], coords[b], el_a, el_b))

        return instances

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_camera(self) -> None:
        """Set the initial viewing angle: 60° around X, 20° around Z."""
        rx = pyrr.matrix44.create_from_x_rotation(math.radians(60.0), dtype=np.float32)
        rz = pyrr.matrix44.create_from_z_rotation(math.radians(20.0), dtype=np.float32)
        self._camera_rotation = rx @ rz

    def _calculate_span(self) -> None:
        if self._structure is None or len(self._structure.coordinates) == 0:
            self._span = 1.0
            return
        dists = np.linalg.norm(self._structure.coordinates, axis=1)
        self._span = float(np.max(dists)) if len(dists) else 1.0
        self._span = max(self._span, 0.5)

    def _bond_instances(
        self, p0: np.ndarray, p1: np.ndarray,
        el_a, el_b
    ) -> list[ModelInstance]:
        """Split bond p0→p1 into two color-coded half-cylinders (one per element)."""
        diff = (p1 - p0).astype(np.float32)
        length = float(np.linalg.norm(diff))
        if length < 1e-6:
            return []

        # Rotation: cylinder is along +Z by default — rotate to bond direction
        direction = diff / length
        z = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        dot = float(np.clip(np.dot(z, direction), -1.0, 1.0))
        if abs(dot + 1.0) < 1e-6:
            rot = pyrr.matrix44.create_from_x_rotation(math.pi, dtype=np.float32)
        elif abs(dot - 1.0) < 1e-6:
            rot = np.eye(4, dtype=np.float32)
        else:
            axis = np.cross(z, direction)
            axis = axis / np.linalg.norm(axis)
            rot = pyrr.matrix44.create_from_axis_rotation(axis, math.acos(dot), dtype=np.float32)

        # Split point: accounts for radius difference (mirrors reference)
        split = 0.5 + (el_a.radius - el_b.radius) / length / 2.0
        trans_a = p0.astype(np.float32)
        trans_b = (p0 + split * diff).astype(np.float32)
        len_a = split * length
        len_b = (1.0 - split) * length

        def _half(trans: np.ndarray, seg_len: float, el) -> ModelInstance:
            scale = pyrr.matrix44.create_from_scale(
                np.array([_CYLINDER_RADIUS, _CYLINDER_RADIUS, seg_len], dtype=np.float32)
            )
            t = pyrr.matrix44.create_from_translation(trans)
            transform = scale @ rot @ t
            c = el.colour
            return ModelInstance("cylinder", transform, (c[0], c[1], c[2], 1.0))

        return [_half(trans_a, len_a, el_a), _half(trans_b, len_b, el_b)]
