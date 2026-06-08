"""
3-D molecule visualizer for pyrrhotite.

Public API
----------
visualize(structure)   — open a PyQt6/OpenGL window for the given Structure
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..structure import Structure


def visualize(structure: "Structure") -> None:
    """Open an interactive 3-D viewer for *structure*.

    Requires the optional ``vis`` dependencies (PyQt6, PyOpenGL, pyrr).
    """
    try:
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        from PyQt6.QtGui import QSurfaceFormat
    except ImportError as exc:
        raise ImportError(
            "The visualizer requires optional dependencies. "
            "Install them with:  pip install 'pyrrhotite[vis]'"
        ) from exc

    import sys

    # Force native OpenGL (avoids ANGLE/DirectX wrapper on Windows which can
    # silently fail for uniform uploads and VAO state).
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseDesktopOpenGL)

    # Request OpenGL 3.3 core profile + depth buffer before any window is shown.
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    fmt.setSamples(4)
    QSurfaceFormat.setDefaultFormat(fmt)

    from .window import VisualizerWindow

    app = QApplication.instance() or QApplication(sys.argv)
    win = VisualizerWindow(structure)
    win.show()
    app.exec()
