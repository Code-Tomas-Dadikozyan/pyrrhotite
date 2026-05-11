"""
Command-line interface for Schoenflies point group determination.

Usage:
    schoenflies molecule.xyz
    schoenflies mol1.xyz mol2.xyz ...
    python -m schoenflies molecule.xyz
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .structure import Structure
from .symmetry import Symmetry


def _analyse(path: Path, verbose: bool) -> int:
    """Run the pipeline on one file; return 0 on success, 1 on error."""
    try:
        structure = Structure(str(path))
        sym = Symmetry(structure)
        pg = sym.get_point_group()
        label = pg.get_label().get_name()

        if verbose:
            ops = sym.get_operation_manager().get_operations()
            print(f"{path.name}")
            print(f"  Point group : {label}")
            print(f"  Rotor class : {sym.get_rotor_class().name}")
            print(f"  Operations  : {len(ops)} found")
            for op in ops:
                print(f"    {op.get_label().get_short_name()}")
        else:
            print(f"{path.name}: {label}")

    except Exception as exc:
        print(f"ERROR {path.name}: {exc}", file=sys.stderr)
        return 1

    return 0


def main() -> None:
    """Entry point for the schoenflies command."""
    parser = argparse.ArgumentParser(
        prog="schoenflies",
        description="Determine the Schoenflies point group of a molecule from an XYZ file.",
    )
    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="+",
        help="XYZ file(s) to analyse",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show rotor class and all found symmetry operations",
    )

    args = parser.parse_args()

    exit_code = 0
    for filename in args.files:
        code = _analyse(Path(filename), verbose=args.verbose)
        if code != 0:
            exit_code = code

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
