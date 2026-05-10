"""Unit tests for Structure: XYZ loading, COM centering, closest-index lookup."""

from pathlib import Path

import numpy as np
import pytest

from schoenflies.structure import Structure

XYZ_DIR = Path(__file__).parent / "files"


def test_load_water():
    s = Structure(str(XYZ_DIR / "water.xyz"))
    assert s.num_atoms == 3
    assert len(s.atomic_numbers) == 3
    assert s.coordinates.shape == (3, 3)


def test_com_at_origin_water():
    """After loading, the centre of mass must be at the origin."""
    s = Structure(str(XYZ_DIR / "water.xyz"))
    from schoenflies.periodic_table import get_element
    masses = np.array([get_element(int(z)).mass for z in s.atomic_numbers])
    com = np.average(s.coordinates, axis=0, weights=masses)
    np.testing.assert_allclose(com, np.zeros(3), atol=1e-10)


def test_com_at_origin_buckminsterfullerene():
    s = Structure(str(XYZ_DIR / "buckminsterfullerene.xyz"))
    from schoenflies.periodic_table import get_element
    masses = np.array([get_element(int(z)).mass for z in s.atomic_numbers])
    com = np.average(s.coordinates, axis=0, weights=masses)
    np.testing.assert_allclose(com, np.zeros(3), atol=1e-10)


def test_atomic_numbers_water():
    """Water: O=8, H=1, H=1."""
    s = Structure(str(XYZ_DIR / "water.xyz"))
    assert set(s.atomic_numbers.tolist()) == {1, 8}
    assert (s.atomic_numbers == 8).sum() == 1
    assert (s.atomic_numbers == 1).sum() == 2


def test_find_closest_index():
    """find_closest_index must return the index of the nearest atom of the given element."""
    s = Structure(str(XYZ_DIR / "water.xyz"))
    # Query the O position itself — must get back the O index.
    o_idx = int(np.where(s.atomic_numbers == 8)[0][0])
    result = s.find_closest_index(s.coordinates[o_idx], 8)
    assert result == o_idx


def test_calculate_bond_pairs_water():
    """Water has exactly two O-H bonds."""
    s = Structure(str(XYZ_DIR / "water.xyz"))
    pairs = s.calculate_bond_pairs()
    assert len(pairs) == 2
    for i, j in pairs:
        elements = {int(s.atomic_numbers[i]), int(s.atomic_numbers[j])}
        assert elements == {1, 8}


def test_unsupported_format():
    with pytest.raises(RuntimeError, match="not supported"):
        Structure("molecule.pdb")


def test_description_filename():
    s = Structure(str(XYZ_DIR / "water.xyz"))
    label = s.get_description_filename()
    assert "water.xyz" in label
