"""
test_point_group.py — Full pytest suite for PointGroupClassifier.

Runs the complete Schoenflies pipeline (Molecule → SymmetryFinder → classify)
against every .xyz file in tests/molecules/ and checks the expected symbol.
The expected symbol is embedded in the second line (comment) of each .xyz file,
surrounded by parentheses as the last token: e.g. "(D6h)".
"""

import os
import re
import pytest

from schoenflies.molecule import Molecule
from schoenflies.symmetry_elements import SymmetryFinder
from schoenflies.point_group import PointGroupClassifier

_MOLECULES_DIR = os.path.join(os.path.dirname(__file__), "molecules")

# Molecules excluded from the test suite due to corrupt coordinate data in
# the original C++ repository's test files.  They are kept in the directory
# for reference but cannot be used for automated verification.
_EXCLUDED = {"adamantane"}  # corrupt H coordinate (5.675 Å from origin)


def _expected_symbol(xyz_path: str) -> str:
    """Extract the expected point group from the XYZ comment line."""
    with open(xyz_path) as f:
        f.readline()               # atom count
        comment = f.readline()    # comment line
    match = re.search(r'\(([A-Za-z0-9_]+)\)\s*$', comment.strip())
    if match is None:
        raise ValueError("No point group found in comment of %s" % xyz_path)
    raw = match.group(1)
    # Normalise: inf → _inf_ (already written as D_inf_h / C_inf_v in files)
    return raw


def _collect_xyz_files():
    """Return list of (xyz_path, expected_symbol) for all test molecules."""
    cases = []
    for fname in sorted(os.listdir(_MOLECULES_DIR)):
        if not fname.endswith(".xyz"):
            continue
        stem = fname[:-4]
        if stem in _EXCLUDED:
            continue
        path = os.path.join(_MOLECULES_DIR, fname)
        try:
            sym = _expected_symbol(path)
        except ValueError:
            continue
        cases.append(pytest.param(path, sym, id=stem))
    return cases


@pytest.mark.parametrize("xyz_path,expected", _collect_xyz_files())
def test_point_group(xyz_path, expected):
    mol = Molecule(xyz_path)
    sf  = SymmetryFinder(mol)
    sf.find_all()
    pgc = PointGroupClassifier(mol, sf)
    got = pgc.classify()
    assert got == expected, "%-40s  expected %s, got %s" % (
        os.path.basename(xyz_path), expected, got
    )
