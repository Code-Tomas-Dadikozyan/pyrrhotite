"""
OpenGL shader program wrapper.

Mirrors reference/src/gui/shaders/shader_program.h/.cpp:
  - Compile vertex + fragment source
  - Link into a program
  - Typed uniform setters (mat4, vec3, vec4, int, float)
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from OpenGL import GL


class ShaderProgram:
    """Compiled and linked OpenGL shader program."""

    def __init__(self, vertex_path: Path, fragment_path: Path) -> None:
        vert_src = vertex_path.read_text(encoding="utf-8")
        frag_src = fragment_path.read_text(encoding="utf-8")
        self._id = self._compile_and_link(vert_src, frag_src)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def use(self) -> None:
        """Bind this shader program."""
        GL.glUseProgram(self._id)

    def delete(self) -> None:
        GL.glDeleteProgram(self._id)

    # ------------------------------------------------------------------
    # Uniform setters
    # ------------------------------------------------------------------

    def set_mat4(self, name: str, matrix: np.ndarray) -> None:
        """Upload a 4×4 float matrix (column-major, like GLM)."""
        loc = GL.glGetUniformLocation(self._id, name)
        GL.glUniformMatrix4fv(loc, 1, GL.GL_FALSE, matrix.astype(np.float32).flatten())

    def set_vec3(self, name: str, v: np.ndarray | tuple) -> None:
        loc = GL.glGetUniformLocation(self._id, name)
        GL.glUniform3f(loc, float(v[0]), float(v[1]), float(v[2]))

    def set_vec4(self, name: str, v: np.ndarray | tuple) -> None:
        loc = GL.glGetUniformLocation(self._id, name)
        GL.glUniform4f(loc, float(v[0]), float(v[1]), float(v[2]), float(v[3]))

    def set_int(self, name: str, value: int) -> None:
        loc = GL.glGetUniformLocation(self._id, name)
        GL.glUniform1i(loc, value)

    def set_float(self, name: str, value: float) -> None:
        loc = GL.glGetUniformLocation(self._id, name)
        GL.glUniform1f(loc, value)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compile_shader(source: str, shader_type: int) -> int:
        shader = GL.glCreateShader(shader_type)
        GL.glShaderSource(shader, source)
        GL.glCompileShader(shader)
        if not GL.glGetShaderiv(shader, GL.GL_COMPILE_STATUS):
            log = GL.glGetShaderInfoLog(shader).decode()
            GL.glDeleteShader(shader)
            kind = "vertex" if shader_type == GL.GL_VERTEX_SHADER else "fragment"
            raise RuntimeError(f"Shader compile error ({kind}):\n{log}")
        return shader

    @classmethod
    def _compile_and_link(cls, vert_src: str, frag_src: str) -> int:
        vert = cls._compile_shader(vert_src, GL.GL_VERTEX_SHADER)
        frag = cls._compile_shader(frag_src, GL.GL_FRAGMENT_SHADER)
        program = GL.glCreateProgram()
        GL.glAttachShader(program, vert)
        GL.glAttachShader(program, frag)
        GL.glLinkProgram(program)
        GL.glDeleteShader(vert)
        GL.glDeleteShader(frag)
        if not GL.glGetProgramiv(program, GL.GL_LINK_STATUS):
            log = GL.glGetProgramInfoLog(program).decode()
            GL.glDeleteProgram(program)
            raise RuntimeError(f"Shader link error:\n{log}")
        return program
