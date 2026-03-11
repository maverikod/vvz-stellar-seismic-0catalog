#!/usr/bin/env python3
"""
Compute observables, clean, build plots, README and zip.
Reads stars_enriched.csv; writes stars_analysis_ready.csv, plots/, archive.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import os
from pathlib import Path

from stellar_seismic_catalog.enrichment.archive_enriched import (
    build_enriched_archive,
    build_enriched_readme,
)
from stellar_seismic_catalog.enrichment.compute_observables import run_compute
from stellar_seismic_catalog.enrichment.constants import write_constants_json
from stellar_seismic_catalog.enrichment.plots_enriched import build_plots


def main() -> None:
    output = Path(os.environ.get("STELLAR_SEISMIC_ENRICHED_OUTPUT", "output_enriched"))
    enriched_path = output / "stars_enriched.csv"
    if not enriched_path.exists():
        raise FileNotFoundError(f"Run merge_enrichment first: {enriched_path}")
    import pandas as pd

    merged = pd.read_csv(enriched_path)
    analysis = run_compute(merged)
    analysis.to_csv(output / "stars_analysis_ready.csv", index=False)
    build_plots(analysis, output / "plots")
    write_constants_json(output / "constants.json")
    sources = [
        "VizieR J/ApJS/239/32/table5 (APOKASC-2): evolutionary_stage, errors",
        "Gaia DR3 I/355/gaiadr3: distance from parallax (CDS XMatch)",
        "NIST ASD or fallback: atomic_reference_raw.csv",
    ]
    (output / "sources.txt").write_text("\n".join(sources), encoding="utf-8")
    n = len(analysis)
    n_class = (
        analysis["evolutionary_stage"].notna() & (analysis["evolutionary_stage"] != "")
    ).sum()
    n_errors = (
        analysis["radius_err"].notna()
        | analysis["mass_err"].notna()
        | analysis["nu_max_err"].notna()
        | analysis["delta_nu_err"].notna()
        | analysis["Teff_err"].notna()
    ).sum()
    n_dist = analysis["distance"].notna().sum()
    n_mw = analysis["mode_width"].notna().sum()
    readme = build_enriched_readme(
        n_stars=n,
        n_with_class=int(n_class),
        n_with_errors=int(n_errors),
        n_with_distance=int(n_dist),
        n_with_mode_width=int(n_mw),
        columns_added=[
            "evolutionary_stage",
            "stellar_class",
            "radius_err",
            "mass_err",
            "luminosity_err",
            "nu_max_err",
            "delta_nu_err",
            "Teff_err",
        ],
        columns_computed=[
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
        ],
        columns_not_obtained=["mode_width (not in APOKASC-2)"],
        sources_list=sources,
    )
    (output / "README.md").write_text(readme, encoding="utf-8")
    scripts_dir = Path(
        os.environ.get("STELLAR_SEISMIC_SCRIPTS", str(Path.cwd() / "scripts"))
    )
    zip_path = build_enriched_archive(
        output_dir=output,
        scripts_dir=scripts_dir,
        readme_content=readme,
    )
    out_csv = output / "stars_analysis_ready.csv"
    print(f"Analysis-ready: {len(analysis)} stars -> {out_csv}")
    print(f"Archive: {zip_path}")


if __name__ == "__main__":
    main()
