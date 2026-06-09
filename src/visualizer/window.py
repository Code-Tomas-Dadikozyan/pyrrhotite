"""
Main visualizer window.

Mirrors reference/src/gui/main_window.h/.cpp.
Creates a QMainWindow with the GLWidget as its central widget.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QMainWindow, QWidget
from PyQt6.QtCore import Qt

from ..structure import Structure
from .structure_renderer import StructureRenderer
from .gl_widget import GLWidget


class VisualizerWindow(QMainWindow):
    """Top-level window for the molecule visualizer."""

    def __init__(self, structure: Structure, show_labels: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._renderer = StructureRenderer()
        self._renderer.set_structure(structure)

        self._gl_widget = GLWidget(self._renderer, show_labels=show_labels, parent=self)
        self.setCentralWidget(self._gl_widget)

        title = Path(structure.filename).name if structure.filename else "pyrrhotite visualizer"
        self.setWindowTitle(f"pyrrhotite — {title}")
        self.resize(800, 600)
        self.setMinimumSize(400, 300)
