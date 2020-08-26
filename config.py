import os
import json

# Global Variables
API_HOST = "https://adsorption.nist.gov"
HEADERS = {"Accept": "application/citeproc+json"}  # JSON Headers
TEXTENCODE = "utf-8"
CANONICALIZE = "NFKC"

SCRIPT_PATH = os.path.split(os.path.realpath(__file__))[0]
ROOT_DIR = os.getcwd()
DOI_MAPPING_PATH = os.path.join(ROOT_DIR, "DOI_mapping.csv")
JSON_FOLDER = os.path.join(ROOT_DIR, "Library")

# Character Substitution Rules for Converting the DOI to a stub
doi_stub_rules = [
    {"old": "/", "new": "-"},
    {"old": "(", "new": ""},
    {"old": ")", "new": ""},
    {"old": ":", "new": ""},
    {"old": ":", "new": ""},
    {"old": " ", "new": ""},
    {"old": "+", "new": "plus"},
    {"old": "-", "new": ""},
]

# Pressure Conversions (to bar units)
pressure_units = {
    "bar": 1.0,
    "Pa": 1.0e-05,
    "kPa": 1.0e-02,
    "MPa": 10.0,
    "atm": 1.01325e0,
    "mmHg": 1.333223684e-03,
    "Torr": 1.333223684e-03,
    "psi": 6.8947572932e-02,
    "mbar": 1.0e-03,
}

# Canonical Keys for Isotherm JSON (required keys for ISODB)
canonical_keys = [
    "DOI",
    "adsorbates",
    "adsorbent",
    "adsorptionUnits",
    "articleSource",
    "category",
    "compositionType",
    "concentrationUnits",
    "date",
    "digitizer",
    "filename",
    "isotherm_data",
    "isotherm_type",
    "pressureUnits",
    "tabular_data",
    "temperature",
]

# Wrapper function for JSON writes to ensure consistency in formatting
def json_writer(filename, data):
    """Format JSON according to ISODB specs"""
    with open(filename, mode="w") as output:
        json.dump(
            data, output, ensure_ascii=False, sort_keys=True, indent=4
        )  # formatting rules
        output.write("\n")  # new line at EOF
