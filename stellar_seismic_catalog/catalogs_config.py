"""
VizieR catalog IDs and column name mappings for stellar asteroseismic data.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

# Target columns in our schema (tech spec)
TARGET_RAW_COLUMNS = [
    "star_id",
    "catalog",
    "ra",
    "dec",
    "mass",
    "radius",
    "luminosity",
    "Teff",
    "metallicity",
    "distance",
    "nu_max",
    "delta_nu",
    "mode_width",
    "mode_amplitude",
]

# Clean table columns (tech spec)
CLEAN_COLUMNS = [
    "star_id",
    "radius",
    "mass",
    "luminosity",
    "nu_max",
    "delta_nu",
    "mode_width",
    "Teff",
    "distance",
]

# VizieR catalog config: (catalog_id, table_index, {our_name: vizier_column})
# APOKASC-2: table5 = main stellar properties (6676 rows)
VIZIER_CATALOGS = [
    {
        "catalog_id": "J/ApJS/239/32/table5",
        "name": "APOKASC-2",
        "url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/239/32",
        "column_map": {
            "star_id": "KIC",
            "ra": "_RA",
            "dec": "_DE",
            "Teff": "Teff",
            "metallicity": "FeH",
            "nu_max": "Numax",
            "delta_nu": "Dnu",
            "mass": "M(cor)",
            "radius": "R(cor)",
            "luminosity": None,
            "distance": None,
            "mode_width": None,
            "mode_amplitude": None,
        },
        "error_columns": {
            "nu_max": "e_Numax",
            "delta_nu": "e_Dnu",
            "radius": "e_R(cor)",
        },
    },
]
