"""Pyrrhotite: Schoenflies point group determination package."""

from ._version import __version__
from .structure import Structure
from .rotor_class import RotorClass
from .symmetry import Symmetry
from .structure_generator import generate_idealized_structure, write_xyz

from . import display
from .display import (
    list_sample_molecules,
    load_sample,
    analyse_sample,
    visualize_sample,
    show_character_table_sample,
)


def visualize(structure: "Structure", show_labels: bool = False) -> None:
    """Open an interactive 3-D viewer for *structure* (requires ``pip install 'pyrrhotite[vis]'``).

    Parameters
    ----------
    show_labels:
        Overlay element symbols on each atom. Default is ``False``.
    """
    from .visualizer import visualize as _vis
    _vis(structure, show_labels=show_labels)


__all__ = [
    "__version__",
    "Structure",
    "RotorClass",
    "Symmetry",
    "generate_idealized_structure",
    "write_xyz",
    "display",
    "visualize",
    "list_sample_molecules",
    "load_sample",
    "analyse_sample",
    "visualize_sample",
    "show_character_table_sample",
]
