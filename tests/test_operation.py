"""Unit tests for Operation: matrix construction, do_operation, equality."""

from pathlib import Path

import numpy as np
import pytest

from schoenflies.operations.operation import Operation
from schoenflies.operations.operation_label import OperationLabel
from schoenflies.structure import Structure

XYZ_DIR = Path(__file__).parent / "files"

E = OperationLabel.Element


# ------------------------------------------------------------------
# Matrix construction
# ------------------------------------------------------------------

def test_inversion_matrix():
    op = Operation.inversion()
    np.testing.assert_allclose(op.matrix, -np.eye(3))


def test_c2_z_matrix():
    op = Operation.rotation(E.ProperRotation, 2, np.array([0.0, 0.0, 1.0]))
    np.testing.assert_allclose(op.matrix, np.diag([-1.0, -1.0, 1.0]), atol=1e-10)


def test_c2_x_matrix():
    op = Operation.rotation(E.ProperRotation, 2, np.array([1.0, 0.0, 0.0]))
    np.testing.assert_allclose(op.matrix, np.diag([1.0, -1.0, -1.0]), atol=1e-10)


def test_c4_z_matrix():
    """C4 about z rotates x→y, y→-x, z→z."""
    op = Operation.rotation(E.ProperRotation, 4, np.array([0.0, 0.0, 1.0]))
    v = np.array([1.0, 0.0, 0.0])
    result = op.do_atom_operation(v)
    np.testing.assert_allclose(result, np.array([0.0, 1.0, 0.0]), atol=1e-10)


def test_c3_z_matrix():
    """C3 about z rotates by 120°."""
    op = Operation.rotation(E.ProperRotation, 3, np.array([0.0, 0.0, 1.0]))
    v = np.array([1.0, 0.0, 0.0])
    result = op.do_atom_operation(v)
    expected = np.array([-0.5, np.sqrt(3) / 2, 0.0])
    np.testing.assert_allclose(result, expected, atol=1e-10)


def test_sigma_h_matrix():
    """Reflection through z=0 plane (normal = z) inverts z."""
    op = Operation.reflection(np.array([0.0, 0.0, 1.0]))
    np.testing.assert_allclose(op.matrix, np.diag([1.0, 1.0, -1.0]), atol=1e-10)


def test_sigma_v_xz_matrix():
    """Reflection through xz-plane (normal = y) inverts y."""
    op = Operation.reflection(np.array([0.0, 1.0, 0.0]))
    np.testing.assert_allclose(op.matrix, np.diag([1.0, -1.0, 1.0]), atol=1e-10)


def test_improper_rotation_s2_is_inversion():
    """S2 = σh ∘ C2 = inversion."""
    op = Operation.rotation(E.ImproperRotation, 2, np.array([0.0, 0.0, 1.0]))
    np.testing.assert_allclose(op.matrix, -np.eye(3), atol=1e-10)


def test_rotation_normalises_axis():
    """Non-unit axis should be normalised internally."""
    op = Operation.rotation(E.ProperRotation, 2, np.array([0.0, 0.0, 5.0]))
    np.testing.assert_allclose(op.axis, np.array([0.0, 0.0, 1.0]), atol=1e-10)


def test_degree_inf_returns_identity():
    """degree=0 (DEGREE_INF) should give the identity matrix."""
    op = Operation.rotation(E.ProperRotation, 0, np.array([0.0, 0.0, 1.0]))
    np.testing.assert_allclose(op.matrix, np.eye(3), atol=1e-10)


# ------------------------------------------------------------------
# do_operation / error
# ------------------------------------------------------------------

def test_c3_valid_on_ammonia():
    """C3 along the principal axis of ammonia should have low error."""
    s = Structure(str(XYZ_DIR / "ammonia.xyz"))
    # principal axis of ammonia is approximately z after COM centering
    # use the N→centroid-of-H direction
    h_indices = np.where(s.atomic_numbers == 1)[0]
    centroid = s.coordinates[h_indices].mean(axis=0)
    n_idx = int(np.where(s.atomic_numbers == 7)[0][0])
    axis = centroid - s.coordinates[n_idx]
    op = Operation.rotation(E.ProperRotation, 3, axis)
    op.do_operation(s)
    assert op.get_error() < 0.1, f"C3 error too high: {op.get_error()}"


def test_inversion_invalid_on_ammonia():
    """Ammonia (C3v) has no inversion centre."""
    s = Structure(str(XYZ_DIR / "ammonia.xyz"))
    op = Operation.inversion()
    op.do_operation(s)
    assert op.get_error() >= 0.1, "Inversion should fail for ammonia"


def test_inversion_valid_on_sf6():
    """SF6 (Oh) has an inversion centre."""
    s = Structure(str(XYZ_DIR / "sulfur-hexafluoride.xyz"))
    op = Operation.inversion()
    op.do_operation(s)
    assert op.get_error() < 0.1, f"Inversion error too high for SF6: {op.get_error()}"


def test_error_raises_before_do_operation():
    op = Operation.inversion()
    with pytest.raises(RuntimeError, match="before it was computed"):
        op.get_error()


def test_result_indices_set_after_do_operation():
    s = Structure(str(XYZ_DIR / "water.xyz"))
    op = Operation.rotation(E.ProperRotation, 2, np.array([0.0, 0.0, 1.0]))
    op.do_operation(s)
    assert len(op.result_indices_forwards) == s.num_atoms


# ------------------------------------------------------------------
# Equality
# ------------------------------------------------------------------

def test_eq_inversions_always_equal():
    assert Operation.inversion() == Operation.inversion()


def test_eq_same_c2_axis():
    a = Operation.rotation(E.ProperRotation, 2, np.array([0.0, 0.0, 1.0]))
    b = Operation.rotation(E.ProperRotation, 2, np.array([0.0, 0.0, 1.0]))
    assert a == b


def test_eq_antiparallel_axis_equal():
    """Antiparallel axes define the same rotation axis."""
    a = Operation.rotation(E.ProperRotation, 3, np.array([0.0, 0.0, 1.0]))
    b = Operation.rotation(E.ProperRotation, 3, np.array([0.0, 0.0, -1.0]))
    assert a == b


def test_eq_different_degree_not_equal():
    a = Operation.rotation(E.ProperRotation, 2, np.array([0.0, 0.0, 1.0]))
    b = Operation.rotation(E.ProperRotation, 3, np.array([0.0, 0.0, 1.0]))
    assert a != b


def test_eq_different_element_not_equal():
    a = Operation.rotation(E.ProperRotation, 2, np.array([0.0, 0.0, 1.0]))
    b = Operation.rotation(E.ImproperRotation, 2, np.array([0.0, 0.0, 1.0]))
    assert a != b


def test_eq_reflections_same_normal():
    a = Operation.reflection(np.array([0.0, 0.0, 1.0]))
    b = Operation.reflection(np.array([0.0, 0.0, 1.0]))
    assert a == b


def test_eq_reflections_antiparallel_normal():
    a = Operation.reflection(np.array([0.0, 0.0, 1.0]))
    b = Operation.reflection(np.array([0.0, 0.0, -1.0]))
    assert a == b
