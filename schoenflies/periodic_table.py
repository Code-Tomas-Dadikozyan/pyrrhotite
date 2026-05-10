"""
Periodic table data: atomic numbers, masses, covalent radii, and colours.
Direct translation of reference/src/periodic_table/periodic_table.cpp.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Element:
    """Represents a chemical element with display and physical properties."""

    symbol: str
    name: str
    radius: float
    mass: float
    colour: tuple[float, float, float]


# fmt: off
SYMBOL_TO_ATOMIC_NUMBER: dict[str, int] = {
    "H": 1,   "He": 2,  "Li": 3,  "Be": 4,  "B": 5,   "C": 6,   "N": 7,   "O": 8,
    "F": 9,   "Ne": 10, "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15,  "S": 16,
    "Cl": 17, "Ar": 18, "K": 19,  "Ca": 20, "Sc": 21, "Ti": 22, "V": 23,  "Cr": 24,
    "Mn": 25, "Fe": 26, "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30, "Ga": 31, "Ge": 32,
    "As": 33, "Se": 34, "Br": 35, "Kr": 36, "Rb": 37, "Sr": 38, "Y": 39,  "Zr": 40,
    "Nb": 41, "Mo": 42, "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48,
    "In": 49, "Sn": 50, "Sb": 51, "Te": 52, "I": 53,  "Xe": 54, "Cs": 55, "Ba": 56,
    "La": 57, "Ce": 58, "Pr": 59, "Nd": 60, "Pm": 61, "Sm": 62, "Eu": 63, "Gd": 64,
    "Tb": 65, "Dy": 66, "Ho": 67, "Er": 68, "Tm": 69, "Yb": 70, "Lu": 71, "Hf": 72,
    "Ta": 73, "W": 74,  "Re": 75, "Os": 76, "Ir": 77, "Pt": 78, "Au": 79, "Hg": 80,
    "Tl": 81, "Pb": 82, "Bi": 83, "Po": 84, "At": 85, "Rn": 86, "Fr": 87, "Ra": 88,
    "Ac": 89, "Th": 90, "Pa": 91, "U": 92,  "Np": 93, "Pu": 94, "Am": 95, "Cm": 96,
    "Bk": 97, "Cf": 98, "Es": 99, "Fm": 100,"Md": 101,"No": 102,"Lr": 103,"Rf": 104,
    "Db": 105,"Sg": 106,"Bh": 107,"Hs": 108,"Mt": 109,"Ds": 110,"Rg": 111,"Cn": 112,
    "Nh": 113,"Fl": 114,"Mc": 115,"Lv": 116,"Ts": 117,"Og": 118,
}

ATOMIC_NUMBER_TO_ELEMENT: dict[int, Element] = {
    1  : Element("H" , "hydrogen"     , 0.25, 1.008   , (1        , 1        , 1        )),
    2  : Element("He", "helium"       , 0.4 , 4.002602, (0.8509804, 1        , 1        )),
    3  : Element("Li", "lithium"      , 0.4 , 6.94    , (0.8      , 0.5019608, 1        )),
    4  : Element("Be", "beryllium"    , 0.4 , 9.012183, (0.7607843, 1        , 0        )),
    5  : Element("B" , "boron"        , 0.4 , 10.81   , (1        , 0.7098039, 0.7098039)),
    6  : Element("C" , "carbon"       , 0.4 , 12.011  , (0.1254902, 0.1254902, 0.1254902)),
    7  : Element("N" , "nitrogen"     , 0.4 , 14.007  , (0.0901961, 0.5843137, 1        )),
    8  : Element("O" , "oxygen"       , 0.4 , 15.999  , (0.8666667, 0        , 0        )),
    9  : Element("F" , "fluorine"     , 0.4 , 18.9984 , (0.5647059, 0.8784314, 0.3137255)),
    10 : Element("Ne", "neon"         , 0.4 , 20.1798 , (0.7019608, 0.8901961, 0.9607843)),
    11 : Element("Na", "sodium"       , 0.4 , 22.98977, (0.6705882, 0.3607843, 0.9490196)),
    12 : Element("Mg", "magnesium"    , 0.4 , 24.305  , (0.5411765, 1        , 0        )),
    13 : Element("Al", "aluminium"    , 0.4 , 26.98154, (0.7490196, 0.6509804, 0.6509804)),
    14 : Element("Si", "silicon"      , 0.4 , 28.085  , (0.9411765, 0.7843137, 0.627451 )),
    15 : Element("P" , "phosphorus"   , 0.4 , 30.97376, (1        , 0.5019608, 0        )),
    16 : Element("S" , "sulfur"       , 0.6 , 32.06   , (0.9215686, 0.827451 , 0.1803922)),
    17 : Element("Cl", "chlorine"     , 0.6 , 35.45   , (0.1215686, 0.9411765, 0.1215686)),
    18 : Element("Ar", "argon"        , 0.6 , 39.95   , (0.5019608, 0.8196078, 0.8901961)),
    19 : Element("K" , "potassium"    , 1.2 , 39.0983 , (0.5607843, 0.2509804, 0.8313725)),
    20 : Element("Ca", "calcium"      , 1.2 , 40.078  , (0.2392157, 1        , 0        )),
    21 : Element("Sc", "scandium"     , 1.2 , 44.95591, (0.9019608, 0.9019608, 0.9019608)),
    22 : Element("Ti", "titanium"     , 1.2 , 47.867  , (0.7490196, 0.7607843, 0.7803922)),
    23 : Element("V" , "vanadium"     , 1.2 , 50.9415 , (0.6509804, 0.6509804, 0.6705882)),
    24 : Element("Cr", "chromium"     , 1.2 , 51.9961 , (0.5411765, 0.6      , 0.7803922)),
    25 : Element("Mn", "manganese"    , 1.2 , 54.98304, (0.6117647, 0.4784314, 0.7803922)),
    26 : Element("Fe", "iron"         , 1.2 , 55.845  , (0.8784314, 0.4      , 0.2      )),
    27 : Element("Co", "cobalt"       , 1.2 , 58.93319, (0.9411765, 0.5647059, 0.627451 )),
    28 : Element("Ni", "nickel"       , 1.2 , 58.6934 , (0.3137255, 0.8156863, 0.3137255)),
    29 : Element("Cu", "copper"       , 1.2 , 63.546  , (0.7843137, 0.5019608, 0.2      )),
    30 : Element("Zn", "zinc"         , 1.2 , 65.38   , (0.4901961, 0.5019608, 0.6901961)),
    31 : Element("Ga", "gallium"      , 1.2 , 69.723  , (0.7607843, 0.5607843, 0.5607843)),
    32 : Element("Ge", "germanium"    , 1.2 , 72.63   , (0.4      , 0.5607843, 0.5607843)),
    33 : Element("As", "arsenic"      , 1.2 , 74.9216 , (0.7411765, 0.5019608, 0.8901961)),
    34 : Element("Se", "selenium"     , 1.2 , 78.971  , (1        , 0.6313725, 0        )),
    35 : Element("Br", "bromine"      , 1.2 , 79.904  , (0.6509804, 0.1607843, 0.1607843)),
    36 : Element("Kr", "krypton"      , 1.2 , 83.798  , (0.3607843, 0.7215686, 0.8196078)),
    37 : Element("Rb", "rubidium"     , 1.2 , 85.4678 , (0.4392157, 0.1803922, 0.6901961)),
    38 : Element("Sr", "strontium"    , 1.2 , 87.62   , (0        , 1        , 0        )),
    39 : Element("Y" , "yttrium"      , 1.2 , 88.90584, (0.5803922, 1        , 1        )),
    40 : Element("Zr", "zirconium"    , 1.2 , 91.224  , (0.5803922, 0.8784314, 0.8784314)),
    41 : Element("Nb", "niobium"      , 1.2 , 92.90637, (0.4509804, 0.7607843, 0.7882353)),
    42 : Element("Mo", "molybdenum"   , 1.2 , 95.95   , (0.3294118, 0.7098039, 0.7098039)),
    43 : Element("Tc", "technetium"   , 1.2 , 97      , (0.2313725, 0.6196078, 0.6196078)),
    44 : Element("Ru", "ruthenium"    , 1.2 , 101.07  , (0.1411765, 0.5607843, 0.5607843)),
    45 : Element("Rh", "rhodium"      , 1.2 , 102.9055, (0.0392157, 0.4901961, 0.5490196)),
    46 : Element("Pd", "palladium"    , 1.2 , 106.42  , (0.4117647, 0.5215686, 0.5215686)),
    47 : Element("Ag", "silver"       , 1.2 , 107.8682, (0.7529412, 0.7529412, 0.7529412)),
    48 : Element("Cd", "cadmium"      , 1.2 , 112.414 , (1        , 0.8509804, 0.5607843)),
    49 : Element("In", "indium"       , 1.2 , 114.818 , (0.6509804, 0.4588235, 0.4509804)),
    50 : Element("Sn", "tin"          , 1.2 , 118.71  , (0.4      , 0.5019608, 0.5019608)),
    51 : Element("Sb", "antimony"     , 1.2 , 121.76  , (0.6196078, 0.3882353, 0.7098039)),
    52 : Element("Te", "tellurium"    , 1.2 , 127.6   , (0.8313725, 0.4784314, 0        )),
    53 : Element("I" , "iodine"       , 1.2 , 126.9045, (0.5803922, 0        , 0.5803922)),
    54 : Element("Xe", "xenon"        , 1.2 , 131.293 , (0.2588235, 0.6196078, 0.6901961)),
    55 : Element("Cs", "caesium"      , 1.2 , 132.9055, (0.3411765, 0.0901961, 0.5607843)),
    56 : Element("Ba", "barium"       , 1.2 , 137.327 , (0        , 0.7882353, 0        )),
    57 : Element("La", "lanthanum"    , 1.2 , 138.9055, (0.4392157, 0.8313725, 1        )),
    58 : Element("Ce", "cerium"       , 1.2 , 140.116 , (1        , 1        , 0.7803922)),
    59 : Element("Pr", "praseodymium" , 1.2 , 140.9077, (0.8509804, 1        , 0.7803922)),
    60 : Element("Nd", "neodymium"    , 1.2 , 144.242 , (0.7803922, 1        , 0.7803922)),
    61 : Element("Pm", "promethium"   , 1.2 , 145     , (0.6392157, 1        , 0.7803922)),
    62 : Element("Sm", "samarium"     , 1.2 , 150.36  , (0.5607843, 1        , 0.7803922)),
    63 : Element("Eu", "europium"     , 1.2 , 151.964 , (0.3803922, 1        , 0.7803922)),
    64 : Element("Gd", "gadolinium"   , 1.2 , 157.25  , (0.2705882, 1        , 0.7803922)),
    65 : Element("Tb", "terbium"      , 1.2 , 158.9254, (0.1882353, 1        , 0.7803922)),
    66 : Element("Dy", "dysprosium"   , 1.2 , 162.5   , (0.1215686, 1        , 0.7803922)),
    67 : Element("Ho", "holmium"      , 1.2 , 164.9303, (0        , 1        , 0.6117647)),
    68 : Element("Er", "erbium"       , 1.2 , 167.259 , (0        , 0.9019608, 0.4588235)),
    69 : Element("Tm", "thulium"      , 1.2 , 168.9342, (0        , 0.8313725, 0.3215686)),
    70 : Element("Yb", "ytterbium"    , 1.2 , 173.045 , (0.8313725, 0.4784314, 0        )),
    71 : Element("Lu", "lutetium"     , 1.2 , 174.9668, (0        , 0.6705882, 0.1411765)),
    72 : Element("Hf", "hafnium"      , 1.2 , 178.486 , (0.3019608, 0.7607843, 1        )),
    73 : Element("Ta", "tantalum"     , 1.2 , 180.9479, (0.3019608, 0.6509804, 1        )),
    74 : Element("W" , "tungsten"     , 1.2 , 183.84  , (0.1294118, 0.5803922, 0.8392157)),
    75 : Element("Re", "rhenium"      , 1.2 , 186.207 , (0.1490196, 0.4901961, 0.6705882)),
    76 : Element("Os", "osmium"       , 1.2 , 190.23  , (0.1490196, 0.4      , 0.5882353)),
    77 : Element("Ir", "iridium"      , 1.2 , 192.217 , (0.0901961, 0.3294118, 0.5294118)),
    78 : Element("Pt", "platinum"     , 1.2 , 195.084 , (0.8156863, 0.8156863, 0.8784314)),
    79 : Element("Au", "gold"         , 1.2 , 196.9666, (1        , 0.8196078, 0.1372549)),
    80 : Element("Hg", "mercury"      , 1.2 , 200.592 , (0.7215686, 0.7215686, 0.8156863)),
    81 : Element("Tl", "thallium"     , 1.2 , 204.38  , (0.6509804, 0.3294118, 0.3019608)),
    82 : Element("Pb", "lead"         , 1.2 , 207.2   , (0.3411765, 0.3490196, 0.3803922)),
    83 : Element("Bi", "bismuth"      , 1.2 , 208.9804, (0.6196078, 0.3098039, 0.7098039)),
    84 : Element("Po", "polonium"     , 1.2 , 209     , (0.6705882, 0.3607843, 0        )),
    85 : Element("At", "astatine"     , 1.2 , 210     , (0.4588235, 0.3098039, 0.2705882)),
    86 : Element("Rn", "radon"        , 1.2 , 222     , (0.2588235, 0.5098039, 0.5882353)),
    87 : Element("Fr", "francium"     , 1.2 , 223     , (0.3411765, 0.0901961, 0.5607843)),
    88 : Element("Ra", "radium"       , 1.2 , 226     , (0        , 0.7882353, 0        )),
    89 : Element("Ac", "actinium"     , 1.2 , 227     , (0.4392157, 0.8313725, 1        )),
    90 : Element("Th", "thorium"      , 1.2 , 232.0377, (1        , 1        , 0.7803922)),
    91 : Element("Pa", "protactinium" , 1.2 , 231.0359, (0.8509804, 1        , 0.7803922)),
    92 : Element("U" , "uranium"      , 1.2 , 238.0289, (0.7803922, 1        , 0.7803922)),
    93 : Element("Np", "neptunium"    , 1.2 , 237     , (0.6392157, 1        , 0.7803922)),
    94 : Element("Pu", "plutonium"    , 1.2 , 244     , (0.5607843, 1        , 0.7803922)),
    95 : Element("Am", "americium"    , 1.2 , 243     , (0.3803922, 1        , 0.7803922)),
    96 : Element("Cm", "curium"       , 1.2 , 247     , (0.2705882, 1        , 0.7803922)),
    97 : Element("Bk", "berkelium"    , 1.2 , 247     , (0.1882353, 1        , 0.7803922)),
    98 : Element("Cf", "californium"  , 1.2 , 251     , (0.1215686, 1        , 0.7803922)),
    99 : Element("Es", "einsteinium"  , 1.2 , 252     , (0        , 1        , 0.6117647)),
    100: Element("Fm", "fermium"      , 1.2 , 257     , (0        , 0.9019608, 0.4588235)),
    101: Element("Md", "mendelevium"  , 1.2 , 258     , (0        , 0.8313725, 0.3215686)),
    102: Element("No", "nobelium"     , 1.2 , 259     , (0.8313725, 0.4784314, 0        )),
    103: Element("Lr", "lawrencium"   , 1.2 , 266     , (0        , 0.6705882, 0.1411765)),
    104: Element("Rf", "rutherfordium", 1.2 , 267     , (0.3019608, 0.7607843, 1        )),
    105: Element("Db", "dubnium"      , 1.2 , 268     , (0.3019608, 0.6509804, 1        )),
    106: Element("Sg", "seaborgium"   , 1.2 , 269     , (0.1294118, 0.5803922, 0.8392157)),
    107: Element("Bh", "bohrium"      , 1.2 , 270     , (0.1490196, 0.4901961, 0.6705882)),
    108: Element("Hs", "hassium"      , 1.2 , 269     , (0.1490196, 0.4      , 0.5882353)),
    109: Element("Mt", "meitnerium"   , 1.2 , 278     , (0.0901961, 0.3294118, 0.5294118)),
    110: Element("Ds", "darmstadtium" , 1.2 , 281     , (0.8156863, 0.8156863, 0.8784314)),
    111: Element("Rg", "roentgenium"  , 1.2 , 282     , (1        , 0.8196078, 0.1372549)),
    112: Element("Cn", "copernicium"  , 1.2 , 285     , (0.7215686, 0.7215686, 0.8156863)),
    113: Element("Nh", "nihonium"     , 1.2 , 286     , (0.6509804, 0.3294118, 0.3019608)),
    114: Element("Fl", "flerovium"    , 1.2 , 289     , (0.3411765, 0.3490196, 0.3803922)),
    115: Element("Mc", "moscovium"    , 1.2 , 290     , (0.6196078, 0.3098039, 0.7098039)),
    116: Element("Lv", "livermorium"  , 1.2 , 293     , (0.6705882, 0.3607843, 0        )),
    117: Element("Ts", "tennessine"   , 1.2 , 294     , (0.4588235, 0.3098039, 0.2705882)),
    118: Element("Og", "oganesson"    , 1.2 , 294     , (0.2588235, 0.5098039, 0.5882353)),
}
# fmt: on


def get_atomic_number(symbol: str) -> int:
    """Return the atomic number for the given element symbol."""
    if not symbol:
        raise ValueError("No element symbol supplied.")
    try:
        return SYMBOL_TO_ATOMIC_NUMBER[symbol]
    except KeyError:
        raise ValueError(f"Invalid element symbol: {symbol!r}")


def get_element(atomic_number: int) -> Element:
    """Return the Element record for the given atomic number."""
    try:
        return ATOMIC_NUMBER_TO_ELEMENT[atomic_number]
    except KeyError:
        raise ValueError(f"Invalid atomic number: {atomic_number}")
