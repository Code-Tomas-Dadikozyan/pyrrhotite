"""
display.py — pretty-printing helpers and sample-molecule shortcuts.

This module has two halves:

1. Pretty-print helpers (`print_bond_pairs`, `print_ops_with_atoms`,
   `print_basis_functions`, `print_char_table_programmatic`) that take objects
   already produced by `Structure`, `Symmetry`, or `PointGroup` and print them in a
   readable form — useful for exploring results in a Python shell or notebook.

2. Sample-molecule convenience functions (`list_sample_molecules`, `load_sample`,
   `analyse_sample`, `visualize_sample`, `show_character_table_sample`) that work
   with the 32 `.xyz` files bundled in `tests/files/`, so new users can try out
   pyrrhotite without supplying their own molecule.
"""

from __future__ import annotations

import random
from pathlib import Path

from .structure import Structure
from .operations.operation import Operation
from .operations.operation_label import OperationLabel
from .periodic_table import element
from .point_groups.point_group import PointGroup
from .point_groups.basis_functions import compute_basis_functions

_SEP = "-" * 60

# ---------------------------------------------------------------------------
# Pretty-print helpers
# ---------------------------------------------------------------------------

def print_bond_pairs(s: Structure) -> None:
    """Print every bonded atom pair with element symbols and atom indices."""
    for a, b in s.calculate_bond_pairs():
        ea = element(int(s.atomic_numbers[a])).symbol
        eb = element(int(s.atomic_numbers[b])).symbol
        print(f"  {ea}{a} — {eb}{b}")


def print_ops_with_atoms(ops: list[Operation], s: Structure) -> None:
    """Print each symmetry operation and the atoms that lie on its axis or plane."""
    for op in ops:
        lbl = op.label
        if lbl.element == OperationLabel.Element.Reflection:
            atom_indices = op.atoms_in_plane(s)
            loc = "in plane" + (" [molecular plane]" if op.is_molecular_plane(s) else "")
        else:
            atom_indices = op.atoms_on_axis(s)
            loc = "on axis"
        atoms = ", ".join(
            f"{element(int(s.atomic_numbers[i])).symbol}{i}" for i in atom_indices
        ) or "none"
        print(f"  {lbl.short_name:<10}  {loc}: {atoms}")


def print_basis_functions(pg: PointGroup) -> None:
    """Print the irrep → linear/rotational and quadratic basis function table."""
    bf = compute_basis_functions(pg)
    print(f"  {'Irrep':<8}  {'Linear / Rotational':<26}  Quadratic")
    print("  " + _SEP)
    for irrep_name, funcs in bf.items():
        lin  = ", ".join(funcs["linear"])    or "—"
        quad = ", ".join(funcs["quadratic"]) or "—"
        print(f"  {irrep_name:<8}  {lin:<26}  {quad}")


def print_char_table_programmatic(pg: PointGroup) -> None:
    """Print the character table by directly accessing pg.irreps, pg.characters, and pg.unique_operations."""
    irreps = pg.irreps
    ops    = pg.unique_operations
    chars  = pg.characters
    print("Irreducible representations:")
    for ir in irreps:
        print(f"  {ir.name}")
    print("\nConjugacy classes (from unique_operations, excluding E):")
    for olc in ops:
        print(f"  {olc.short_name:<12}  count={olc.count}")
    print("\nFull character table (rows = irreps, columns = E then unique ops):")
    header = f"  {'':>6}" + f"  {'E':>6}" + "".join(f"  {o.label.short_name:>6}" for o in ops)
    print(header)
    for i, ir in enumerate(irreps):
        row = "  ".join(f"{v:6.3f}" for v in chars[i])
        print(f"  {ir.name:<6}  {row}")


# ---------------------------------------------------------------------------
# Sample-molecule exploration
# ---------------------------------------------------------------------------

_SAMPLES_DIR = Path(__file__).parent.parent / "tests" / "files"


def _samples_dir() -> Path:
    if not _SAMPLES_DIR.is_dir():
        raise FileNotFoundError(
            f"Sample molecules directory not found at {_SAMPLES_DIR}. "
            "Make sure you are running from the repository root and that "
            "the tests/files/ directory is present."
        )
    return _SAMPLES_DIR


def list_sample_molecules() -> list[str]:
    """Return a sorted list of names of the built-in sample molecules.

    Each name corresponds to the stem of an XYZ file in tests/files/ and can
    be passed directly to :func:`load_sample`, :func:`analyse_sample`,
    :func:`visualize_sample`, or :func:`show_character_table_sample`.
    """
    return sorted(p.stem for p in _samples_dir().glob("*.xyz"))


def load_sample(name: str | None = None) -> Structure:
    """Load a sample molecule as a :class:`~src.Structure`.

    Parameters
    ----------
    name:
        Stem of the XYZ file (e.g. ``"benzene"``, ``"water"``).
        If *None* a molecule is chosen at random.
    """
    samples = _samples_dir()
    if name is None:
        path = random.choice(list(samples.glob("*.xyz")))
    else:
        path = samples / f"{name}.xyz"
        if not path.is_file():
            available = ", ".join(list_sample_molecules())
            raise FileNotFoundError(
                f"No sample molecule named '{name}'. Available: {available}"
            )
    return Structure(str(path))


def analyse_sample(name: str | None = None) -> "Symmetry":  # noqa: F821
    """Run the full symmetry-determination pipeline on a sample molecule and print the result.

    Parameters
    ----------
    name:
        Stem of the XYZ file (e.g. ``"ammonia"``).
        If *None* a molecule is chosen at random.

    Returns
    -------
    Symmetry
        The completed :class:`~src.Symmetry` object for further inspection.
    """
    from .symmetry import Symmetry
    structure = load_sample(name)
    print(f"Molecule : {structure.description}")
    sym = Symmetry(structure)
    print(f"Point group : {sym.point_group.label.name}")
    print(f"Rotor class : {sym.rotor_class.name}")
    return sym


def visualize_sample(name: str | None = None) -> None:
    """Open the interactive 3-D viewer for a sample molecule.

    Requires the visualizer optional dependency (``pip install 'pyrrhotite[vis]'``).

    Parameters
    ----------
    name:
        Stem of the XYZ file (e.g. ``"buckminsterfullerene"``).
        If *None* a molecule is chosen at random.
    """
    from .visualizer import visualize as _vis
    structure = load_sample(name)
    print(f"Visualising: {structure.description}")
    _vis(structure)


def show_character_table_sample(name: str | None = None) -> None:
    """Print the character table for the point group of a sample molecule.

    Parameters
    ----------
    name:
        Stem of the XYZ file (e.g. ``"benzene"``).
        If *None* a molecule is chosen at random.
    """
    from .character_tables import print_character_table_for
    from .symmetry import Symmetry
    structure = load_sample(name)
    print(f"Molecule : {structure.description}")
    sym = Symmetry(structure)
    group_name = sym.point_group.label.name
    print(f"Point group : {group_name}\n")
    print_character_table_for(group_name)
