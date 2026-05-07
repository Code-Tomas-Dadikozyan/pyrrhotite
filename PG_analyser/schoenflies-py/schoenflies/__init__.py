"""
schoenflies — Molecular point group determination from XYZ coordinates.

Pipeline
--------
    from schoenflies import Molecule, SymmetryFinder, PointGroupClassifier

    mol = Molecule("benzene.xyz")           # load, centre, compute inertia
    sf  = SymmetryFinder(mol)
    sf.find_all()                           # detect all symmetry elements
    pgc = PointGroupClassifier(mol, sf)
    print(pgc.classify())                   # 'D6h'
"""

from .molecule import Molecule
from .symmetry_elements import SymmetryFinder
from .point_group import PointGroupClassifier

__all__ = ["Molecule", "SymmetryFinder", "PointGroupClassifier"]
