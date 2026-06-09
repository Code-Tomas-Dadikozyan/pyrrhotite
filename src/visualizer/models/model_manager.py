"""
VAO/VBO registry for named 3-D models.

Mirrors reference/src/gui/models/model_manager.h/.cpp.

Usage
-----
    mm = ModelManager()
    mm.initialize()                          # call after OpenGL context is active
    mm.register("sphere", *geometry.sphere())
    mm.draw("sphere", shader, transform, color)
    mm.cleanup()
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from OpenGL import GL

from .geometry import sphere, cylinder
from .obj_loader import load_obj
from ..shaders.shader_program import ShaderProgram


@dataclass
class _GPUModel:
    vao: int
    vbo: int
    ebo: int
    index_count: int


class ModelManager:
    """Registry of named OpenGL models (VAO + VBO + EBO)."""

    def __init__(self) -> None:
        self._models: dict[str, _GPUModel] = {}

    def initialize(self, arrow_obj_path) -> None:
        """Upload built-in models to the GPU. Call after OpenGL context is ready."""
        self.register("sphere", *sphere(stacks=20, slices=20))
        self.register("cylinder", *cylinder(segments=20))
        try:
            from pathlib import Path
            self.register("arrow", *load_obj(Path(arrow_obj_path)))
        except Exception:
            pass  # arrow is optional; used only for symmetry ops

    def register(self, name: str, vertices: np.ndarray, indices: np.ndarray) -> None:
        """Upload a model and store under *name*."""
        vao = GL.glGenVertexArrays(1)
        vbo = GL.glGenBuffers(1)
        ebo = GL.glGenBuffers(1)

        GL.glBindVertexArray(vao)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL.GL_STATIC_DRAW)

        GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GL.glBufferData(GL.GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL.GL_STATIC_DRAW)

        stride = 6 * 4  # 6 floats × 4 bytes
        # attribute 0: position (xyz)
        GL.glVertexAttribPointer(0, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, GL.ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(0)
        # attribute 1: normal (xyz)
        GL.glVertexAttribPointer(1, 3, GL.GL_FLOAT, GL.GL_FALSE, stride, GL.ctypes.c_void_p(12))
        GL.glEnableVertexAttribArray(1)

        GL.glBindVertexArray(0)
        self._models[name] = _GPUModel(vao, vbo, ebo, len(indices))

    def draw(
        self,
        name: str,
        shader: ShaderProgram,
        model_matrix: np.ndarray,
        view_matrix: np.ndarray,
        proj_matrix: np.ndarray,
        color: tuple[float, float, float, float],
        light_pos: tuple[float, float, float] = (0.0, -100.0, 0.0),
    ) -> None:
        """Draw the named model with Phong uniforms."""
        if name not in self._models:
            return
        m = self._models[name]
        # pyrr uses row-vector convention; with GL_FALSE GLSL receives M.T.
        # To get proj_cv @ view_cv @ model_cv in GLSL we need (model@view@proj).T
        mvp = model_matrix @ view_matrix @ proj_matrix

        shader.use()
        shader.set_mat4("model", model_matrix)
        shader.set_mat4("view", view_matrix)
        shader.set_mat4("mvp", mvp)
        shader.set_vec4("color", color)
        shader.set_vec3("lightpos", light_pos)

        GL.glBindVertexArray(m.vao)
        GL.glDrawElements(GL.GL_TRIANGLES, m.index_count, GL.GL_UNSIGNED_INT, None)
        GL.glBindVertexArray(0)

    def draw_axes(
        self,
        name: str,
        shader: ShaderProgram,
        model_matrix: np.ndarray,
        view_matrix: np.ndarray,
        proj_matrix: np.ndarray,
        color: tuple[float, float, float],
    ) -> None:
        """Draw with the axes shader (vec3 color uniform, hardcoded light)."""
        if name not in self._models:
            return
        m = self._models[name]
        mvp = model_matrix @ view_matrix @ proj_matrix

        shader.use()
        shader.set_mat4("mvp", mvp)
        shader.set_mat4("model", model_matrix)
        shader.set_mat4("view", view_matrix)
        shader.set_vec3("color", color)

        GL.glBindVertexArray(m.vao)
        GL.glDrawElements(GL.GL_TRIANGLES, m.index_count, GL.GL_UNSIGNED_INT, None)
        GL.glBindVertexArray(0)

    def cleanup(self) -> None:
        for m in self._models.values():
            GL.glDeleteVertexArrays(1, [m.vao])
            GL.glDeleteBuffers(1, [m.vbo])
            GL.glDeleteBuffers(1, [m.ebo])
        self._models.clear()
