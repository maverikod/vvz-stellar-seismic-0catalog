"""
Build stellar_seismic_catalog_enriched.zip with README, CSVs, constants, plots, scripts.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import zipfile
from pathlib import Path

from stellar_seismic_catalog.enrichment.constants import SOLAR_CONSTANTS


def build_enriched_readme(
    n_stars: int,
    n_with_class: int,
    n_with_errors: int,
    n_with_distance: int,
    n_with_mode_width: int,
    columns_added: list[str],
    columns_computed: list[str],
    columns_not_obtained: list[str],
    sources_list: list[str],
) -> str:
    """Generate README content for enriched archive."""
    cols_all = [
        "star_id",
        "radius",
        "mass",
        "luminosity",
        "nu_max",
        "delta_nu",
        "mode_width",
        "Teff",
        "distance",
        "evolutionary_stage",
        "stellar_class",
        "radius_err",
        "mass_err",
        "luminosity_err",
        "nu_max_err",
        "delta_nu_err",
        "Teff_err",
        "radius_solar",
        "mass_solar",
        "luminosity_solar",
        "nu_max_ratio_sun",
        "delta_nu_ratio_sun",
        "mean_density_proxy",
        "surface_gravity_proxy",
        "energy_proxy",
        "q_proxy",
        "luminosity_computed",
        "luminosity_source",
    ]
    constants_desc = "\n".join(f"- {k}: {v}" for k, v in SOLAR_CONSTANTS.items())
    return f"""# Stellar Seismic Catalog (Enriched)

## Data sources

{chr(10).join('- ' + s for s in sources_list)}

## Solar constants (see constants.json)

{constants_desc}

## Column list (stars_analysis_ready.csv)

{', '.join(cols_all)}

## Added fields (from enrichment)

{', '.join(columns_added) or 'None'}

## Computed fields

{', '.join(columns_computed) or 'None'}

## Not obtained (left empty or as in base catalog)

{', '.join(columns_not_obtained) or 'None'}

## Star counts

- Total stars (analysis-ready): {n_stars}
- With evolutionary_stage: {n_with_class}
- With at least one measurement error: {n_with_errors}
- With distance filled: {n_with_distance}
- With mode_width filled: {n_with_mode_width}
"""


def build_enriched_archive(
    output_dir: str | Path,
    zip_path: str | Path | None = None,
    scripts_dir: str | Path | None = None,
    readme_content: str | None = None,
) -> Path:
    """
    Create stellar_seismic_catalog_enriched.zip.
    output_dir must contain stars_analysis_ready.csv and optionally other listed files.
    """
    out = Path(output_dir)
    zip_file = (
        Path(zip_path) if zip_path else out / "stellar_seismic_catalog_enriched.zip"
    )
    scripts_src = Path(scripts_dir) if scripts_dir else out / "scripts"
    for name in ["stars_analysis_ready.csv"]:
        if not (out / name).exists():
            raise FileNotFoundError(f"Required file not found: {out / name}")
    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
        if readme_content:
            zf.writestr("README.md", readme_content)
        for fname in [
            "stars_raw.csv",
            "stars_enriched.csv",
            "stars_analysis_ready.csv",
            "atomic_reference_raw.csv",
            "constants.json",
            "sources.txt",
        ]:
            p = out / fname
            if p.exists():
                zf.write(p, fname)
        plots_dir = out / "plots"
        if plots_dir.exists():
            for f in plots_dir.iterdir():
                if f.is_file():
                    zf.write(f, f"plots/{f.name}")
        if scripts_src.exists():
            for name in [
                "download_enrichment.py",
                "merge_enrichment.py",
                "compute_observables.py",
            ]:
                f = scripts_src / name
                if f.exists():
                    zf.write(f, f"scripts/{name}")
    return zip_file
