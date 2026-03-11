"""
Enrichment pipeline: load base -> download -> merge -> compute -> plots -> archive.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from pathlib import Path

from stellar_seismic_catalog.enrichment.archive_enriched import (
    build_enriched_archive,
    build_enriched_readme,
)
from stellar_seismic_catalog.enrichment.compute_observables import run_compute
from stellar_seismic_catalog.enrichment.constants import write_constants_json
from stellar_seismic_catalog.enrichment.download_data import (
    fetch_atomic_reference,
    fetch_gaia_distance,
    fetch_vizier_enrichment,
)
from stellar_seismic_catalog.enrichment.merge_data import (
    load_base_catalog,
    load_base_raw,
    merge_enrichment,
)
from stellar_seismic_catalog.enrichment.plots_enriched import build_plots
from stellar_seismic_catalog.build_full_archive import build_full_archive


def run_pipeline(
    input_zip: str | Path | None = None,
    fallback_dir: str | Path | None = None,
    output_dir: str | Path = "output_enriched",
    output_base: str | Path = "output",
    scripts_dir: str | Path | None = None,
    repo_root: str | Path | None = None,
    build_full: bool = True,
) -> Path:
    """
    Run download -> merge -> compute -> plots -> README -> zip -> full archive.

    If build_full is True and no errors, builds stellar_seismic_catalog_full.zip
    (docs + data + plots + scripts) after the enriched zip.
    Returns path to stellar_seismic_catalog_full.zip when build_full else enriched zip.
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    enrich_dir = out / "enrichment_data"
    enrich_dir.mkdir(parents=True, exist_ok=True)

    # Load base
    base = load_base_catalog(input_zip, fallback_dir)
    base_raw = load_base_raw(input_zip, fallback_dir)
    if not base_raw.empty:
        base_raw.to_csv(out / "stars_raw.csv", index=False)
    else:
        base.head(0).to_csv(out / "stars_raw.csv", index=False)

    # 1. Download
    viz_df = fetch_vizier_enrichment(enrich_dir)
    fetch_gaia_distance(viz_df[["star_id", "ra", "dec"]], enrich_dir)
    fetch_atomic_reference(out)

    # 2. Merge
    merged = merge_enrichment(base, enrich_dir)
    merged.to_csv(out / "stars_enriched.csv", index=False)

    # 3. Compute
    analysis = run_compute(merged)
    analysis.to_csv(out / "stars_analysis_ready.csv", index=False)

    # 4. Plots
    build_plots(analysis, out / "plots")

    # 5. Constants and sources
    write_constants_json(out / "constants.json")
    sources = [
        "VizieR J/ApJS/239/32/table5 (APOKASC-2): evolutionary_stage, errors",
        "Gaia DR3 I/355/gaiadr3: distance (parallax), rotation (Vbroad) via CDS XMatch",
        "NIST ASD or fallback: atomic_reference_raw.csv",
    ]
    (out / "sources.txt").write_text("\n".join(sources), encoding="utf-8")

    # 6. README
    n = len(analysis)
    n_class = analysis["evolutionary_stage"].notna() & (
        analysis["evolutionary_stage"] != ""
    )
    n_errors = (
        analysis["radius_err"].notna()
        | analysis["mass_err"].notna()
        | analysis["nu_max_err"].notna()
        | analysis["delta_nu_err"].notna()
        | analysis["Teff_err"].notna()
    )
    n_dist = analysis["distance"].notna()
    n_mw = analysis["mode_width"].notna()
    columns_added = [
        "evolutionary_stage",
        "stellar_class",
        "distance",
        "rotation",
        "radius_err",
        "mass_err",
        "luminosity_err",
        "nu_max_err",
        "delta_nu_err",
        "Teff_err",
    ]
    columns_computed = [
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
    columns_not_obtained = [
        "mode_width (not in base catalogs; left empty)",
        "magnetic_activity (no source configured; left empty)",
    ]
    readme = build_enriched_readme(
        n_stars=n,
        n_with_class=int(n_class.sum()),
        n_with_errors=int(n_errors.sum()),
        n_with_distance=int(n_dist.sum()),
        n_with_mode_width=int(n_mw.sum()),
        columns_added=columns_added,
        columns_computed=columns_computed,
        columns_not_obtained=columns_not_obtained,
        sources_list=sources,
    )

    # 7. Enriched zip
    repo = Path(repo_root) if repo_root is not None else Path.cwd()
    base_out = Path(output_base)
    scripts_src = scripts_dir or repo / "scripts"
    enriched_zip = build_enriched_archive(
        output_dir=out,
        zip_path=out / "stellar_seismic_catalog_enriched.zip",
        scripts_dir=scripts_src,
        readme_content=readme,
    )
    if not build_full:
        return enriched_zip
    # 8. Full archive (docs + data + plots + scripts), overwrites previous
    full_zip = build_full_archive(
        repo_root=repo,
        output_base=base_out,
        output_enriched=out,
        scripts_dir=scripts_src,
        zip_path=repo / "stellar_seismic_catalog_full.zip",
    )
    return full_zip


def main() -> None:
    """CLI: run pipeline from env paths; builds full archive (docs+data) at end."""
    import os

    input_zip = os.environ.get("STELLAR_SEISMIC_INPUT_ZIP")
    fallback = os.environ.get("STELLAR_SEISMIC_OUTPUT", "output")
    output = os.environ.get("STELLAR_SEISMIC_ENRICHED_OUTPUT", "output_enriched")
    scripts_dir = os.environ.get("STELLAR_SEISMIC_SCRIPTS")
    repo = os.environ.get("STELLAR_SEISMIC_REPO", ".")
    zip_path = run_pipeline(
        input_zip=input_zip,
        fallback_dir=fallback,
        output_dir=output,
        output_base=fallback,
        scripts_dir=Path(scripts_dir) if scripts_dir else None,
        repo_root=Path(repo),
        build_full=True,
    )
    print(f"Full archive: {zip_path}")
