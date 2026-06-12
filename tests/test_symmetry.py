"""Integration tests: full Symmetry pipeline against all 32 reference molecules."""

from pathlib import Path

import numpy as np
import pytest

from pyrrhotite.structure import Structure
from pyrrhotite.symmetry import Symmetry
from pyrrhotite.rotor_class import RotorClass

from .conftest import EXPECTED_POINT_GROUPS

XYZ_DIR = Path(__file__).parent.parent / "src" / "sample_molecules"


# ------------------------------------------------------------------
# Parametrized point group integration tests
# ------------------------------------------------------------------

@pytest.mark.parametrize("filename,expected", list(EXPECTED_POINT_GROUPS.items()))
def test_point_group(filename: str, expected: str) -> None:
    """Symmetry(Structure(xyz)) must identify the correct Schoenflies symbol."""
    path = XYZ_DIR / filename
    s = Structure(str(path))
    sym = Symmetry(s)
    result = sym.point_group.label.name
    assert result == expected, f"{filename}: expected {expected}, got {result}"


# ------------------------------------------------------------------
# Rotor class spot checks
# ------------------------------------------------------------------

@pytest.mark.parametrize("filename,expected_rotor", [
    ("carbon-dioxide.xyz",       RotorClass.Linear),
    ("hydrogen-chloride.xyz",    RotorClass.Linear),
    ("sulfur-hexafluoride.xyz",  RotorClass.SphericalTop),
    ("methane.xyz",              RotorClass.SphericalTop),
    ("buckminsterfullerene.xyz", RotorClass.SphericalTop),
])
def test_rotor_class(filename: str, expected_rotor: RotorClass) -> None:
    s = Structure(str(XYZ_DIR / filename))
    sym = Symmetry(s)
    assert sym.rotor_class == expected_rotor, \
        f"{filename}: expected {expected_rotor}, got {sym.rotor_class}"


# ------------------------------------------------------------------
# Cartesian axis sanity
# ------------------------------------------------------------------

@pytest.mark.parametrize("filename", [
    "water.xyz", "ammonia.xyz", "benzene.xyz", "methane.xyz",
])
def test_cartesian_axes_orthonormal(filename: str) -> None:
    """x, y, z axes must be mutually orthogonal unit vectors."""
    s = Structure(str(XYZ_DIR / filename))
    sym = Symmetry(s)
    x, y, z = sym.x_axis, sym.y_axis, sym.z_axis
    np.testing.assert_allclose(np.linalg.norm(x), 1.0, atol=1e-6, err_msg=f"{filename}: x not unit")
    np.testing.assert_allclose(np.linalg.norm(y), 1.0, atol=1e-6, err_msg=f"{filename}: y not unit")
    np.testing.assert_allclose(np.linalg.norm(z), 1.0, atol=1e-6, err_msg=f"{filename}: z not unit")
    np.testing.assert_allclose(np.dot(x, y), 0.0, atol=1e-6, err_msg=f"{filename}: x·y ≠ 0")
    np.testing.assert_allclose(np.dot(x, z), 0.0, atol=1e-6, err_msg=f"{filename}: x·z ≠ 0")
    np.testing.assert_allclose(np.dot(y, z), 0.0, atol=1e-6, err_msg=f"{filename}: y·z ≠ 0")


# ------------------------------------------------------------------
# Principal moments sanity
# ------------------------------------------------------------------

def test_principal_moments_ascending():
    """eigh guarantees ascending eigenvalues."""
    s = Structure(str(XYZ_DIR / "ammonia.xyz"))
    sym = Symmetry(s)
    m = sym.principal_moments
    assert m[0] <= m[1] <= m[2], f"Moments not ascending: {m}"


def test_linear_smallest_moment_near_zero():
    """Linear molecules have Ia ≈ 0."""
    s = Structure(str(XYZ_DIR / "carbon-dioxide.xyz"))
    sym = Symmetry(s)
    assert sym.principal_moments[0] < 0.1, \
        f"CO2 smallest moment not near zero: {sym.principal_moments[0]}"
