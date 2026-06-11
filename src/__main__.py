"""
Command-line interface for Schoenflies point group determination.

Usage:
    pyrrhotite molecule.xyz
    pyrrhotite mol1.xyz mol2.xyz ...
    pyrrhotite -g C3v
    python -m pyrrhotite molecule.xyz
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from .structure import Structure
from .symmetry import Symmetry
from .periodic_table import get_element
from .operations.operation_label import OperationLabel
from .character_tables import get_or_generate_point_group
from .structure_generator import generate_idealized_structure, format_xyz, write_xyz


def _print_group(name: str, *, use_complex: bool, plain: bool) -> int:
    """Print the character table for a named point group; return 0 on success, 1 on error."""
    try:
        pg = get_or_generate_point_group(name)
    except ValueError as exc:
        print(f"ERROR: unrecognised point group '{name}': {exc}", file=sys.stderr)
        return 1

    if pg is None:
        print(f"ERROR: could not generate character table for '{name}'", file=sys.stderr)
        return 1

    pg.print_character_table(complex=use_complex, plain=plain)
    return 0


def _generate_xyz(name: str, path: str) -> int:
    """Generate an idealized structure for *name* and write it as XYZ; return 0/1."""
    try:
        structure = generate_idealized_structure(name)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if path == "-":
        sys.stdout.write(format_xyz(structure))
    else:
        write_xyz(structure, path)
    return 0


def _analyse(
    path: Path,
    verbose: bool,
    character_table: bool,
    use_complex: bool,
    moments: bool,
    operations_detail: bool,
    plain: bool,
) -> int:
    """Run the pipeline on one file; return 0 on success, 1 on error."""
    try:
        structure = Structure(str(path))
        sym = Symmetry(structure)
        pg = sym.point_group
        label = pg.label.name

        if verbose:
            ops = sym.operation_manager.operations
            print(f"{path.name}")
            print(f"  Point group : {label}")
            print(f"  Rotor class : {sym.rotor_class.name}")
            print(f"  Operations  : {len(ops)} found")
            for op in ops:
                print(f"    {op.label.short_name}")
        else:
            print(f"{path.name}: {label}")

        if moments:
            pm = sym.principal_moments
            axes = sym.principal_axes
            print(f"\n  Principal moments of inertia (u·Ų):")
            print(f"    Ia = {pm[0]:.6f}")
            print(f"    Ib = {pm[1]:.6f}")
            print(f"    Ic = {pm[2]:.6f}")
            print(f"\n  Principal axes (columns = x, y, z eigenvectors):")
            labels = ["x", "y", "z"]
            print(f"    {'':8s}  {'x':>12s}  {'y':>12s}  {'z':>12s}")
            for row_idx, row_label in enumerate(labels):
                vals = "  ".join(f"{axes[row_idx, col]:12.6f}" for col in range(3))
                print(f"    {row_label:8s}  {vals}")

        if operations_detail:
            struct = sym.structure
            ops = sym.operation_manager.operations
            print(f"\n  Symmetry operation geometry:")
            for op in ops:
                short = op.label.short_name
                is_reflection = (
                    op.label.element == OperationLabel.Element.Reflection
                )
                if is_reflection:
                    atom_indices = op.atoms_in_plane(struct)
                    location = "in plane"
                else:
                    atom_indices = op.atoms_on_axis(struct)
                    location = "on axis"
                if atom_indices:
                    atom_symbols = [
                        f"{get_element(struct.atomic_numbers[i]).symbol}{i}"
                        for i in atom_indices
                    ]
                    atoms_str = ", ".join(atom_symbols)
                else:
                    atoms_str = "none"
                print(f"    {short:10s}  {location}: {atoms_str}")

        if character_table:
            print()
            pg.print_character_table(complex=use_complex, plain=plain)

    except Exception as exc:
        print(f"ERROR {path.name}: {exc}", file=sys.stderr)
        return 1

    return 0


def main() -> None:
    """Entry point for the pyrrhotite command."""
    # Ensure stdout/stderr can represent Unicode symbols (σ, ′, ″, ε, …) on
    # Windows consoles whose default encoding may not cover them.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
        except (AttributeError, io.UnsupportedOperation):
            pass

    parser = argparse.ArgumentParser(
        prog="pyrrhotite",
        description="Determine the Schoenflies point group of a molecule from an XYZ file.",
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="*",
        help="XYZ file(s) to analyse",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show rotor class and all found symmetry operations",
    )
    parser.add_argument(
        "-ct", "--character-table",
        action="store_true",
        help="Print the full character table (with basis functions) for the determined point group",
    )
    parser.add_argument(
        "--complex",
        action="store_true",
        help="Use ε-notation in the character table (cyclic/Sn groups only); only meaningful with -ct or -g",
    )
    parser.add_argument(
        "-m", "--moments",
        action="store_true",
        help="Show principal moments of inertia and the Cartesian axes matrix",
    )
    parser.add_argument(
        "-od", "--operations-detail",
        action="store_true",
        help="List the atoms lying on each symmetry axis or mirror plane",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Force plain-text output (suppress rich formatting)",
    )
    parser.add_argument(
        "-g", "--group",
        metavar="NAME",
        help="Print the character table for a named group without an XYZ file (e.g. C3v, D6h, Oh)",
    )
    parser.add_argument(
        "--xyz",
        nargs="?",
        const="-",
        metavar="PATH",
        help=(
            "With -g/--group, generate an idealized structure for the named "
            "axial point group (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) and write it "
            "as XYZ to PATH, or to stdout if PATH is omitted"
        ),
    )
    parser.add_argument(
        "--visualize", "-vis",
        action="store_true",
        help=(
            "Open an interactive 3-D viewer after analysis, or (with -g/--group "
            "and without --xyz) for an idealized structure of the named axial "
            "point group (requires pip install 'pyrrhotite[vis]')"
        ),
    )
    parser.add_argument(
        "--labels", "-l",
        action="store_true",
        help="Show element labels on atoms in the 3-D viewer (implies --visualize)",
    )

    args = parser.parse_args()

    # Mutual exclusion: --group and FILE positional args cannot be combined.
    if args.group and args.files:
        parser.error("--group / -g cannot be combined with FILE arguments")
    if args.xyz is not None and not args.group:
        parser.error("--xyz requires -g/--group")
    if not args.group and not args.files:
        parser.print_help()
        sys.exit(1)

    if args.group:
        if args.xyz is not None:
            sys.exit(_generate_xyz(args.group, args.xyz))

        exit_code = _print_group(args.group, use_complex=args.complex, plain=args.plain)

        if exit_code == 0 and (args.visualize or args.labels):
            try:
                structure = generate_idealized_structure(args.group)
            except ValueError as exc:
                print(f"ERROR: {exc}", file=sys.stderr)
                sys.exit(1)
            try:
                from .visualizer import visualize
                visualize(structure, show_labels=args.labels)
            except ImportError:
                print(
                    "ERROR: visualizer dependencies not installed. "
                    "Run:  pip install 'pyrrhotite[vis]'",
                    file=sys.stderr,
                )
                exit_code = 1

        sys.exit(exit_code)

    exit_code = 0
    structures = []
    for filename in args.files:
        code = _analyse(
            Path(filename),
            verbose=args.verbose,
            character_table=args.character_table,
            use_complex=args.complex,
            moments=args.moments,
            operations_detail=args.operations_detail,
            plain=args.plain,
        )
        if code != 0:
            exit_code = code
        elif args.visualize or args.labels:
            try:
                structures.append(Structure(str(Path(filename))))
            except Exception:
                pass

    if (args.visualize or args.labels) and structures:
        try:
            from .visualizer import visualize
            for structure in structures:
                visualize(structure, show_labels=args.labels)
        except ImportError:
            print(
                "ERROR: visualizer dependencies not installed. "
                "Run:  pip install 'pyrrhotite[vis]'",
                file=sys.stderr,
            )
            exit_code = 1

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
