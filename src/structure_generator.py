"""
Idealized structure generator for axial point groups.

Builds synthetic `Structure` instances whose geometry has, by construction, a
requested axial Schoenflies point group (Cn, Cnh, Cnv, Sn, Dn, Dnh, Dnd).
These are useful as test fixtures for the symmetry-detection pipeline,
especially for orders n > 8 where the adaptive axis-order search and
tightened operation tolerance (see Symmetry._MAX_AXIS_ORDER) come into play.

Beyond the bare geometry, each generated structure is built so that
`Structure.calculate_bond_pairs` (dist^2 < 20 * r_i * r_j, in covalent radii
from `periodic_table.py`) produces a *plausible* bonding pattern -- modelled
after real molecules of the same family (e.g. ammonia's apex+ring for Cnv,
benzene's ring+terminal-substituent for Cnh, ferrocene's metal-hub sandwich
for Dn/Dnh/Dnd/Sn) -- rather than an over-connected uniform ring where every
atom bonds to four neighbours.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .character_tables.generator import _coerce_label
from .periodic_table import get_atomic_number, get_element
from .point_groups.point_group_label import PointGroupLabel
from .structure import Structure

_Class = PointGroupLabel.Class

# F-F bonding cutoff distance (Angstroms): sqrt(20 * r_F * r_F) = sqrt(20 * 0.4 * 0.4).
# Used as the reference scale for ring spacing -- see `_radius_for`.
_FF_BOND_CUTOFF = np.sqrt(20.0 * 0.4 * 0.4)


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


def _radius_for(n: int) -> float:
    """Return a ring radius (Angstroms) for which adjacent atoms bond but next-nearest
    atoms do not.

    For a regular n-gon, the nearest-neighbour distance is `2*r*sin(pi/n)` and the
    next-nearest-neighbour distance is `2*r*sin(2*pi/n)`. This picks `r` roughly
    midway between the largest radius for which the nearest-neighbour distance
    stays under `_FF_BOND_CUTOFF` and the smallest radius for which the
    next-nearest-neighbour distance exceeds it -- i.e. each ring atom ends up
    bonded to exactly its two ring neighbours (degree 2 from the ring itself).
    """
    if n == 3:
        # n=3: "nearest" and "next-nearest" are the same pair (every atom is
        # adjacent to both others), so the two bounds coincide; r=1.0 keeps the
        # single distance (2*sin(pi/3) ~= 1.73 A) just under the cutoff.
        return 1.0
    lo = _FF_BOND_CUTOFF / (2.0 * np.sin(2.0 * np.pi / n))
    hi = _FF_BOND_CUTOFF / (2.0 * np.sin(np.pi / n))
    return (lo + hi) / 2.0


def _decoration_element(element: str) -> str:
    """Pick a small, light placeholder element for terminal substituent atoms
    (e.g. the "H" in a benzene-like ring+H pattern), distinct from `element`.
    """
    return "H" if element != "H" else "C"


def _apex_element(element: str) -> str:
    """Pick an apex/cap element (similar covalent radius to common ring elements),
    distinct from `element` -- mirrors ammonia's N apex over an H ring.
    """
    return "N" if element != "N" else "O"


def _apex_element_heavy(element: str) -> str:
    """Pick a slightly larger-radius apex element (for high-order Cnv rings,
    where a larger apex-ring bonding cutoff is needed), distinct from `element`.
    """
    return "S" if element != "S" else "Cl"


def _hub_element(element: str) -> str:
    """Pick a large-radius (metal-like) placeholder element for a central hub
    atom, distinct from `element` -- mirrors ferrocene's central Fe.
    """
    return "Fe" if element != "Fe" else "Co"


def generate_idealized_structure(
    point_group: str | PointGroupLabel,
    radius: float = 1.0,
    height: float = 0.6,
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
        Scale factor (default 1.0) applied to the ring radii used for the
        primary ring(s) of atoms. The default geometry is tuned so that, at
        `radius=1.0`, ring atoms bond to exactly their ring neighbours (per
        `Structure.calculate_bond_pairs`'s `dist^2 < 20 * r_i * r_j`
        criterion); scaling `radius` away from 1.0 may change which atoms end
        up bonded.
    height:
        Scale factor (default 0.6, matching the historical default) applied
        to the z-offsets used for apex atoms / second rings / hub-to-ring
        separation, where applicable.
    element:
        Placeholder element symbol used for the primary ring(s) of atoms.
        Apex, hub, and decoration atoms automatically use a different element
        (see `_apex_element`, `_hub_element`, `_decoration_element`).

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
    height_scale = height / 0.6

    if group_class == _Class.Cv:
        # Cnv: ring + apex atom of a different element on the z-axis, mirroring
        # ammonia's N-apex-over-H-ring pattern. Each ring atom bonds to its 2
        # ring neighbours + the apex (degree 3); the apex bonds to all n ring
        # atoms.
        ring_radius = _radius_for(n) * radius
        if n >= 8:
            # For larger rings, cap the radius and use a larger-covalent-radius
            # apex element so the apex-ring distance stays within bonding range.
            ring_radius = min(ring_radius, 2.1 * radius)
            apex_element_name = _apex_element_heavy(element)
            apex_height = 0.5 * height_scale
        else:
            apex_element_name = _apex_element(element)
            apex_height = 0.6 * height_scale
        ring_coords = _ring(n, ring_radius, z=0.0)
        apex_z = get_atomic_number(apex_element_name)
        coords = np.vstack((np.array([[0.0, 0.0, apex_height]]), ring_coords))
        atomic_numbers = np.concatenate(([apex_z], np.full(n, main_z, dtype=int)))
        description = f"Idealized {label.name}: {n}-ring + apex"

    elif group_class == _Class.C:
        # Cn: ring1 (main, z=0) + ring2 (terminal substituent ring, slightly
        # larger radius, small z-offset and angular offset). Each ring1 atom
        # bonds to its 2 ring1 neighbours + 1 ring2 (terminal) atom (degree 3);
        # ring2 atoms are terminal (degree 1). The small offsets break sigma_h,
        # sigma_v, and S2n while preserving Cn.
        ring1_radius = _radius_for(n) * radius
        eps = (2.0 * np.pi / n) * 0.05
        ring1 = _ring(n, ring1_radius, z=0.0)
        ring2 = _ring(n, ring1_radius * 1.1, z=0.45 * height_scale, phase=eps)
        decoration_z = get_atomic_number(_decoration_element(element))
        coords = np.vstack((ring1, ring2))
        atomic_numbers = np.concatenate((np.full(n, main_z, dtype=int), np.full(n, decoration_z, dtype=int)))
        description = f"Idealized {label.name}: {n}-ring + terminal {n}-ring"

    elif group_class == _Class.Ch:
        # Cnh: ring1 (main) + ring2 (terminal substituent ring), both planar at
        # z=0 with a small angular offset. A planar arrangement is automatically
        # invariant under sigma_h (the molecular plane itself); the generic
        # offset avoids accidentally introducing sigma_v / extra C2 axes, which
        # would promote this to Dnh/Cnv. Each ring1 atom bonds to its 2 ring1
        # neighbours + 1 ring2 (terminal) atom (degree 3); ring2 atoms are
        # terminal (degree 1).
        upper = 1.75 / (2.0 * np.sin(np.pi / n))
        r1 = min(max(1.1, 0.5 / np.sin(np.pi / n)), upper) * radius
        eps = (2.0 * np.pi / n) * 0.05
        r2_factor = 1.8 if n <= 8 else 1.8 - 0.05 * (n - 8)
        ring1 = _ring(n, r1, z=0.0)
        ring2 = _ring(n, r1 * r2_factor, z=0.0, phase=eps)
        decoration_z = get_atomic_number(_decoration_element(element))
        coords = np.vstack((ring1, ring2))
        atomic_numbers = np.concatenate((np.full(n, main_z, dtype=int), np.full(n, decoration_z, dtype=int)))
        description = f"Idealized {label.name}: planar {n}-ring + terminal {n}-ring"

    elif group_class in (_Class.D, _Class.Dh, _Class.Dd):
        # Dn / Dnh / Dnd: a central hub atom (different, larger-radius element,
        # mirroring ferrocene's Fe) plus two parallel n-gon rings, related by a
        # twist angle theta: theta=0 (eclipsed prism, Dnh, like ferrocene-eclipsed),
        # theta=pi/(2n) (generic twist, Dn, chiral), or theta=pi/n (staggered
        # antiprism, Dnd, like ferrocene-staggered). The ring separation is
        # large enough that the two rings are not directly bonded to each
        # other -- they are connected only through the hub. Each ring atom
        # bonds to its 2 ring neighbours + the hub (degree 3); the hub bonds to
        # all 2n ring atoms.
        if group_class == _Class.Dh:
            theta = 0.0
        elif group_class == _Class.Dd:
            theta = np.pi / n
        else:
            theta = np.pi / (2 * n)

        ring_radius = _radius_for(n) * radius
        base_height = 0.8 if (group_class == _Class.Dd and n in (3, 4)) else 1.0
        ring_height = base_height * height_scale

        ring_top = _ring(n, ring_radius, z=ring_height)
        ring_bottom = _ring(n, ring_radius, z=-ring_height, phase=theta)
        hub_z = get_atomic_number(_hub_element(element))
        coords = np.vstack((np.array([[0.0, 0.0, 0.0]]), ring_top, ring_bottom))
        atomic_numbers = np.concatenate(([hub_z], np.full(2 * n, main_z, dtype=int)))
        description = f"Idealized {label.name}: hub + twisted double {n}-ring (theta={theta:.4f} rad)"

    elif group_class == _Class.S:
        # Sn (n even): a central hub atom + an (n/2)-gon antiprism (two rings
        # of m=n/2 atoms, staggered by the Sn rotation angle 2*pi/n, separated
        # widely enough to avoid direct cross-ring bonds) + small "marker"
        # atoms on each ring atom, angularly offset by a generic delta
        # consistent with the Sn operation (top markers offset by delta,
        # bottom markers offset by theta+delta, matching how Sn maps top atoms
        # to bottom atoms). The antiprism + hub alone has D_{(n/2)d} symmetry
        # (a strict superset of Sn); the markers break its extra C2 axes /
        # sigma_d planes while preserving Sn. Each main ring atom bonds to its
        # 2 ring neighbours + the hub + its own marker (degree 4, like a
        # substituted ferrocene ring carbon); markers are terminal (or, for
        # n=4, also reach the hub).
        m = n // 2
        theta = np.pi / m
        delta = (2.0 * np.pi / n) * 0.25
        mr_factor = 1.05

        if n == 4:
            ring_radius = 0.7 * radius
            mz_off = 1.2 * height_scale
        else:
            ring_radius = _radius_for(m) * radius
            mz_off = {6: 1.25, 8: 1.2, 10: 1.1}.get(n, 1.2) * height_scale
        ring_height = 1.0 * height_scale

        ring_top = _ring(m, ring_radius, z=ring_height)
        ring_bottom = _ring(m, ring_radius, z=-ring_height, phase=theta)
        marker_top = _ring(m, ring_radius * mr_factor, z=ring_height + mz_off, phase=delta)
        marker_bottom = _ring(m, ring_radius * mr_factor, z=-(ring_height + mz_off), phase=theta + delta)

        marker_z = get_atomic_number(_decoration_element(element))
        hub_z = get_atomic_number(_hub_element(element))
        coords = np.vstack((np.array([[0.0, 0.0, 0.0]]), ring_top, ring_bottom, marker_top, marker_bottom))
        atomic_numbers = np.concatenate(
            ([hub_z], np.full(2 * m, main_z, dtype=int), np.full(2 * m, marker_z, dtype=int))
        )
        description = f"Idealized {label.name}: hub + {m}-gon antiprism + Sn-consistent markers"

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
