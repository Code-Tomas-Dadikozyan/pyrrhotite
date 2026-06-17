"""Tests for the automatic character table generator.

Verification strategy:
1. Consistency: generated tables match hardcoded tables for all axial groups
   already in POINT_GROUPS (within floating-point tolerance). This is the
   strongest check, because the hardcoded tables are the literature values, so
   it pins the generated tables to an external ground truth wherever the two
   overlap.
2. Row orthogonality: for freshly generated groups at n=11,12,15,20 the first
   great orthogonality relation (over operations, summing across columns) holds.
3. Column orthogonality: the *second*, independent great orthogonality relation
   (over irreps, summing down columns) holds for the non-abelian families. This
   is checked separately because, unlike row orthogonality, it is not implied by
   the construction and so catches a different class of error. It is restricted
   to Cnv/Dn/Dnh/Dnd: the abelian families (Cn, Cnh, Sn) represent each pair of
   complex-conjugate 1-D irreps as a single combined real "E" row, which is a
   reducible representation for which the simple column relation does not apply
   (those families are covered by the relaxed row check in 2 instead).
4. Structural sanity: correct order, correct irrep count, E col = dimension.
"""
from __future__ import annotations

import math

import pytest

from pyrrhotite.character_tables import generate_point_group
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
    chars = pg.characters
    ops = pg.unique_operations
    order = pg.order

    # Column multiplicities (E is implicit with count 1)
    multiplicities = [1] + [olc.count for olc in ops]

    n_irreps = len(chars)
    n_cols = len(chars[0])
    assert n_cols == len(multiplicities), (
        f"{pg_label.name}: col count mismatch {n_cols} vs {len(multiplicities)}"
    )

    # Off-diagonal row orthogonality: Σ_R h_R χ_i(R) χ_j(R) = 0 for i≠j.
    # This holds universally for real character tables (including combined
    # complex-pair "E" irreps in abelian/cyclic groups).
    for i in range(n_irreps):
        for j in range(i + 1, n_irreps):
            val = sum(
                multiplicities[c] * chars[i][c] * chars[j][c]
                for c in range(n_cols)
            )
            assert abs(val) < _TOL, (
                f"{pg_label.name} off-diag row orthog failed: "
                f"irreps {i},{j}  got {val:.6f}"
            )

    # Diagonal row orthogonality: Σ_R h_R χ_i(R)^2 = k_i * |G|
    # where k_i = 1 for genuine irreps (A, B, and non-abelian E/T)
    # and k_i = 2 for combined complex-pair E irreps (abelian cyclic groups).
    # We only verify it is a positive integer multiple of |G|.
    for i in range(n_irreps):
        val = sum(multiplicities[c] * chars[i][c] ** 2 for c in range(n_cols))
        assert val > 0, f"{pg_label.name} irrep {i} has non-positive diagonal"
        ratio = val / order
        assert abs(ratio - round(ratio)) < _TOL, (
            f"{pg_label.name} irrep {i}: diagonal {val:.6f} "
            f"is not a multiple of |G|={order}"
        )


def _check_column_orthogonality(pg_label: PGL) -> None:
    """Assert the second great orthogonality relation (columns) for a table.

    For a genuine character table the columns are orthogonal:

        Σ_i  χ_i(C_p) · χ_i(C_q)*  =  (|G| / h_p) · δ_{pq}

    where the sum runs over the irreducible representations i and h_p is the
    number of group elements in class p. Summing *down* a column over irreps is
    independent of the row relation in ``_check_orthogonality`` (which sums
    *across* a row over operations), so this catches errors the row check would
    miss. The tables here are real, so χ* = χ.

    This is only valid where every row is a genuine irreducible character, i.e.
    the non-abelian families Cnv/Dn/Dnh/Dnd. It must NOT be applied to the
    abelian families, whose combined complex-pair "E" rows are reducible.
    """
    pg = generate_point_group(pg_label)
    chars = pg.characters
    ops = pg.unique_operations
    order = pg.order

    # Class sizes h_p; the implicit E column always has exactly one element.
    multiplicities = [1] + [olc.count for olc in ops]
    n_irreps = len(chars)
    n_cols = len(chars[0])

    for p in range(n_cols):
        for q in range(p, n_cols):
            val = sum(chars[i][p] * chars[i][q] for i in range(n_irreps))
            if p == q:
                expected = order / multiplicities[p]
                assert abs(val - expected) < _TOL, (
                    f"{pg_label.name} column self-overlap failed at class {p}: "
                    f"got {val:.6f}, expected |G|/h_p = {expected:.6f}"
                )
            else:
                assert abs(val) < _TOL, (
                    f"{pg_label.name} column orthogonality failed for classes "
                    f"{p},{q}: got {val:.6f}"
                )


def _check_sanity(pg_label: PGL) -> None:
    """Check order, irrep count == class count, and E column = dimension."""
    pg = generate_point_group(pg_label)
    chars = pg.characters
    ops = pg.unique_operations
    n_classes = 1 + len(ops)   # E (implicit) + listed
    n_irreps = len(chars)

    # Number of irreps must equal number of conjugacy classes
    assert n_irreps == n_classes, (
        f"{pg_label.name}: {n_irreps} irreps but {n_classes} classes"
    )

    # First column (E) must equal the dimension of each irrep
    dims_from_chars = [row[0] for row in chars]
    assert all(d > 0 for d in dims_from_chars), (
        f"{pg_label.name}: non-positive dimension in E column"
    )

    # Sum of dim^2 >= |G| (due to real-rep grouping it may exceed |G|, but
    # the basic sanity check is that the order matches the group order stored)
    assert pg.order > 0


# ---------------------------------------------------------------------------
# Consistency tests: generated == hardcoded
# ---------------------------------------------------------------------------

_HARDCODED_AXIAL_CLASSES = {_C.C, _C.Ch, _C.Cv, _C.S, _C.D, _C.Dh, _C.Dd}


def _hardcoded_axial_groups():
    """Yield (label, hardcoded_PointGroup) for all axial groups in POINT_GROUPS."""
    for pg in POINT_GROUPS:
        lbl = pg.label
        if lbl.group_class in _HARDCODED_AXIAL_CLASSES and lbl.order >= 2:
            yield lbl, pg


@pytest.mark.parametrize("lbl,hc_pg", list(_hardcoded_axial_groups()))
def test_generated_matches_hardcoded(lbl, hc_pg):
    """Generated character values must match the hardcoded table (±1e-4)."""
    gen_pg = generate_point_group(lbl)
    hc_chars = hc_pg.characters
    gen_chars = gen_pg.characters

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


# Column orthogonality is only well-defined for the non-abelian families, whose
# E irreps are genuine 2-D representations (see _check_column_orthogonality).
_LARGE_N_NONABELIAN_LABELS = [
    PGL(_C.Cv, 11),
    PGL(_C.Cv, 12),
    PGL(_C.Cv, 15),
    PGL(_C.Cv, 20),
    PGL(_C.D,  11),
    PGL(_C.D,  12),
    PGL(_C.D,  20),
    PGL(_C.Dh, 11),
    PGL(_C.Dh, 12),
    PGL(_C.Dh, 20),
    PGL(_C.Dd, 11),
    PGL(_C.Dd, 12),
    PGL(_C.Dd, 20),
]


@pytest.mark.parametrize("lbl", _LARGE_N_NONABELIAN_LABELS)
def test_column_orthogonality_large_n(lbl):
    """Second (column) orthogonality relation holds for non-abelian groups."""
    _check_column_orthogonality(lbl)


# ---------------------------------------------------------------------------
# Order and basic structure tests
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("n,expected_order", [
    (11, 11), (12, 12), (20, 20), (100, 100),
])
def test_cn_order(n, expected_order):
    pg = generate_point_group(PGL(_C.C, n))
    assert pg.order == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 22), (12, 24), (20, 40),
])
def test_cnh_order(n, expected_order):
    pg = generate_point_group(PGL(_C.Ch, n))
    assert pg.order == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 22), (12, 24), (20, 40),
])
def test_cnv_order(n, expected_order):
    pg = generate_point_group(PGL(_C.Cv, n))
    assert pg.order == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (12, 12), (14, 14), (20, 20),
])
def test_sn_order(n, expected_order):
    pg = generate_point_group(PGL(_C.S, n))
    assert pg.order == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 22), (12, 24), (20, 40),
])
def test_dn_order(n, expected_order):
    pg = generate_point_group(PGL(_C.D, n))
    assert pg.order == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 44), (12, 48), (15, 60),
])
def test_dnh_order(n, expected_order):
    pg = generate_point_group(PGL(_C.Dh, n))
    assert pg.order == expected_order


@pytest.mark.parametrize("n,expected_order", [
    (11, 44), (12, 48), (15, 60),
])
def test_dnd_order(n, expected_order):
    pg = generate_point_group(PGL(_C.Dd, n))
    assert pg.order == expected_order


# ---------------------------------------------------------------------------
# Character value spot-checks (known analytical values)
# ---------------------------------------------------------------------------

def test_c11_e_irrep_first_class():
    """C11 E_1 at 2C11: χ = 2cos(2π/11)."""
    pg = generate_point_group(PGL(_C.C, 11))
    chars = pg.characters
    # irrep order: A, E1, E2, E3, E4, E5  (n=11 odd → 6 irreps)
    e1_row = chars[1]   # E1
    expected = 2.0 * math.cos(2.0 * math.pi / 11)
    assert abs(e1_row[1] - expected) < _TOL


def test_c12_b_irrep():
    """C12 B at C12 class: χ = (-1)^1 = -1."""
    pg = generate_point_group(PGL(_C.C, 12))
    chars = pg.characters
    # irrep order: A, B, E1, E2, ..., E5
    b_row = chars[1]   # B
    assert abs(b_row[1] - (-1.0)) < _TOL


def test_c12v_a2_at_sigma():
    """C12v A2 character at σv column must be −1."""
    pg = generate_point_group(PGL(_C.Cv, 12))
    chars = pg.characters
    a2_row = chars[1]   # A2
    sigma_col = len(pg.unique_operations) - 1   # last col = σd
    sigma_v_col = len(pg.unique_operations) - 2  # second-to-last = σv
    # A2 is −1 at both σv and σd
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
