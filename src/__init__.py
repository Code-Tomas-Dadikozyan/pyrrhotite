"""Pyrrhotite: Schoenflies point group determination package."""

from ._version import __version__
from .structure import Structure
from .rotor_class import RotorClass
from .symmetry import Symmetry

from . import display


def visualize(structure: "Structure") -> None:
    """Open an interactive 3-D viewer for *structure* (requires ``pip install 'pyrrhotite[vis]'``)."""
    from .visualizer import visualize as _vis
    _vis(structure)


__all__ = ["__version__", "Structure", "RotorClass", "Symmetry", "display", "visualize"]
