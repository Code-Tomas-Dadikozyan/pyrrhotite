"""
Idealized structure generator for axial point groups.

Builds synthetic `Structure` instances -- rings (and combinations of rings) of
a placeholder element -- whose geometry has, by construction, a requested
axial Schoenflies point group (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd). These are
useful as test fixtures for the symmetry-detection pipeline, especially for
orders n > 8 where the adaptive axis-order search and tightened operation
tolerance (see Symmetry._MAX_AXIS_ORDER) come into play.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .character_tables.generator import _coerce_label
from .periodic_table import get_atomic_number, get_element
from .point_groups.point_group_label import PointGroupLabel
from .structure import Structure

_Class = PointGroupLabel.Class


def _ring(n: int, radius: float, z: float, phase: float = 0.0) -> np.ndarray:
    """Return an (n, 3) array of coordinates for a regular n-gon ring.

    The ring lies in the plane perpendicular to the z-axis at height `z`,
    centred on the z-axis, with the first atom at angle `phase` (radians)
    measured from the x-axis.
    """
    angles = phase + 2.0 * np.pi * np.arange(n) / n
    x = radius * np.cos(angles)
    y = radius * np.sin(angles)
    z_col = np.full(n, z, dtype=float)
    return np.column_stack((x, y, z_col))


def generate_idealized_structure(
    point_group: str | PointGroupLabel,
    radius: float = 1.5,
    height: float = 1.0,
    element: str = "F",
) -> Structure:
    """Build an idealized `Structure` with the requested axial point group symmetry.

    Parameters
    ----------
    point_group:
        Either a `PointGroupLabel` or a name string accepted by
        `parse_point_group_name` (e.g. "C12v", "D9h", "S8"). Only the seven
        axial families -- Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd -- are supported.
    radius:
        Radius (in Angstroms) of the primary ring of atoms.
    height:
        z-offset (in Angstroms) used for apex atoms / second rings, where
        applicable.
    element:
        Placeholder element symbol used for the primary ring of atoms.

    Returns
    -------
    Structure
        A structure centred at its centre of mass, ready to be passed to
        `Symmetry`.

    Raises
    ------
    ValueError
        If `point_group` is not one of the seven supported axial families,
        or if the order `n` is out of range for the requested family
        (n < 3 in general, or n odd / n < 4 for Sn).
    """
    label = _coerce_label(point_group)

    group_class = label.group_class
    n = label.order

    if group_class not in (_Class.C, _Class.Ch, _Class.Cv, _Class.S, _Class.D, _Class.Dh, _Class.Dd):
        raise ValueError(
            f"generate_idealized_structure only supports the axial families "
            f"Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd; got {label.name!r}"
        )

    if group_class == _Class.S:
        if n < 4 or n % 2 != 0:
            raise ValueError(f"Sn requires an even order n >= 4; got n={n}")
    elif n < 3:
        raise ValueError(f"{label.name!r} requires order n >= 3; got n={n}")

    main_z = get_atomic_number(element)

    if group_class == _Class.Dh:
        # Dnh: a single regular n-gon ring in the xy-plane.
        coords = _ring(n, radius, z=0.0)
        atomic_numbers = np.full(n, main_z, dtype=int)
        description = f"Idealized {label.name}: regular {n}-ring"

    elif group_class == _Class.Cv:
        # Cnv: ring + apex atom of a different element on the z-axis.
        ring_coords = _ring(n, radius, z=0.0)
        apex_z = get_atomic_number("N" if element != "N" else "O")
        coords = np.vstack((np.array([[0.0, 0.0, height]]), ring_coords))
        atomic_numbers = np.concatenate(([apex_z], np.full(n, main_z, dtype=int)))
        description = f"Idealized {label.name}: {n}-ring + apex"

    elif group_class == _Class.C:
        # Cn: ring1 (z=0) + ring2 (z=height*0.3, smaller radius), with a
        # generic angular offset that breaks sigma_v / sigma_h while
        # preserving the Cn rotation.
        ring1 = _ring(n, radius, z=0.0)
        ring2 = _ring(n, radius * 0.6, z=height * 0.3, phase=(2.0 * np.pi / n) * 0.25)
        decoration_z = get_atomic_number("H" if element != "H" else "C")
        coords = np.vstack((ring1, ring2))
        atomic_numbers = np.concatenate((np.full(n, main_z, dtype=int), np.full(n, decoration_z, dtype=int)))
        description = f"Idealized {label.name}: {n}-ring + offset {n}-ring"

    elif group_class == _Class.Ch:
        # Cnh: ring1 (z=0) + ring2 (z=+height) + ring3 = mirror image of
        # ring2 (z=-height, same phase). Generic phase offset for ring2/3
        # avoids accidentally introducing C2 axes or sigma_v planes.
        ring1 = _ring(n, radius, z=0.0)
        phase = (2.0 * np.pi / n) * 0.37
        ring2 = _ring(n, radius * 0.6, z=height, phase=phase)
        ring3 = _ring(n, radius * 0.6, z=-height, phase=phase)
        decoration_z = get_atomic_number("N" if element != "N" else "O")
        coords = np.vstack((ring1, ring2, ring3))
        atomic_numbers = np.concatenate(
            (np.full(n, main_z, dtype=int), np.full(2 * n, decoration_z, dtype=int))
        )
        description = f"Idealized {label.name}: {n}-ring + mirrored {n}-ring pair"

    elif group_class in (_Class.D, _Class.Dd):
        # Dn / Dnd: a "twisted double ring" -- two parallel n-gon rings of
        # the same radius and element, offset by a twist angle theta.
        # theta = pi/(2n) (strictly between eclipsed and staggered) gives Dn
        # (chiral); theta = pi/n (staggered antiprism) gives Dnd.
        theta = (np.pi / n) if group_class == _Class.Dd else (np.pi / (2 * n))
        ring_top = _ring(n, radius, z=height)
        ring_bottom = _ring(n, radius, z=-height, phase=theta)
        coords = np.vstack((ring_top, ring_bottom))
        atomic_numbers = np.full(2 * n, main_z, dtype=int)
        description = f"Idealized {label.name}: twisted double {n}-ring (theta={theta:.4f} rad)"

    elif group_class == _Class.S:
        # Sn (n even): an (n/2)-gon antiprism (top ring at z=+height, bottom
        # ring at z=-height, staggered by the Sn rotation angle 2*pi/n)
        # plus small "marker" atoms on each ring atom, angularly offset by a
        # generic delta consistent with the Sn operation. The antiprism
        # alone has D_{(n/2)d} symmetry (a strict superset of Sn); the
        # markers break its extra C2 axes / sigma_d planes while preserving
        # Sn.
        m = n // 2
        sn_angle = 2.0 * np.pi / n
        delta = sn_angle * 0.15
        marker_radius = radius * 1.15
        marker_z_offset = height * 0.1

        top_main = _ring(m, radius, z=height)
        bottom_main = _ring(m, radius, z=-height, phase=sn_angle)
        top_marker = _ring(m, marker_radius, z=height + marker_z_offset, phase=delta)
        bottom_marker = _ring(m, marker_radius, z=-(height + marker_z_offset), phase=sn_angle + delta)

        decoration_z = get_atomic_number("H" if element != "H" else "C")
        coords = np.vstack((top_main, bottom_main, top_marker, bottom_marker))
        atomic_numbers = np.concatenate(
            (np.full(2 * m, main_z, dtype=int), np.full(2 * m, decoration_z, dtype=int))
        )
        description = f"Idealized {label.name}: {m}-gon antiprism + Sn-consistent markers"

    structure = Structure(None)
    structure.num_atoms = coords.shape[0]
    structure.coordinates = coords
    structure.atomic_numbers = atomic_numbers
    structure.description = description
    structure.filename = ""
    structure._centre_at_com()
    return structure


def format_xyz(structure: Structure) -> str:
    """Return `structure` formatted as standard XYZ text.

    The output mirrors the format read by `Structure._load_from_xyz`: an
    atom-count line, a comment line (`structure.description`), then one
    `<symbol> x y z` line per atom.
    """
    lines = [str(structure.num_atoms), structure.description]
    for i in range(structure.num_atoms):
        symbol = get_element(int(structure.atomic_numbers[i])).symbol
        x, y, z = structure.coordinates[i]
        lines.append(f"{symbol}  {x:.7f}  {y:.7f}  {z:.7f}")
    return "\n".join(lines) + "\n"


def write_xyz(structure: Structure, path: str | Path) -> None:
    """Write `structure` to `path` in standard XYZ format (see `format_xyz`)."""
    with open(path, "w") as fh:
        fh.write(format_xyz(structure))
