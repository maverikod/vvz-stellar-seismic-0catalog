"""
Process and clean stellar asteroseismic catalog data.

Reads stars_raw.csv, applies cleaning rules, writes stars_clean.csv and plots,
then builds stellar_seismic_catalog.zip.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import os
from pathlib import Path

import pandas as pd

from stellar_seismic_catalog.archive import build_result_archive
from stellar_seismic_catalog.catalogs_config import CLEAN_COLUMNS, VIZIER_CATALOGS


def _load_raw(output_dir: Path) -> pd.DataFrame:
    """Load stars_raw.csv from output directory."""
    path = output_dir / "stars_raw.csv"
    if not path.exists():
        raise FileNotFoundError(f"Run download first: {path} not found")
    return pd.read_csv(path)


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove rows without radius, without nu_max, and with relative error > 20%.
    """
    out = df.copy()
    out = out.dropna(subset=["radius", "nu_max"])
    for err_col in ["e_radius", "e_nu_max", "e_delta_nu"]:
        if err_col in out.columns:
            out = out.loc[out[err_col].fillna(0) <= 0.2]
    return out


def _select_clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only CLEAN_COLUMNS; ensure all present (NaN if missing)."""
    out = pd.DataFrame()
    for col in CLEAN_COLUMNS:
        out[col] = df[col] if col in df.columns else float("nan")
    return out


def _fill_age_myr(df: pd.DataFrame) -> pd.DataFrame:
    """Set age_Myr = 10**log_age_Myr where log_age_Myr is valid."""
    out = df.copy()
    if "log_age_Myr" not in out.columns:
        return out
    valid = out["log_age_Myr"].notna()
    if valid.any():
        out.loc[valid, "age_Myr"] = 10.0 ** out.loc[valid, "log_age_Myr"]
    return out


# Solar effective temperature (K) for L = (R/Rsun)^2 * (Teff/Teff_sun)^4
_TEFF_SUN = 5772.0


def _fill_luminosity_from_teff_radius(df: pd.DataFrame) -> pd.DataFrame:
    """Where luminosity is missing, set L/Lsun = (R/Rsun)^2 * (Teff/Teff_sun)^4."""
    out = df.copy()
    if "luminosity" not in out.columns:
        out["luminosity"] = float("nan")
    need = out["luminosity"].isna() & out["radius"].notna() & out["Teff"].notna()
    if need.any():
        r = out.loc[need, "radius"]
        t = out.loc[need, "Teff"]
        out.loc[need, "luminosity"] = (r**2) * ((t / _TEFF_SUN) ** 4)
    return out


def _build_plots(clean_df: pd.DataFrame, plots_dir: Path) -> None:
    """Save radius vs luminosity, nu_max vs radius, delta_nu vs mass (PNG)."""
    import matplotlib.pyplot as plt

    plots_dir.mkdir(parents=True, exist_ok=True)
    plt.rcParams["figure.figsize"] = (6, 4)

    # 1. radius vs luminosity (fill L from R, Teff when missing)
    plot_df = _fill_luminosity_from_teff_radius(clean_df)
    valid = plot_df["radius"].notna() & plot_df["luminosity"].notna()
    valid = valid & (plot_df["luminosity"] > 0)
    fig, ax = plt.subplots()
    ax.scatter(
        plot_df.loc[valid, "radius"],
        plot_df.loc[valid, "luminosity"],
        alpha=0.5,
        s=5,
    )
    ax.set_xlabel("Radius (Rsun)")
    ax.set_ylabel("Luminosity (Lsun)")
    ax.set_title("Radius vs Luminosity")
    ax.set_xscale("log")
    ax.set_yscale("log")
    fig.savefig(plots_dir / "radius_vs_luminosity.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 2. nu_max vs radius
    fig, ax = plt.subplots()
    ax.scatter(clean_df["radius"], clean_df["nu_max"], alpha=0.5, s=5)
    ax.set_xlabel("Radius (Rsun)")
    ax.set_ylabel("nu_max (uHz)")
    ax.set_title("nu_max vs Radius")
    ax.set_xscale("log")
    fig.savefig(plots_dir / "numax_vs_radius.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # 3. delta_nu vs mass
    fig, ax = plt.subplots()
    ax.scatter(clean_df["mass"], clean_df["delta_nu"], alpha=0.5, s=5)
    ax.set_xlabel("Mass (Msun)")
    ax.set_ylabel("delta_nu (uHz)")
    ax.set_title("delta_nu vs Mass")
    fig.savefig(plots_dir / "deltanu_vs_mass.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _write_readme(output_dir: Path, n_raw: int, n_clean: int) -> None:
    """Write README.md with sources, column descriptions, star counts."""
    sources_desc = "\n".join(
        f"- **{c['name']}**: {c['catalog_id']} — {c['url']}" for c in VIZIER_CATALOGS
    )
    column_desc = """
| Column          | Description |
|-----------------|-------------|
| star_id         | Star identifier (e.g. KIC) |
| radius          | Stellar radius (Rsun) |
| mass            | Stellar mass (Msun) |
| luminosity      | Luminosity (if available) |
| nu_max          | Frequency of maximum power (uHz) |
| delta_nu        | Large frequency spacing (uHz) |
| mode_width      | Mode width (if available) |
| Teff            | Effective temperature (K) |
| distance        | Distance (if available) |
| metallicity     | [Fe/H] (dex), from catalog |
| log_age_Myr      | log10(age in Myr), from catalog |
| age_Myr         | Age (Myr), 10^log_age_Myr |
| rotation        | Rotation (e.g. vsini); empty if not in catalog |
| magnetic_activity | Magnetic activity index; empty if not in catalog |
"""
    content = f"""# Stellar Seismic Catalog

## Data sources

{sources_desc}

## Column descriptions (stars_clean.csv)

{column_desc}

## Star counts

- **Raw (stars_raw.csv):** {n_raw} stars
- **Clean (stars_clean.csv):** {n_clean} stars (radius/nu_max present; rel.err. <= 20%)
"""
    (output_dir / "README.md").write_text(content.strip(), encoding="utf-8")


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


def run_process(
    output_dir: str | Path, scripts_dir: str | Path | None = None
) -> tuple[pd.DataFrame, Path]:
    """
    Load raw, clean, write stars_clean.csv, plots, README, and zip.

    Returns:
        (clean DataFrame, path to created zip).
    """
    out = Path(output_dir)
    raw = _load_raw(out)
    cleaned = _clean(raw)
    clean_df = _select_clean_columns(cleaned)
    clean_df = _fill_age_myr(clean_df)
    clean_df = _fill_luminosity_from_teff_radius(clean_df)
    clean_df.to_csv(out / "stars_clean.csv", index=False)
    _build_plots(clean_df, out / "plots")
    _write_readme(out, len(raw), len(clean_df))
    zip_path = _run_pack_step(out, scripts_dir)
    return clean_df, zip_path


def main() -> None:
    """
    Entry point for stellar-seismic-process: clean, plot, pack.
    """
    output_dir = os.environ.get("STELLAR_SEISMIC_OUTPUT", "output")
    scripts_dir = os.environ.get("STELLAR_SEISMIC_SCRIPTS") or str(
        Path.cwd() / "scripts"
    )
    clean_df, zip_path = run_process(output_dir, Path(scripts_dir))
    print(f"Clean: {len(clean_df)} stars -> {output_dir}/stars_clean.csv")
    print(f"Archive: {zip_path}")
