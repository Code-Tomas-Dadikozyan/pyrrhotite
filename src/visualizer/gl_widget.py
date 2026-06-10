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
from PyQt6.QtGui import QColor, QPainter, QFont, QFontMetrics
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

    def __init__(self, renderer: StructureRenderer, show_labels: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._renderer = renderer
        self._show_labels = show_labels
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
            self._renderer.apply_arcball_rotation()
            self._arcball_active = False
            self.update()

    def mouseMoveEvent(self, event) -> None:
        if not self._arcball_active:
            return
        p0 = self._arcball_vector(self._mouse_pos)   # click-start, never updated
        p1 = self._arcball_vector(event.pos())
        dot = float(np.clip(np.dot(p0, p1), -1.0, 1.0))
        if abs(dot) > 0.9999:
            return
        angle = math.acos(dot) * 1.6   # 60% sensitivity boost
        # Axis in screen/camera space
        axis_cam = np.cross(p0, p1)
        axis_cam = axis_cam / np.linalg.norm(axis_cam)
        # Convert to world space using the COMMITTED camera rotation only (no arcball).
        # arcball_rotation may already be set from earlier this drag; including it
        # would rotate the basis each frame and produce a wrong, drifting axis.
        # Matches the reference, where view is a fixed lookAt that never changes
        # during a drag — so the cam→world basis is constant across the whole drag.
        camera_rot = self._renderer.get_camera_rotation()
        axis_world = axis_cam @ camera_rot[:3, :3].T
        self._renderer.set_arcball_rotation(angle, axis_world)
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
        """Draw XYZ axis arrows — top-right corner, orthographic, Phong-lit.

        Mirrors reference paint_gizmos(): the molecule rotation lives in the
        MODEL matrix (base_camera_matrix @ per-axis rotation), the gizmo view
        is a fixed lookAt from -Y, and projection is orthographic.
        """
        if not self._axes_shader or not self._model_manager:
            return

        dpr = self.devicePixelRatioF()
        w = self.width()
        h = self.height()
        pw, ph = int(w * dpr), int(h * dpr)
        gizmo_px = int(min(pw, ph) * 0.25)
        # Bottom-right corner
        GL.glViewport(pw - gizmo_px, 0, gizmo_px, gizmo_px)

        size = 15.0
        gizmo_proj = pyrr.matrix44.create_orthogonal_projection_matrix(
            -size, size, -size, size, 0.1, 1000.0, dtype=np.float32
        )
        gizmo_view = pyrr.matrix44.create_look_at(
            np.array([0.0, -10.0, 0.0], dtype=np.float32),
            np.array([0.0,   0.0, 0.0], dtype=np.float32),
            np.array([0.0,   0.0, 1.0], dtype=np.float32),
            dtype=np.float32,
        )

        base = self._renderer.get_base_camera_matrix()

        # set_mat4 sends GL_FALSE + row-major flatten → GLSL receives M.T.
        # For rotation M: M.T = M_cv(θ), so pyrr.create_from_y_rotation(+π/2) → GLSL Ry_cv(+π/2).
        # Matches reference: X=Ry_cv(+90°), Y=Rx_cv(-90°), Z=identity.
        axes_specs = [
            (pyrr.matrix44.create_from_y_rotation( math.pi / 2, dtype=np.float32),
             (1.0, 0.2117, 0.3255)),
            (pyrr.matrix44.create_from_x_rotation(-math.pi / 2, dtype=np.float32),
             (0.5412, 0.8549, 0.0235)),
            (np.eye(4, dtype=np.float32),
             (0.1725, 0.5608, 1.0)),
        ]

        # Painter's algorithm: sort arrows back-to-front relative to the gizmo camera.
        # Gizmo camera is at (0,-10,0) looking along +Y.  GLSL sees model_cv = (axis_rot@base).T,
        # so the tip (model-space (0,0,10)) lands at world-Y = 10 * (axis_rot@base)[2,1].
        # Largest world-Y → furthest from camera → draw first (behind others).
        # We also disable the depth test entirely so the gizmo always renders on top
        # of the main scene (matching the reference, whose screen framebuffer depth
        # is clean when paint_gizmos runs).
        arrow_list = []
        for axis_rot, color in axes_specs:
            model = axis_rot @ base
            world_y = float(model[2, 1])   # proxy for tip depth along gizmo camera axis
            arrow_list.append((world_y, model, color))
        arrow_list.sort(key=lambda x: -x[0])   # furthest first

        GL.glDisable(GL.GL_DEPTH_TEST)
        for _, model, color in arrow_list:
            self._model_manager.draw_axes(
                "arrow", self._axes_shader, model, gizmo_view, gizmo_proj, color
            )
        GL.glEnable(GL.GL_DEPTH_TEST)

        GL.glViewport(0, 0, pw, ph)

    def _paint_labels(self, proj: np.ndarray, view: np.ndarray) -> None:
        """Overlay atom element labels using QPainter (no FreeType needed)."""
        if not self._show_labels or self._renderer._structure is None:
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

        # Camera distance = 4*span, so atom screen size ∝ 1/span → font shrinks for large molecules.
        raw_size = int(35 / (self._renderer.get_span() * self._zoom_multiplier))
        font_size = max(7, min(20, raw_size))
        font = QFont("Arial", font_size, QFont.Weight.Bold)
        fm = QFontMetrics(font)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(font)

        for depth, sx, sy, sym in items:
            # Front atoms fully opaque, back atoms more transparent
            t = (depth - d_min) / d_range  # 0 = front, 1 = back
            alpha = int(230 * (1.0 - 0.6 * t))
            tw = fm.horizontalAdvance(sym)
            th = fm.ascent()
            cx = sx - tw // 2
            cy = sy + th // 2
            # Dark shadow for readability against all CPK atom colors
            painter.setPen(QColor(0, 0, 0, min(255, alpha)))
            painter.drawText(cx + 1, cy + 1, sym)
            # White — contrasts with every CPK color when shadow is present
            painter.setPen(QColor(255, 255, 255, alpha))
            painter.drawText(cx, cy, sym)

        painter.end()
