"""
Build a single archive with all data and documentation.

Includes: README, tech.spec, docs/, data (raw, clean, enriched, analysis-ready,
atomic ref, constants, sources), plots/, scripts/.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import zipfile
from pathlib import Path


def build_full_archive(
    repo_root: str | Path,
    output_base: str | Path = "output",
    output_enriched: str | Path | None = "output_enriched",
    scripts_dir: str | Path | None = None,
    zip_path: str | Path | None = None,
) -> Path:
    """
    Create one zip with all project docs and data.

    Packs: README.md, tech.spec.md, docs/, data/*.csv and data/*.json,
    plots/, scripts/. Data taken from output_base and output_enriched.
    """
    repo = Path(repo_root)
    base = Path(output_base)
    enriched = Path(output_enriched) if output_enriched else None
    scripts_src = Path(scripts_dir) if scripts_dir else repo / "scripts"
    out_zip = Path(zip_path) if zip_path else repo / "stellar_seismic_catalog_full.zip"

    added: set[str] = set()

    def add_file(zf: zipfile.ZipFile, path: Path, arcname: str) -> None:
        if path.exists() and arcname not in added:
            zf.write(path, arcname)
            added.add(arcname)

    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        # Documentation
        for name in ["README.md", "tech.spec.md"]:
            add_file(zf, repo / name, name)
        docs_dir = repo / "docs"
        if docs_dir.exists():
            for f in docs_dir.iterdir():
                if f.is_file():
                    add_file(zf, f, f"docs/{f.name}")

        # Data: enriched first (priority), then base for missing
        if enriched and enriched.exists():
            for name in [
                "stars_raw.csv",
                "stars_clean.csv",
                "stars_enriched.csv",
                "stars_analysis_ready.csv",
                "atomic_reference_raw.csv",
                "constants.json",
                "sources.txt",
            ]:
                add_file(zf, enriched / name, f"data/{name}")
            plots_enr = enriched / "plots"
            if plots_enr.exists():
                for f in plots_enr.iterdir():
                    if f.is_file():
                        add_file(zf, f, f"plots/{f.name}")
        for name in ["stars_raw.csv", "stars_clean.csv", "sources.txt"]:
            add_file(zf, base / name, f"data/{name}")
        plots_base = base / "plots"
        if plots_base.exists():
            for f in plots_base.iterdir():
                if f.is_file():
                    add_file(zf, f, f"plots/{f.name}")

        # Scripts
        if scripts_src.exists():
            for f in scripts_src.iterdir():
                if f.is_file() and f.suffix == ".py":
                    add_file(zf, f, f"scripts/{f.name}")

    return out_zip


def main() -> None:
    """CLI: build full archive from env or default paths."""
    import os

    repo = Path(os.environ.get("STELLAR_SEISMIC_REPO", "."))
    base = os.environ.get("STELLAR_SEISMIC_OUTPUT", "output")
    enriched = os.environ.get("STELLAR_SEISMIC_ENRICHED_OUTPUT", "output_enriched")
    zip_path = build_full_archive(
        repo_root=repo,
        output_base=base,
        output_enriched=enriched,
        zip_path=repo / "stellar_seismic_catalog_full.zip",
    )
    print(f"Full archive: {zip_path}")
