"""
Tests for result archive building.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from stellar_seismic_catalog.archive import build_result_archive


def test_build_result_archive_creates_zip_with_required_files() -> None:
    """build_result_archive creates zip with stars_raw.csv and stars_clean.csv."""
    with TemporaryDirectory() as tmp:
        out = Path(tmp)
        (out / "stars_raw.csv").write_text("a,b\n1,2")
        (out / "stars_clean.csv").write_text("x,y\n3,4")
        zip_path = build_result_archive(output_dir=out)
        assert zip_path == out / "stellar_seismic_catalog.zip"
        assert zip_path.exists()
        with zipfile.ZipFile(zip_path) as zf:
            names = set(zf.namelist())
        assert "stars_raw.csv" in names
        assert "stars_clean.csv" in names


def test_build_result_archive_raises_without_raw_csv() -> None:
    """build_result_archive raises FileNotFoundError if stars_raw.csv is missing."""
    with TemporaryDirectory() as tmp:
        out = Path(tmp)
        (out / "stars_clean.csv").write_text("x,y\n3,4")
        with pytest.raises(FileNotFoundError, match="stars_raw.csv"):
            build_result_archive(output_dir=out)


def test_build_result_archive_raises_without_clean_csv() -> None:
    """build_result_archive raises FileNotFoundError if stars_clean.csv is missing."""
    with TemporaryDirectory() as tmp:
        out = Path(tmp)
        (out / "stars_raw.csv").write_text("a,b\n1,2")
        with pytest.raises(FileNotFoundError, match="stars_clean.csv"):
            build_result_archive(output_dir=out)
