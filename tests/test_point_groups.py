"""Unit tests for point group data: POINT_GROUPS list, PointGroup matching."""

import pytest

from schoenflies.operations.operation import Operation
from schoenflies.operations.operation_label import OperationLabel
from schoenflies.point_groups.point_group_label import PointGroupLabel
from schoenflies.point_groups.point_groups import POINT_GROUPS

E = OperationLabel.Element
PGC = PointGroupLabel.Class


# ------------------------------------------------------------------
# POINT_GROUPS list integrity
# ------------------------------------------------------------------

def test_point_groups_count():
    assert len(POINT_GROUPS) >= 54, f"Expected ≥54 point groups, got {len(POINT_GROUPS)}"


def test_point_groups_no_duplicate_labels():
    names = [pg.get_label().get_name() for pg in POINT_GROUPS]
    assert len(names) == len(set(names)), "Duplicate point group labels found"


def test_point_groups_orders_positive():
    # infinite groups (C∞v, D∞h) have order=0 by convention
    for pg in POINT_GROUPS:
        if not pg.get_label().is_linear():
            assert pg.get_order() > 0, f"{pg.get_label().get_name()} has order 0"


def test_character_table_dimensions():
    """Each character table must have as many rows as irreps; columns must be consistent."""
    for pg in POINT_GROUPS:
        name = pg.get_label().get_name()
        irreps = pg.get_irreps()
        chars = pg.get_characters()
        assert len(chars) == len(irreps), \
            f"{name}: {len(chars)} char rows but {len(irreps)} irreps"
        # all rows must have the same number of columns
        if chars:
            col_count = len(chars[0])
            for i, row in enumerate(chars):
                assert len(row) == col_count, \
                    f"{name} irrep {i}: inconsistent column count"


def test_c1_has_order_1():
    c1 = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "C1")
    assert c1.get_order() == 1


def test_oh_has_order_48():
    oh = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "Oh")
    assert oh.get_order() == 48


def test_ih_has_order_120():
    ih = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "Ih")
    assert ih.get_order() == 120


def test_td_has_order_24():
    td = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "Td")
    assert td.get_order() == 24


# ------------------------------------------------------------------
# compare_to_symmetry_operations
# ------------------------------------------------------------------

def _make_ops(*specs) -> list[Operation]:
    """Build a list of Operations from (element, degree, axis) or (element,) tuples."""
    import numpy as np
    ops = []
    for spec in specs:
        if spec[0] == E.Inversion:
            ops.append(Operation.inversion())
        elif spec[0] == E.Reflection:
            ops.append(Operation.reflection(spec[1]))
        else:
            ops.append(Operation.rotation(spec[0], spec[1], spec[2]))
    return ops


def test_c1_matches_empty_operations():
    """C1 requires no operations beyond E — any list has zero surplus."""
    import numpy as np
    c1 = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "C1")
    result = c1.compare_to_symmetry_operations([])
    assert result == 0


def test_ci_requires_inversion():
    import numpy as np
    ci = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "Ci")
    # without inversion → -1
    assert ci.compare_to_symmetry_operations([]) == -1
    # with inversion → 0 surplus
    ops = [Operation.inversion()]
    assert ci.compare_to_symmetry_operations(ops) == 0


def test_cs_requires_reflection():
    import numpy as np
    cs = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "Cs")
    assert cs.compare_to_symmetry_operations([]) == -1
    ops = [Operation.reflection(np.array([0.0, 0.0, 1.0]))]
    assert cs.compare_to_symmetry_operations(ops) == 0


def test_c2v_requires_c2_and_two_reflections():
    import numpy as np
    c2v = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "C2v")
    # missing everything
    assert c2v.compare_to_symmetry_operations([]) == -1
    # only C2 — still missing reflections
    ops = [Operation.rotation(E.ProperRotation, 2, np.array([0.0, 0.0, 1.0]))]
    assert c2v.compare_to_symmetry_operations(ops) == -1
    # C2 + two reflections → 0 surplus
    ops += [
        Operation.reflection(np.array([1.0, 0.0, 0.0])),
        Operation.reflection(np.array([0.0, 1.0, 0.0])),
    ]
    assert c2v.compare_to_symmetry_operations(ops) == 0


def test_surplus_operations_counted():
    """Extra operations that aren't required are counted as surplus."""
    import numpy as np
    c1 = next(pg for pg in POINT_GROUPS if pg.get_label().get_name() == "C1")
    ops = [Operation.inversion()]  # C1 doesn't need inversion
    result = c1.compare_to_symmetry_operations(ops)
    assert result == 1
