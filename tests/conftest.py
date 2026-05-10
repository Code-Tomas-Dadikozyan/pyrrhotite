"""Shared pytest fixtures and expected point group labels for integration tests."""

from pathlib import Path

import pytest

XYZ_DIR = Path(__file__).parent / "files"

# Filename → expected Schoenflies label string
# Labels match PointGroupLabel.get_name() output (to be defined in point_group_label.py).
EXPECTED_POINT_GROUPS: dict[str, str] = {
    "water.xyz":                   "C2v",
    "ammonia.xyz":                 "C3v",
    "methane.xyz":                 "Td",
    "carbon-dioxide.xyz":          "D∞h",   # D∞h
    "hydrogen-chloride.xyz":       "C∞v",   # C∞v
    "benzene.xyz":                 "D6h",
    "sulfur-hexafluoride.xyz":     "Oh",
    "cubane.xyz":                  "Oh",
    "buckminsterfullerene.xyz":    "Ih",
    "ferrocene-eclipsed.xyz":      "D5h",
    "ferrocene-staggered.xyz":     "D5d",
    "fluorochlorobromomethane.xyz":"C1",
    "thionyl-chloride.xyz":        "Cs",
    "boric-acid.xyz":              "C3h",
    "cyclobutadiene.xyz":          "D4h",
    "coronene.xyz":                "D6h",
    "prismane.xyz":                "D3h",
    "dodecahydrododecaborate.xyz": "Ih",
    "adamantane.xyz":              "Td",
    "iron-pentacarbonyl.xyz":      "D3h",
    "diborane.xyz":                "D2h",
    "tropylium.xyz":               "D7h",
    "octasulfur.xyz":              "D4d",
    "cyclooctatetraene.xyz":       "D2d",
    "trans-azobenzene.xyz":        "C2h",
    "biphenyl.xyz":                "D2h",
    "hydrazine.xyz":               "C2",
    "inositol.xyz":                "Ci",
    "triethylamine.xyz":           "C3",
    "E-hex-3-ene.xyz":             "C2h",
    "bicyclooctane.xyz":           "D2",
    "pentaborane-9.xyz":           "C4v",
}


@pytest.fixture
def xyz_dir() -> Path:
    """Path to the directory containing XYZ test molecules."""
    return XYZ_DIR
