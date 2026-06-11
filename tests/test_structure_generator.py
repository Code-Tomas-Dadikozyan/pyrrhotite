"""Tests for the idealized structure generator (src/structure_generator.py)."""

import pytest

from pyrrhotite.structure_generator import generate_idealized_structure
from pyrrhotite.symmetry import Symmetry

# Representative sample spanning all seven axial families and a range of
# orders, including n > 8 to exercise the adaptive axis-order search
# (Symmetry._MAX_AXIS_ORDER) and the tightened high-degree tolerance.
ROUND_TRIP_NAMES = [
    "C3", "C5", "C9",
    "C4h", "C5h", "C9h",
    "C3v", "C5v", "C10v",
    "S4", "S6", "S8",
    "D3", "D5", "D9",
    "D3h", "D5h", "D9h",
    "D3d", "D5d", "D9d",
]


@pytest.mark.parametrize("name", ROUND_TRIP_NAMES)
def test_round_trip(name: str) -> None:
    """Symmetry(generate_idealized_structure(name)) must recover the requested label."""
    structure = generate_idealized_structure(name)
    sym = Symmetry(structure)
    result = sym.point_group.label.name
    assert result == name, f"{name}: expected {name}, got {result}"


@pytest.mark.parametrize("name", ["C2", "D2", "C2v", "S2"])
def test_order_too_low_raises(name: str) -> None:
    """n < 3 (or n < 4 for Sn) is out of scope for the ring-based generator."""
    with pytest.raises(ValueError):
        generate_idealized_structure(name)


@pytest.mark.parametrize("name", ["S5", "S7"])
def test_sn_odd_order_raises(name: str) -> None:
    """Sn requires an even order n >= 4."""
    with pytest.raises(ValueError):
        generate_idealized_structure(name)


@pytest.mark.parametrize("name", ["Td", "Oh", "Ih", "Cs", "Ci", "C∞v", "D∞h"])
def test_non_axial_group_raises(name: str) -> None:
    """Only the seven axial families (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd) are supported."""
    with pytest.raises(ValueError):
        generate_idealized_structure(name)
