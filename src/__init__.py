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


def visualize_idealized_structure(
    point_group,
    radius: float = 1.0,
    height: float = 0.6,
    element: str = "F",
    show_labels: bool = False,
) -> None:
    """Generate an idealized structure for *point_group* and open the 3-D viewer.

    Equivalent to ``visualize(generate_idealized_structure(point_group, ...))``,
    without writing the structure to an `.xyz` file first. Requires
    ``pip install 'pyrrhotite[vis]'``.

    Parameters
    ----------
    point_group:
        Either a `PointGroupLabel` or a name string (e.g. "C12v", "D9d") --
        see `generate_idealized_structure`.
    radius, height, element:
        Forwarded to `generate_idealized_structure`.
    show_labels:
        Overlay element symbols on each atom. Default is ``False``.
    """
    structure = generate_idealized_structure(point_group, radius=radius, height=height, element=element)
    visualize(structure, show_labels=show_labels)


__all__ = [
    "__version__",
    "Structure",
    "RotorClass",
    "Symmetry",
    "generate_idealized_structure",
    "write_xyz",
    "display",
    "visualize",
    "visualize_idealized_structure",
    "list_sample_molecules",
    "load_sample",
    "analyse_sample",
    "visualize_sample",
    "show_character_table_sample",
]
