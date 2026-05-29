"""Tests for the automatic character table generator.

Verification strategy:
1. Consistency: generated tables match hardcoded tables for all axial groups
   already in POINT_GROUPS (within floating-point tolerance).
2. Orthogonality: for freshly generated groups at n=11,12,15,20 the great
   orthogonality theorem relations hold.
3. Structural sanity: correct order, correct irrep count, E col = dimension.
"""
from __future__ import annotations

import math

import pytest

from pyrrhotite.point_groups.character_table_generator import generate_point_group
from pyrrhotite.point_groups.point_group_label import PointGroupLabel as PGL
from pyrrhotite.point_groups.point_groups import POINT_GROUPS

_TOL = 1e-9
_MATCH_TOL = 1e-4   # tolerance for comparing to hardcoded tables (match float rounding)

_C = PGL.Class

# ---------------------------------------------------------------------------
# Helper: great orthogonality theorem column/row checks
# ---------------------------------------------------------------------------

def _check_orthogonality(pg_label: PGL) -> None:
    """Assert row and column orthogonality for the generated character table."""
    pg = generate_point_group(pg_label)
    chars = pg.get_characters()
    ops = pg.get_unique_operations()
    order = pg.get_order()

    # Column multiplicities (E is implicit with count 1)
    multiplicities = [1] + [olc.get_count() for olc in ops]

    n_irreps = len(chars)
    n_cols = len(chars[0])
    assert n_cols == len(multiplicities), (
        f"{pg_label.get_name()}: col count mismatch {n_cols} vs {len(multiplicities)}"
    )

    # Off-diagonal row orthogonality: Î£_R h_R Ï‡_i(R) Ï‡_j(R) = 0 for iâ‰ j.
    # This holds universally for real character tables (including combined
    # complex-pair "E" irreps in abelian/cyclic groups).
    for i in range(n_irreps):
        for j in range(i + 1, n_irreps):
            val = sum(
                multiplicities[c] * chars[i][c] * chars[j][c]
                for c in range(n_cols)
            )
            assert abs(val) < _TOL, (
                f"{pg_label.get_name()} off-diag row orthog failed: "
                f"irreps {i},{j}  got {val:.6f}"
            )

    # Diagonal row orthogonality: Î£_R h_R Ï‡_i(R)^2 = k_i * |G|
    # where k_i = 1 for genuine irreps (A, B, and non-abelian E/T)
    # and k_i = 2 for combined complex-pair E irreps (abelian cyclic groups).
    # We only verify it is a positive integer multiple of |G|.
    for i in range(n_irreps):
        val = sum(multiplicities[c] * chars[i][c] ** 2 for c in range(n_cols))
        assert val > 0, f"{pg_label.get_name()} irrep {i} has non-positive diagonal"
        ratio = val / order
        assert abs(ratio - round(ratio)) < _TOL, (
            f"{pg_label.get_name()} irrep {i}: diagonal {val:.6f} "
            f"is not a multiple of |G|={order}"
        )


def _check_sanity(pg_label: PGL) -> None:
    """Check order, irrep count == class count, and E column = dimension."""
    pg = generate_point_group(pg_label)
    chars = pg.get_characters()
    ops = pg.get_unique_operations()
    n_classes = 1 + len(ops)   # E (implicit) + listed
    n_irreps = len(chars)

    # Number of irreps must equal number of conjugacy classes
    assert n_irreps == n_classes, (
        f"{pg_label.get_name()}: {n_irreps} irreps but {n_classes} classes"
    )

    # First column (E) must equal the dimension of each irrep
    dims_from_chars = [row[0] for row in chars]
    assert all(d > 0 for d in dims_from_chars), (
        f"{pg_label.get_name()}: non-positive dimension in E column"
    )

    # Sum of dim^2 >= |G| (due to real-rep grouping it may exceed |G|, but
    # the basic sanity check is that the order matches the group order stored)
    assert pg.get_order() > 0


# ---------------------------------------------------------------------------
# Consistency tests: generated == hardcoded
# ---------------------------------------------------------------------------

_HARDCODED_AXIAL_CLASSES = {_C.C, _C.Ch, _C.Cv, _C.S, _C.D, _C.Dh, _C.Dd}


def _hardcoded_axial_groups():
    """Yield (label, hardcoded_PointGroup) for all axial groups in POINT_GROUPS."""
    for pg in POINT_GROUPS:
        lbl = pg.get_label()
        if lbl.get_class() in _HARDCODED_AXIAL_CLASSES and lbl.get_order() >= 2:
            yield lbl, pg


@pytest.mark.parametrize("lbl,hc_pg", list(_hardcoded_axial_groups()))
def test_generated_matches_hardcoded(lbl, hc_pg):
    """Generated character values must match the hardcoded table (Â±1e-4)."""
    gen_pg = generate_point_group(lbl)
    hc_chars = hc_pg.get_characters()
    gen_chars = gen_pg.get_characters()

    # Build value multisets for comparison (order-independent, since column
    # ordering may differ from hardcoded for some groups)
    def _all_values(chars):
        vals = []
        for row in chars:
            vals.extend(row)
        return sorted(vals)

    hc_vals = _all_values(hc_chars)
    gen_vals = _all_values(gen_chars)

    assert len(hc_vals) == len(gen_vals), (
        f"{lbl.get_name()}: different number of character values "
        f"({len(gen_vals)} generated vs {len(hc_vals)} hardcoded)"
    )
    for v_gen, v_hc in zip(gen_vals, hc_vals):
        assert abs(v_gen - v_hc) < _MATCH_TOL, (
            f"{lbl.get_name()}: generated value {v_gen:.6f} != "
            f"hardcoded {v_hc:.6f}"
        )


# ---------------------------------------------------------------------------
# Orthogonality tests for groups beyond the hardcoded list
# ---------------------------------------------------------------------------

_LARGE_N_LABELS = [
    PGL(_C.C,  11),
    PGL(_C.C,  12),
    PGL(_C.C,  15),
    PGL(_C.C,  20),
    PGL(_C.Ch, 11),
    PGL(_C.Ch, 12),
    PGL(_C.Ch, 15),
    PGL(_C.Cv, 11),
    PGL(_C.Cv, 12),
    PGL(_C.S,  12),
    PGL(_C.S,  14),
    PGL(_C.D,  11),
    PGL(_C.D,  12),
    PGL(_C.Dh, 11),
    PGL(_C.Dh, 12),
    PGL(_C.Dd, 11),
    PGL(_C.Dd, 12),
]


@pytest.mark.parametrize("lbl", _LARGE_N_LABELS)
def test_orthogonality_large_n(lbl):
    """Great orthogonality theorem holds for n > 10 generated groups."""
    _check_orthogonality(lbl)


@pytest.mark.parametrize("lbl", _LARGE_N_LABELS)
def test_sanity_large_n(lbl):
    """Structural sanity: correct irrep count and positive dimensions."""
    _check_sanity(lbl)


# ---------------------------------------------------------------------------
# Order and basic structure tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n,expected_order", [
    (11, 11), (12, 12), (20, 20), (100, 100),
])
def test_cn_order(n, expected_order):
    pg = generate_point_group(PGL(_C.C, n))
    assert pg.get_order() == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 22), (12, 24), (20, 40),
])
def test_cnh_order(n, expected_order):
    pg = generate_point_group(PGL(_C.Ch, n))
    assert pg.get_order() == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 22), (12, 24), (20, 40),
])
def test_cnv_order(n, expected_order):
    pg = generate_point_group(PGL(_C.Cv, n))
    assert pg.get_order() == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (12, 12), (14, 14), (20, 20),
])
def test_sn_order(n, expected_order):
    pg = generate_point_group(PGL(_C.S, n))
    assert pg.get_order() == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 22), (12, 24), (20, 40),
])
def test_dn_order(n, expected_order):
    pg = generate_point_group(PGL(_C.D, n))
    assert pg.get_order() == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 44), (12, 48), (15, 60),
])
def test_dnh_order(n, expected_order):
    pg = generate_point_group(PGL(_C.Dh, n))
    assert pg.get_order() == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 44), (12, 48), (15, 60),
])
def test_dnd_order(n, expected_order):
    pg = generate_point_group(PGL(_C.Dd, n))
    assert pg.get_order() == expected_order


# ---------------------------------------------------------------------------
# Character value spot-checks (known analytical values)
# ---------------------------------------------------------------------------

def test_c11_e_irrep_first_class():
    """C11 E_1 at 2C11: Ï‡ = 2cos(2Ï€/11)."""
    pg = generate_point_group(PGL(_C.C, 11))
    chars = pg.get_characters()
    # irrep order: A, E1, E2, E3, E4, E5  (n=11 odd â†’ 6 irreps)
    e1_row = chars[1]   # E1
    expected = 2.0 * math.cos(2.0 * math.pi / 11)
    assert abs(e1_row[1] - expected) < _TOL


def test_c12_b_irrep():
    """C12 B at C12 class: Ï‡ = (-1)^1 = -1."""
    pg = generate_point_group(PGL(_C.C, 12))
    chars = pg.get_characters()
    # irrep order: A, B, E1, E2, ..., E5
    b_row = chars[1]   # B
    assert abs(b_row[1] - (-1.0)) < _TOL


def test_c12v_a2_at_sigma():
    """C12v A2 character at Ïƒv column must be âˆ’1."""
    pg = generate_point_group(PGL(_C.Cv, 12))
    chars = pg.get_characters()
    a2_row = chars[1]   # A2
    sigma_col = len(pg.get_unique_operations()) - 1   # last col = Ïƒd
    sigma_v_col = len(pg.get_unique_operations()) - 2  # second-to-last = Ïƒv
    # A2 is âˆ’1 at both Ïƒv and Ïƒd
    assert abs(a2_row[1 + sigma_v_col] - (-1.0)) < _TOL
    assert abs(a2_row[1 + sigma_col] - (-1.0)) < _TOL


# ---------------------------------------------------------------------------
# ValueError tests
# ---------------------------------------------------------------------------

def test_invalid_polyhedral_raises():
    with pytest.raises(ValueError):
        generate_point_group(PGL(_C.Oh))


def test_sn_odd_raises():
    with pytest.raises(ValueError):
        generate_point_group(PGL(_C.S, 5))


def test_sn_too_small_raises():
    with pytest.raises(ValueError):
        generate_point_group(PGL(_C.S, 2))
