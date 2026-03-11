"""
CLI entry point to build stellar_seismic_catalog.zip from output directory.

Run after data are obtained and processed. Archive contains README.md,
stars_raw.csv, stars_clean.csv, plots/, scripts/, sources.txt.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import os
from pathlib import Path

from stellar_seismic_catalog.archive import build_result_archive


def main() -> None:
    """
    Build stellar_seismic_catalog.zip from output directory.

    Uses env STELLAR_SEISMIC_OUTPUT for output dir (default: output).
    Scripts are taken from STELLAR_SEISMIC_SCRIPTS or cwd/scripts.
    """
    output_dir = os.environ.get("STELLAR_SEISMIC_OUTPUT", "output")
    scripts_dir = os.environ.get("STELLAR_SEISMIC_SCRIPTS") or str(
        Path.cwd() / "scripts"
    )
    zip_path = build_result_archive(
        output_dir=output_dir,
        scripts_dir=scripts_dir if Path(scripts_dir).exists() else None,
    )
    print(f"Archive created: {zip_path}")
