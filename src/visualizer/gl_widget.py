"""
OpenGL rendering widget.

Mirrors reference/src/gui/gl_widget.h/.cpp.

Rendering pipeline (per frame)
-------------------------------
1. Clear colour + depth
2. Phong pass — atoms (spheres) + bonds (cylinders) via model_manager.draw()
3. Axes gizmo pass — three coloured arrows in the corner
4. QPainter overlay — element labels on top of GL content

Mouse interaction
-----------------
- Left-drag   : arcball rotation
- Scroll      : zoom (adjusts camera distance multiplier)
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pyrr
from OpenGL import GL
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QPainter, QFont
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QWidget

from .structure_renderer import StructureRenderer
from .models.model_manager import ModelManager
from .shaders.shader_program import ShaderProgram

_ASSETS = Path(__file__).parent / "assets"
_SHADERS = _ASSETS / "shaders"
_MODELS = _ASSETS / "models"

_LIGHT_POS = (3.0, 5.0, 10.0)   # eye-space: slightly above-right of camera
_BG_COLOR = (0.82, 0.84, 0.88, 1.0)
_GIZMO_SCALE = 0.08   # fraction of widget width used by gizmo viewport


class GLWidget(QOpenGLWidget):
    """PyQt6 OpenGL widget — mirrors GLWidget in the C++ reference."""

    def __init__(self, renderer: StructureRenderer, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._renderer = renderer
        self._model_manager: ModelManager | None = None
        self._phong_shader: ShaderProgram | None = None
        self._axes_shader: ShaderProgram | None = None

        self._mouse_pos = QPoint()
        self._arcball_active = False
        self._zoom_multiplier = 1.0

        self.setMinimumSize(400, 300)

    # ------------------------------------------------------------------
    # OpenGL lifecycle
    # ------------------------------------------------------------------

    def initializeGL(self) -> None:
        try:
            self._initializeGL_impl()
        except Exception as exc:
            import traceback
            print(f"[visualizer] initializeGL error: {exc}")
            traceback.print_exc()

    def _initializeGL_impl(self) -> None:
        version = GL.glGetString(GL.GL_VERSION)
        renderer = GL.glGetString(GL.GL_RENDERER)
        print(f"[visualizer] OpenGL {version}  renderer={renderer}")

        GL.glClearColor(*_BG_COLOR)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glCullFace(GL.GL_BACK)

        self._phong_shader = ShaderProgram(
            _SHADERS / "phong.vs",
            _SHADERS / "phong.fs",
        )
        self._axes_shader = ShaderProgram(
            _SHADERS / "axes.vs",
            _SHADERS / "axes.fs",
        )

        self._model_manager = ModelManager()
        self._model_manager.initialize(_MODELS / "arrow.obj")
        print("[visualizer] GL initialisation complete")

    def resizeGL(self, w: int, h: int) -> None:
        self._w = w
        self._h = h

    def paintGL(self) -> None:
        dpr = self.devicePixelRatioF()
        w, h = max(self.width(), 1), max(self.height(), 1)
        pw, ph = int(w * dpr), int(h * dpr)  # physical pixels for GL
        GL.glViewport(0, 0, pw, ph)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        if self._phong_shader is None or self._model_manager is None:
            return

        proj = self._projection_matrix()
        view = self._renderer.get_view_matrix()

        # --- Structure pass (atoms + bonds) ---
        for inst in self._renderer.get_structure_model_instances():
            self._model_manager.draw(
                inst.model_name,
                self._phong_shader,
                inst.transform,
                view,
                proj,
                inst.color,
                _LIGHT_POS,
            )

        # --- Axes gizmo ---
        self._paint_gizmos(view, proj)

        # --- QPainter label overlay ---
        self._paint_labels(proj, view)

    # ------------------------------------------------------------------
    # Mouse interaction (arcball)
    # ------------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_pos = event.pos()
            self._arcball_active = True

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._arcball_active:
            self._arcball_active = False
            self.update()

    def mouseMoveEvent(self, event) -> None:
        if not self._arcball_active:
            return
        p0 = self._arcball_vector(self._mouse_pos)
        p1 = self._arcball_vector(event.pos())
        dot = float(np.clip(np.dot(p0, p1), -1.0, 1.0))
        angle = math.acos(dot) * 2.0
        axis = np.cross(p0, p1)
        if np.linalg.norm(axis) > 1e-6:
            # Accumulate delta rotation into camera so large drags never
            # cause axis flips (the antipodal singularity in total-rotation mode).
            self._renderer.accumulate_arcball_delta(angle, axis)
        self._mouse_pos = event.pos()
        self.update()

    def wheelEvent(self, event) -> None:
        delta = event.angleDelta().y()
        self._zoom_multiplier *= (0.9 if delta > 0 else 1.1)
        self._zoom_multiplier = max(0.1, min(self._zoom_multiplier, 20.0))
        self.update()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _projection_matrix(self) -> np.ndarray:
        w = max(self.width(), 1)
        h = max(self.height(), 1)
        span = self._renderer.get_span()
        dist = 4.0 * span * self._zoom_multiplier
        near = dist * 0.01
        far = dist * 10.0
        return pyrr.matrix44.create_perspective_projection_matrix(
            45.0, w / h, near, far, dtype=np.float32
        )

    def _arcball_vector(self, pos: QPoint) -> np.ndarray:
        """Map a screen point to a unit vector on the arcball hemisphere."""
        w = max(self.width(), 1)
        h = max(self.height(), 1)
        x = (2.0 * pos.x() / w) - 1.0
        y = 1.0 - (2.0 * pos.y() / h)
        r2 = x * x + y * y
        if r2 <= 1.0:
            z = math.sqrt(1.0 - r2)
        else:
            norm = math.sqrt(r2)
            x /= norm
            y /= norm
            z = 0.0
        v = np.array([x, y, z], dtype=np.float32)
        return v / np.linalg.norm(v)

    def _paint_gizmos(self, view: np.ndarray, proj: np.ndarray) -> None:
        """Draw XYZ axis arrows in a small viewport in the bottom-left corner."""
        dpr = self.devicePixelRatioF()
        w = self.width()
        h = self.height()
        pw, ph = int(w * dpr), int(h * dpr)
        size = int(min(w, h) * _GIZMO_SCALE * 2.5 * dpr)
        GL.glViewport(0, 0, size, size)

        # Gizmo uses an orthographic-like small projection
        gizmo_proj = pyrr.matrix44.create_perspective_projection_matrix(
            45.0, 1.0, 0.01, 1000.0, dtype=np.float32
        )
        # Gizmo view: same rotation as scene but fixed distance, no translation.
        # pyrr stores translation in last ROW (row-vector convention): view[3, 0:3].
        rotation_only = view.copy()
        rotation_only[3, 0] = 0.0
        rotation_only[3, 1] = 0.0
        rotation_only[3, 2] = -3.0   # fixed small distance

        axes = [
            (np.array([1, 0, 0], dtype=np.float32), (1.0, 0.2, 0.2)),
            (np.array([0, 1, 0], dtype=np.float32), (0.2, 1.0, 0.2)),
            (np.array([0, 0, 1], dtype=np.float32), (0.2, 0.4, 1.0)),
        ]

        for axis, color in axes:
            angle = 0.0
            z = np.array([0, 0, 1], dtype=np.float32)
            cross = np.cross(z, axis)
            dot = float(np.dot(z, axis))
            if np.linalg.norm(cross) < 1e-6:
                if dot < 0:
                    rot = pyrr.matrix44.create_from_x_rotation(math.pi, dtype=np.float32)
                else:
                    rot = np.eye(4, dtype=np.float32)
            else:
                angle = math.acos(np.clip(dot, -1, 1))
                rot = pyrr.matrix44.create_from_axis_rotation(
                    cross / np.linalg.norm(cross), angle, dtype=np.float32
                )
            # arrow.obj is ~7 units long with radius ~1; scale to match gizmo viewport
            scale = pyrr.matrix44.create_from_scale(
                np.array([0.07, 0.07, 0.07], dtype=np.float32)
            )
            model = scale @ rot
            if self._axes_shader and self._model_manager:
                self._model_manager.draw_axes(
                    "arrow", self._axes_shader, model, rotation_only, gizmo_proj, color
                )

        # Restore full viewport (physical pixels)
        GL.glViewport(0, 0, pw, ph)

    def _paint_labels(self, proj: np.ndarray, view: np.ndarray) -> None:
        """Overlay atom element labels using QPainter (no FreeType needed)."""
        if self._renderer._structure is None:
            return

        # QPainter works in logical pixels; projection aspect uses logical pixels too.
        w = self.width()
        h = self.height()
        mvp = view @ proj  # pyrr row-vector: clip = pos4 @ mvp
        coords = self._renderer._structure.coordinates
        atomic_numbers = self._renderer._structure.atomic_numbers

        from ..periodic_table import element as get_element

        # Project all atoms and collect (ndc_z, screen_x, screen_y, symbol)
        items: list[tuple[float, int, int, str]] = []
        for i, z in enumerate(atomic_numbers):
            pos4 = np.array([coords[i, 0], coords[i, 1], coords[i, 2], 1.0], dtype=np.float32)
            clip = pos4 @ mvp
            if clip[3] < 0.01:
                continue
            ndc = clip[:3] / clip[3]
            if ndc[2] < -1.0 or ndc[2] > 1.0:
                continue
            if abs(ndc[0]) > 1.1 or abs(ndc[1]) > 1.1:
                continue
            sx = int((ndc[0] * 0.5 + 0.5) * w)
            sy = int((0.5 - ndc[1] * 0.5) * h)
            items.append((float(ndc[2]), sx, sy, get_element(int(z)).symbol))

        if not items:
            return

        # Depth range for fading back-side labels
        depths = [d for d, *_ in items]
        d_min, d_max = min(depths), max(depths)
        d_range = max(d_max - d_min, 1e-4)

        # Draw back-to-front so front labels render on top
        items.sort(key=lambda t: -t[0])

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        for depth, sx, sy, sym in items:
            # Front atoms fully opaque, back atoms more transparent
            t = (depth - d_min) / d_range  # 0 = front, 1 = back
            alpha = int(230 * (1.0 - 0.6 * t))
            # Dark shadow for readability against light background and light atoms
            painter.setPen(QColor(0, 0, 0, alpha // 2))
            painter.drawText(sx + 7, sy - 3, sym)
            # Neon green — distinct from all CPK colors (gray/white/blue/red/yellow)
            painter.setPen(QColor(30, 255, 80, alpha))
            painter.drawText(sx + 6, sy - 4, sym)

        painter.end()
