"""
Compute solar-normalized columns, derived observables, luminosity_source; clean data.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import pandas as pd

from stellar_seismic_catalog.enrichment.constants import (
    DELTA_NU_SUN,
    L_SUN,
    M_SUN,
    NU_MAX_SUN,
    R_SUN,
    T_SUN,
)


def ensure_luminosity_and_source(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing L via L/Lsun = (R/Rsun)^2 * (Teff/Tsun)^4.
    Add luminosity_computed and luminosity_source ('catalog' or 'computed').
    """
    out = df.copy()
    if "luminosity" not in out.columns:
        out["luminosity"] = float("nan")
    out["luminosity_computed"] = out["luminosity"].copy()
    out["luminosity_source"] = "catalog"
    need = out["luminosity"].isna() & out["radius"].notna() & out["Teff"].notna()
    if need.any():
        r = out.loc[need, "radius"]
        t = out.loc[need, "Teff"]
        out.loc[need, "luminosity_computed"] = (r**2) * ((t / T_SUN) ** 4)
        out.loc[need, "luminosity_source"] = "computed"
    return out


def add_solar_normalized(df: pd.DataFrame) -> pd.DataFrame:
    """Add solar-normalized and ratio-to-sun columns."""
    out = df.copy()
    out["radius_solar"] = (
        out["radius"] / R_SUN if "radius" in out.columns else float("nan")
    )
    out["mass_solar"] = out["mass"] / M_SUN if "mass" in out.columns else float("nan")
    out["luminosity_solar"] = (
        out["luminosity_computed"] / L_SUN
        if "luminosity_computed" in out.columns
        else (
            out["luminosity"] / L_SUN if "luminosity" in out.columns else float("nan")
        )
    )
    out["nu_max_ratio_sun"] = (
        out["nu_max"] / NU_MAX_SUN if "nu_max" in out.columns else float("nan")
    )
    out["delta_nu_ratio_sun"] = (
        out["delta_nu"] / DELTA_NU_SUN if "delta_nu" in out.columns else float("nan")
    )
    return out


def add_derived_observables(df: pd.DataFrame) -> pd.DataFrame:
    """Add mean_density_proxy, surface_gravity_proxy, energy_proxy, q_proxy."""
    out = df.copy()
    r, m = out.get("radius", pd.Series(dtype=float)), out.get(
        "mass", pd.Series(dtype=float)
    )
    nu, dnu = out.get("nu_max", pd.Series(dtype=float)), out.get(
        "delta_nu", pd.Series(dtype=float)
    )
    out["mean_density_proxy"] = (
        m / (r**3) if r is not None and m is not None else float("nan")
    )
    out["surface_gravity_proxy"] = (
        m / (r**2) if r is not None and m is not None else float("nan")
    )
    out["energy_proxy"] = (
        (m**2) / r if r is not None and m is not None else float("nan")
    )
    out["q_proxy"] = nu / dnu if nu is not None and dnu is not None else float("nan")
    return out


def ensure_error_columns_absolute(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure *_err columns exist and are numeric."""
    out = df.copy()
    err_cols = [
        "radius_err", "mass_err", "luminosity_err",
        "nu_max_err", "delta_nu_err", "Teff_err",
    ]
    for col in err_cols:
        if col not in out.columns:
            out[col] = float("nan")
        else:
            out[col] = pd.to_numeric(out[col], errors="coerce")
    return out


def clean_for_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates; keep rows with required columns non-null."""
    out = df.drop_duplicates(subset=["star_id"], keep="first")
    for c in ["radius", "mass", "nu_max", "delta_nu", "Teff"]:
        if c in out.columns:
            out = out[out[c].notna()]
    return out


def run_compute(merged_df: pd.DataFrame) -> pd.DataFrame:
    """Apply luminosity fill, solar norm, derived observables, errors, cleaning."""
    df = ensure_luminosity_and_source(merged_df)
    df = add_solar_normalized(df)
    df = add_derived_observables(df)
    df = ensure_error_columns_absolute(df)
    return clean_for_analysis(df)
