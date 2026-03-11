"""
Build the result archive stellar_seismic_catalog.zip.

Packs obtained data (stars_raw.csv, stars_clean.csv, plots/),
scripts, sources.txt, and README into a single zip for delivery.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import zipfile
from pathlib import Path


def build_result_archive(
    output_dir: str | Path,
    zip_path: str | Path | None = None,
    scripts_dir: str | Path | None = None,
    readme_path: str | Path | None = None,
    readme_content: str | None = None,
    sources_path: str | Path | None = None,
) -> Path:
    """
    Create stellar_seismic_catalog.zip with README, CSVs, plots/, scripts/, sources.txt.

    Args:
        output_dir: Directory with stars_raw.csv, stars_clean.csv, plots/,
            and optionally sources.txt and README.md.
        zip_path: Output zip path. Default: output_dir / "stellar_seismic_catalog.zip".
        scripts_dir: Directory with scripts to include (e.g. repo scripts/).
            If None, uses output_dir / "scripts" if it exists.
        readme_path: Path to README.md. If None, uses output_dir / "README.md".
        readme_content: If set, write this as README.md (overrides readme_path).
        sources_path: Path to sources.txt. If None, uses output_dir / "sources.txt".

    Returns:
        Path to the created zip file.

    Raises:
        FileNotFoundError: If stars_raw.csv or stars_clean.csv are missing.
    """
    out = Path(output_dir)
    zip_file = Path(zip_path) if zip_path else out / "stellar_seismic_catalog.zip"
    scripts_src = Path(scripts_dir) if scripts_dir else out / "scripts"
    readme_src = Path(readme_path) if readme_path else out / "README.md"
    sources_src = Path(sources_path) if sources_path else out / "sources.txt"

    raw_csv = out / "stars_raw.csv"
    clean_csv = out / "stars_clean.csv"
    plots_dir = out / "plots"

    if not raw_csv.exists():
        raise FileNotFoundError(f"Required file not found: {raw_csv}")
    if not clean_csv.exists():
        raise FileNotFoundError(f"Required file not found: {clean_csv}")

    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zf:
        # README
        if readme_content is not None:
            zf.writestr("README.md", readme_content)
        elif readme_src.exists():
            zf.write(readme_src, "README.md")

        # CSVs
        zf.write(raw_csv, "stars_raw.csv")
        zf.write(clean_csv, "stars_clean.csv")

        # plots/
        if plots_dir.exists():
            for f in plots_dir.iterdir():
                if f.is_file():
                    zf.write(f, f"plots/{f.name}")

        # scripts/
        if scripts_src.exists():
            for f in scripts_src.iterdir():
                if f.is_file() and f.suffix == ".py":
                    zf.write(f, f"scripts/{f.name}")

        # sources.txt
        if sources_src.exists():
            zf.write(sources_src, "sources.txt")

    return zip_file
