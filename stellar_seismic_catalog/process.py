"""
Process and clean stellar asteroseismic catalog data.

After writing stars_raw.csv, stars_clean.csv, plots/, and README/sources.txt
to the output directory, builds stellar_seismic_catalog.zip so that
obtained data are packed into the result archive.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from pathlib import Path

from stellar_seismic_catalog.archive import build_result_archive


def main() -> None:
    """
    Entry point for stellar-seismic-process CLI and scripts/process_catalogs.py.

    When implemented: download/merge/clean data, write CSVs and plots,
    then pack result into stellar_seismic_catalog.zip.
    """
    raise NotImplementedError("Process logic to be implemented")


def _run_pack_step(
    output_dir: str | Path, scripts_dir: str | Path | None = None
) -> Path:
    """
    Build stellar_seismic_catalog.zip from output_dir.
    Call after writing CSVs and plots. Used by main() when implemented.
    """
    scripts = scripts_dir or Path.cwd() / "scripts"
    return build_result_archive(
        output_dir=output_dir,
        scripts_dir=scripts if Path(scripts).exists() else None,
    )


if __name__ == "__main__":
    main()
