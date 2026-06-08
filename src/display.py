"""display.py — Pretty-print helpers for structures, operations, and character tables."""

from __future__ import annotations

from .structure import Structure
from .operations.operation import Operation
from .operations.operation_label import OperationLabel
from .periodic_table import element
from .point_groups.point_group import PointGroup
from .point_groups.basis_functions import compute_basis_functions

_SEP = "-" * 60


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
