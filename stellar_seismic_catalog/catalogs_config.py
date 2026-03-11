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

# Clean table columns (tech spec + optional: metallicity, age, rotation, magnetic)
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
    "metallicity",  # [Fe/H]
    "log_age_Myr",  # log10(age in Myr)
    "age_Myr",  # age in Myr (from 10^log_age_Myr)
    "rotation",  # e.g. vsini or rotation period (if available)
    "magnetic_activity",  # e.g. S-index (if available)
]

# VizieR catalog config: catalog_id, column_map, optional table2_id for merge
# 1) APOKASC-2: Kepler evolved stars (6676 rows)
# 2) HD-TESS: TESS red giants, table1+table2 merged (1709 rows)
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
            "metallicity": "FeH",  # [Fe/H]
            "nu_max": "Numax",
            "delta_nu": "Dnu",
            "mass": "M(cor)",
            "radius": "R(cor)",
            "luminosity": None,
            "distance": None,
            "mode_width": None,
            "mode_amplitude": None,
            "log_age_Myr": "LogAge",  # log10(age in Myr), APOKASC-2
            "rotation": None,  # not in APOKASC-2
            "magnetic_activity": None,  # not in APOKASC-2
        },
        "error_columns": {
            "nu_max": "e_Numax",
            "delta_nu": "e_Dnu",
            "radius": "e_R(cor)",
        },
    },
    {
        "catalog_id": "J/AJ/164/135/table1",
        "table2_id": "J/AJ/164/135/table2",
        "merge_key": "TIC",
        "name": "HD-TESS",
        "url": "https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/AJ/164/135",
        "column_map": {
            "star_id": "TIC",
            "ra": "_RA",
            "dec": "_DE",
            "Teff": "Teff",
            "metallicity": "[M/H]",
            "nu_max": "numax",
            "delta_nu": "Deltanu",
            "mass": "Mass",
            "radius": "Rad",
            "luminosity": None,
            "distance": None,
            "mode_width": None,
            "mode_amplitude": None,
            "log_age_Myr": None,
            "rotation": None,
            "magnetic_activity": None,
        },
        "error_columns": {
            "nu_max": "e_numax",
            "delta_nu": "e_Deltanu",
            "radius": "e_Rad",
            "mass": "e_Mass",
            "Teff": "e_Teff",
        },
    },
]
