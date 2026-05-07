"""
utils.py — Shared constants and geometric utility functions.

Every other module imports from here. Nothing in this file depends on
molecule data; it is pure linear algebra and tolerance bookkeeping.
"""

import numpy as np

# ---------------------------------------------------------------------------
# Tolerance constants
# ---------------------------------------------------------------------------

# GEOMETRY_TOLERANCE is the single threshold used throughout the algorithm
# when deciding whether two atomic positions are "the same" after a symmetry
# operation.  The C++ source uses 0.02 uniformly.
#
# Why 0.02 Å?  Real QM-optimised geometries have numerical noise at the
# 1e-5 Å level, so 0.02 is conservative enough to absorb that while still
# being tight enough to distinguish atoms that differ by a real bond (~1 Å).
# Increasing it makes the algorithm more permissive (may find false symmetry);
# decreasing it makes it stricter (may miss real symmetry in distorted
# structures).
#
# Python/C++ note: this constant plays the same role as the unnamed literal
# 0.02 scattered throughout the C++ source.  Naming it here means every
# module can do `from schoenflies.utils import GEOMETRY_TOLERANCE` and we
# only need to change the value in one place.
GEOMETRY_TOLERANCE = 0.02  # Angstroms

# Eigenvalue tolerance for deciding whether two principal moments of inertia
# are "equal" (used to classify the rotor type in molecule.py).
INERTIA_TOLERANCE = 0.02   # amu·Å²


# ---------------------------------------------------------------------------
# Rotation matrix  (Rodrigues' rotation formula)
# ---------------------------------------------------------------------------

def rotation_matrix(axis: np.ndarray, angle: float) -> np.ndarray:
    """
    Build the 3x3 matrix that rotates space by `angle` radians around `axis`.

    Chemistry meaning
    -----------------
    A proper rotation Cn by 2π/n degrees around an axis is the most
    fundamental symmetry operation.  To test whether a molecule has a C3
    axis along, say, [0,0,1], we rotate all atom coordinates by 120° around
    that vector and check whether every atom lands on top of an equivalent
    atom.  This function produces the matrix that does that rotation.

    Mathematics (Rodrigues' formula)
    ---------------------------------
    For a unit vector k̂ = (kx, ky, kz) and angle θ:

        R = cosθ · I  +  sinθ · [k̂]x  +  (1-cosθ) · k̂⊗k̂

    where [k̂]x is the skew-symmetric cross-product matrix and k̂⊗k̂ is the
    outer product.  numpy does both in a few lines.

    Parameters
    ----------
    axis  : array-like, shape (3,) — rotation axis (need not be unit length)
    angle : float — rotation angle in radians

    Returns
    -------
    R : np.ndarray, shape (3, 3) — orthogonal rotation matrix (det = +1)
    """
    axis = np.asarray(axis, dtype=float)
    axis = axis / np.linalg.norm(axis)          # normalise to unit vector

    kx, ky, kz = axis
    c = np.cos(angle)
    s = np.sin(angle)
    t = 1.0 - c

    # Rodrigues' formula written out element by element
    return np.array([
        [t*kx*kx + c,    t*kx*ky - s*kz, t*kx*kz + s*ky],
        [t*kx*ky + s*kz, t*ky*ky + c,    t*ky*kz - s*kx],
        [t*kx*kz - s*ky, t*ky*kz + s*kx, t*kz*kz + c   ],
    ])


# ---------------------------------------------------------------------------
# Reflection matrix  (reflect through a plane with given normal)
# ---------------------------------------------------------------------------

def reflection_matrix(normal: np.ndarray) -> np.ndarray:
    """
    Build the 3x3 matrix that reflects space through the plane whose normal
    is `normal`.

    Chemistry meaning
    -----------------
    A mirror plane σ maps every atom to its mirror image.  The plane is
    defined by its normal vector n̂.  For example, the xz-plane has normal
    [0,1,0], so reflecting through it negates every atom's y-coordinate.

    Mathematics
    -----------
    Householder reflection:  R = I − 2 n̂ n̂ᵀ

    Parameters
    ----------
    normal : array-like, shape (3,) — plane normal (need not be unit length)

    Returns
    -------
    R : np.ndarray, shape (3, 3) — orthogonal matrix with det = −1
    """
    n = np.asarray(normal, dtype=float)
    n = n / np.linalg.norm(n)
    return np.eye(3) - 2.0 * np.outer(n, n)


# ---------------------------------------------------------------------------
# Apply a 3×3 matrix to a full set of coordinates
# ---------------------------------------------------------------------------

def apply_matrix(coords: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    """
    Apply a 3×3 transformation matrix to every atom in `coords`.

    Parameters
    ----------
    coords : np.ndarray, shape (N, 3) — Cartesian coordinates of N atoms
    matrix : np.ndarray, shape (3, 3) — rotation or reflection matrix

    Returns
    -------
    np.ndarray, shape (N, 3) — transformed coordinates

    Python note: `coords @ matrix.T` is equivalent to applying `matrix` to
    each row vector independently.  In the C++ source this is a loop over
    atoms doing matrix–vector products; numpy vectorises it automatically.
    """
    return coords @ matrix.T


# ---------------------------------------------------------------------------
# Equivalence check
# ---------------------------------------------------------------------------

def are_equivalent(
    coords1: np.ndarray,
    coords2: np.ndarray,
    elements: list[str],
    tol: float = GEOMETRY_TOLERANCE,
) -> bool:
    """
    Return True if the two sets of atomic coordinates represent the same
    molecular geometry (up to `tol` Angstroms), accounting for atom identity.

    Chemistry meaning
    -----------------
    After applying a symmetry operation (e.g. a C3 rotation), every
    transformed atom must land on top of an atom of the SAME element.
    This function checks that condition: for each atom in `coords2`, it looks
    for a matching atom in `coords1` that is within `tol` Å AND has the same
    element symbol.

    Algorithm
    ---------
    For each atom i in coords2, search coords1 for an atom j with:
      - elements[i] == elements[j]   (same chemical element)
      - ||coords1[j] − coords2[i]|| < tol   (close enough in space)
    If every atom finds a match, the operation is a symmetry operation.

    Parameters
    ----------
    coords1  : np.ndarray, shape (N, 3) — reference coordinates (original)
    coords2  : np.ndarray, shape (N, 3) — transformed coordinates
    elements : list of str, length N    — element symbol for each atom
    tol      : float — distance threshold in Angstroms

    Returns
    -------
    bool
    """
    for i, (pos, elem) in enumerate(zip(coords2, elements)):
        # Compute distance from this transformed atom to all original atoms
        diffs = coords1 - pos          # shape (N, 3)
        dists = np.linalg.norm(diffs, axis=1)   # shape (N,)

        # Find original atoms of the same element within tolerance
        matches = np.where(dists < tol)[0]
        if not any(elements[j] == elem for j in matches):
            return False
    return True


# ---------------------------------------------------------------------------
# Plane normal via SVD
# ---------------------------------------------------------------------------

def plane_normal(coords: np.ndarray) -> np.ndarray:
    """
    Find the unit normal to the best-fit plane through a set of points.

    Chemistry meaning
    -----------------
    Used to find the normal of a candidate mirror plane.  For example, to
    test whether benzene has a σh plane, we fit a plane through all the
    carbon atoms and take its normal as the candidate plane normal.

    Mathematics
    -----------
    Centre the points, stack them into a matrix, and take the SVD.  The
    right singular vector corresponding to the SMALLEST singular value points
    perpendicular to the plane of best fit (scipy.linalg replaces the C++
    Eigen JacobiSVD used in the original).

    Parameters
    ----------
    coords : np.ndarray, shape (N, 3) — atom coordinates

    Returns
    -------
    normal : np.ndarray, shape (3,) — unit normal vector
    """
    from scipy.linalg import svd

    centred = coords - coords.mean(axis=0)
    _, _, Vt = svd(centred, full_matrices=False)
    # Last row of Vt is the direction of minimum variance = plane normal
    return Vt[-1]


# ---------------------------------------------------------------------------
# Axis deduplication
# ---------------------------------------------------------------------------

def axes_are_parallel(axis1: np.ndarray, axis2: np.ndarray, tol: float = GEOMETRY_TOLERANCE) -> bool:
    """
    Return True if two axes point in the same or opposite direction.

    Used to avoid adding the same rotation axis twice when building the
    candidate axis list (once found as [0,0,1] and again as [0,0,-1]).

    Parameters
    ----------
    axis1, axis2 : array-like, shape (3,)
    tol          : float — tolerance on |cross product| norm

    Returns
    -------
    bool
    """
    a1 = np.asarray(axis1, dtype=float)
    a2 = np.asarray(axis2, dtype=float)
    a1 = a1 / np.linalg.norm(a1)
    a2 = a2 / np.linalg.norm(a2)
    cross = np.cross(a1, a2)
    return float(np.linalg.norm(cross)) < tol
