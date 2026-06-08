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


_CYLINDER_RADIUS = 0.07   # world-space bond radius
_ATOM_SCALE = 0.25        # scale CPK radius for display


class StructureRenderer:
    """Converts a Structure to per-frame ModelInstance lists."""

    def __init__(self) -> None:
        self._structure: Structure | None = None
        self._bond_pairs: list[tuple[int, int]] = []
        self._span: float = 1.0
        # camera_rotation: accumulated orientation (mat4)
        self._camera_rotation: np.ndarray = np.eye(4, dtype=np.float32)
        # arcball_rotation: temporary rotation from current drag
        self._arcball_rotation: np.ndarray = np.eye(4, dtype=np.float32)
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

    def set_arcball_rotation(self, angle: float, axis: np.ndarray) -> None:
        """Set the temporary arcball rotation (not yet applied)."""
        if np.linalg.norm(axis) < 1e-6:
            self._arcball_rotation = np.eye(4, dtype=np.float32)
        else:
            self._arcball_rotation = pyrr.matrix44.create_from_axis_rotation(
                axis / np.linalg.norm(axis), angle, dtype=np.float32
            )

    def apply_arcball_rotation(self) -> None:
        """Merge the temporary arcball rotation into the camera rotation."""
        self._camera_rotation = self._arcball_rotation @ self._camera_rotation
        self._arcball_rotation = np.eye(4, dtype=np.float32)

    def get_view_matrix(self) -> np.ndarray:
        """Camera view matrix: translate back by 4 × span, then rotate."""
        dist = 4.0 * self._span
        translate = pyrr.matrix44.create_from_translation(
            np.array([0.0, 0.0, -dist], dtype=np.float32)
        )
        rotation = self._arcball_rotation @ self._camera_rotation
        return translate @ rotation

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
            r = max(el.radius, 0.25) * _ATOM_SCALE
            pos = coords[i]
            scale = pyrr.matrix44.create_from_scale(
                np.array([r, r, r], dtype=np.float32)
            )
            trans = pyrr.matrix44.create_from_translation(
                pos.astype(np.float32)
            )
            transform = trans @ scale
            c = el.colour
            instances.append(ModelInstance("sphere", transform, (c[0], c[1], c[2], 1.0)))

        # Bond cylinders
        for a, b in self._bond_pairs:
            instances.extend(self._bond_instances(coords[a], coords[b]))

        return instances

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _reset_camera(self) -> None:
        """Set the initial viewing angle: 60° around X, 20° around Z."""
        rx = pyrr.matrix44.create_from_x_rotation(math.radians(60.0), dtype=np.float32)
        rz = pyrr.matrix44.create_from_z_rotation(math.radians(20.0), dtype=np.float32)
        self._camera_rotation = rx @ rz
        self._arcball_rotation = np.eye(4, dtype=np.float32)

    def _calculate_span(self) -> None:
        if self._structure is None or len(self._structure.coordinates) == 0:
            self._span = 1.0
            return
        dists = np.linalg.norm(self._structure.coordinates, axis=1)
        self._span = float(np.max(dists)) if len(dists) else 1.0
        self._span = max(self._span, 0.5)

    def _bond_instances(
        self, p0: np.ndarray, p1: np.ndarray
    ) -> list[ModelInstance]:
        """Create a cylinder ModelInstance for the bond p0→p1."""
        diff = p1 - p0
        length = float(np.linalg.norm(diff))
        if length < 1e-6:
            return []

        direction = diff / length
        mid = (p0 + p1) / 2.0

        # Rotation: cylinder is along +Z by default — rotate to bond direction
        z = np.array([0.0, 0.0, 1.0], dtype=np.float32)
        d = direction.astype(np.float32)
        dot = float(np.clip(np.dot(z, d), -1.0, 1.0))

        if abs(dot + 1.0) < 1e-6:
            # Anti-parallel: 180° rotation around X
            rot = pyrr.matrix44.create_from_x_rotation(math.pi, dtype=np.float32)
        elif abs(dot - 1.0) < 1e-6:
            rot = np.eye(4, dtype=np.float32)
        else:
            axis = np.cross(z, d)
            axis = axis / np.linalg.norm(axis)
            angle = math.acos(dot)
            rot = pyrr.matrix44.create_from_axis_rotation(axis, angle, dtype=np.float32)

        # Build the full transform: scale Z by length, translate to p0
        # (cylinder goes 0→length along local Z, then rotate, then translate)
        scale = pyrr.matrix44.create_from_scale(
            np.array([_CYLINDER_RADIUS, _CYLINDER_RADIUS, length], dtype=np.float32)
        )
        trans = pyrr.matrix44.create_from_translation(p0.astype(np.float32))
        transform = trans @ rot @ scale

        color = (0.7, 0.7, 0.7, 1.0)
        return [ModelInstance("cylinder", transform, color)]
