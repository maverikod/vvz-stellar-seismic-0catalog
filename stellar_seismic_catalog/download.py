"""
Download stellar asteroseismic catalogs from VizieR (Kepler/TESS) and write raw data.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import os
from pathlib import Path
from typing import cast

import pandas as pd

from stellar_seismic_catalog.catalogs_config import VIZIER_CATALOGS


def _fetch_vizier_catalog(catalog_id: str) -> pd.DataFrame:
    """Query VizieR and return first table as DataFrame."""
    from astroquery.vizier import Vizier

    Vizier.ROW_LIMIT = -1
    result = Vizier.get_catalogs(catalog_id)
    if not result:
        return pd.DataFrame()
    # First table
    table = list(result.values())[0]
    return table.to_pandas()


def _normalize_catalog(
    df: pd.DataFrame,
    column_map: dict[str, str | None],
    error_columns: dict[str, str],
    catalog_name: str,
) -> pd.DataFrame:
    """Map VizieR columns to our schema; add optional error columns and catalog name."""
    out = pd.DataFrame()
    for our_name, vizier_col in column_map.items():
        if vizier_col and vizier_col in df.columns:
            out[our_name] = df[vizier_col]
        else:
            out[our_name] = float("nan")
    for our_err, vizier_err in error_columns.items():
        if vizier_err in df.columns:
            out[f"e_{our_err}"] = df[vizier_err]
    out["catalog"] = catalog_name
    return out


def _fetch_all() -> pd.DataFrame:
    """Fetch all configured catalogs and concatenate."""
    frames: list[pd.DataFrame] = []
    for cfg in VIZIER_CATALOGS:
        cat_id = cast(str, cfg["catalog_id"])
        name = cast(str, cfg["name"])
        col_map = cast(dict[str, str | None], cfg["column_map"])
        err_cols = cast(dict[str, str], cfg.get("error_columns") or {})
        try:
            df = _fetch_vizier_catalog(cat_id)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {cat_id}: {e}") from e
        if df.empty:
            continue
        df_norm = _normalize_catalog(df, col_map, err_cols, name)
        frames.append(df_norm)
    if not frames:
        return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    return combined


def _write_sources(output_dir: Path) -> None:
    """Write sources.txt listing data sources."""
    lines = [
        "Data sources for stellar_seismic_catalog",
        "",
    ]
    for cfg in VIZIER_CATALOGS:
        lines.append(f"  {cfg['name']}: {cfg['catalog_id']}")
        lines.append(f"    URL: {cfg['url']}")
        lines.append("")
    (output_dir / "sources.txt").write_text("\n".join(lines), encoding="utf-8")


def run_download(output_dir: str | Path) -> pd.DataFrame:
    """
    Download catalogs, normalize, save stars_raw.csv and sources.txt.

    Returns:
        Raw DataFrame (also written to output_dir/stars_raw.csv).
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    raw = _fetch_all()
    if raw.empty:
        raise RuntimeError("No data fetched from any catalog")
    raw.to_csv(out / "stars_raw.csv", index=False)
    _write_sources(out)
    return raw


def main() -> None:
    """Entry point for stellar-seismic-download CLI and scripts/download_catalogs.py."""
    output_dir = os.environ.get("STELLAR_SEISMIC_OUTPUT", "output")
    df = run_download(output_dir)
    print(f"Downloaded {len(df)} rows to {output_dir}/stars_raw.csv")
