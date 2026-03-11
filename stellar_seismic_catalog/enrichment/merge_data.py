"""
Merge base catalog (stars_clean) with enrichment data (VizieR ES/errors, Gaia distance).

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from pathlib import Path

import pandas as pd


def load_base_catalog(
    zip_path: str | Path | None, fallback_dir: str | Path | None
) -> pd.DataFrame:
    """Load stars_clean from zip or from fallback_dir/stars_clean.csv."""
    if zip_path and Path(zip_path).exists():
        import zipfile

        with zipfile.ZipFile(zip_path) as z:
            with z.open("stars_clean.csv") as f:
                return pd.read_csv(f)
    if fallback_dir:
        path = Path(fallback_dir) / "stars_clean.csv"
        if path.exists():
            return pd.read_csv(path)
    raise FileNotFoundError(
        "Need stellar_seismic_catalog.zip or output/stars_clean.csv"
    )


def load_base_raw(
    zip_path: str | Path | None, fallback_dir: str | Path | None
) -> pd.DataFrame:
    """Load stars_raw from zip or fallback_dir."""
    if zip_path and Path(zip_path).exists():
        import zipfile

        with zipfile.ZipFile(zip_path) as z:
            if "stars_raw.csv" in z.namelist():
                with z.open("stars_raw.csv") as f:
                    return pd.read_csv(f)
    if fallback_dir:
        path = Path(fallback_dir) / "stars_raw.csv"
        if path.exists():
            return pd.read_csv(path)
    return pd.DataFrame()


def merge_enrichment(
    base: pd.DataFrame,
    enrichment_dir: Path,
) -> pd.DataFrame:
    """
    Merge base (stars_clean) with enrichment_vizier.csv and enrichment_gaia.csv.
    Adds: evolutionary_stage, stellar_class, *_err, distance (from Gaia if new).
    """
    base = base.copy()
    base["star_id"] = base["star_id"].astype(int)
    # Vizier: ES, errors
    viz_path = enrichment_dir / "enrichment_vizier.csv"
    if viz_path.exists():
        viz = pd.read_csv(viz_path)
        viz["star_id"] = viz["star_id"].astype(int)
        extra = [
            c
            for c in viz.columns
            if c != "star_id"
            and c
            in [
                "ra",
                "dec",
                "evolutionary_stage",
                "stellar_class",
                "Teff_err",
                "nu_max_err",
                "delta_nu_err",
                "mass_err",
                "radius_err",
                "luminosity_err",
            ]
        ]
        if extra:
            base = base.merge(viz[["star_id"] + extra], on="star_id", how="left")
    # Gaia: distance and rotation (overwrite where we have new value)
    gaia_path = enrichment_dir / "enrichment_gaia.csv"
    if gaia_path.exists():
        gaia = pd.read_csv(gaia_path)
        if "star_id" in gaia.columns and "distance" in gaia.columns and len(gaia) > 0:
            gaia["star_id"] = gaia["star_id"].astype(int)
            gaia = gaia.drop_duplicates(subset=["star_id"], keep="first")
            rename = {"distance": "distance_gaia"}
            if "rotation" in gaia.columns:
                rename["rotation"] = "rotation_gaia"
            cols = (
                ["star_id", "distance", "rotation"]
                if "rotation" in gaia.columns
                else ["star_id", "distance"]
            )
            merge_df = gaia[cols].rename(columns=rename)
            base = base.merge(merge_df, on="star_id", how="left")
            if "distance_gaia" in base.columns:
                base["distance"] = base["distance_gaia"].fillna(base["distance"])
                base.drop(columns=["distance_gaia"], inplace=True)
            if "rotation_gaia" in base.columns:
                base["rotation"] = base["rotation_gaia"].fillna(base["rotation"])
                base.drop(columns=["rotation_gaia"], inplace=True)
    # Mode width: Vrard+ 2018, merge on star_id (KIC)
    mw_path = enrichment_dir / "enrichment_mode_width.csv"
    if mw_path.exists():
        mw = pd.read_csv(mw_path)
        if "star_id" in mw.columns and "mode_width" in mw.columns and len(mw) > 0:
            mw["star_id"] = mw["star_id"].astype(int)
            mw = mw.drop_duplicates(subset=["star_id"], keep="first")
            base = base.merge(
                mw[["star_id", "mode_width"]],
                on="star_id",
                how="left",
                suffixes=("", "_mw"),
            )
            if "mode_width_mw" in base.columns:
                base["mode_width"] = base["mode_width_mw"].fillna(base["mode_width"])
                base.drop(columns=["mode_width_mw"], inplace=True)
    # Magnetic activity: Boro Saikia+ 2018, merge by position (ra, dec)
    act_path = enrichment_dir / "enrichment_activity.csv"
    if act_path.exists() and "ra" in base.columns and "dec" in base.columns:
        act = pd.read_csv(act_path)
        if "magnetic_activity" in act.columns and len(act) > 0:
            for key in ["ra", "dec"]:
                if key in act.columns:
                    act[key] = pd.to_numeric(act[key], errors="coerce")
            act["ra"] = act["ra"].round(5)
            act["dec"] = act["dec"].round(5)
            act = act.drop_duplicates(subset=["ra", "dec"], keep="first")
            b = base.copy()
            b["ra"] = pd.to_numeric(b["ra"], errors="coerce").round(5)
            b["dec"] = pd.to_numeric(b["dec"], errors="coerce").round(5)
            b = b.merge(
                act[["ra", "dec", "magnetic_activity"]].rename(
                    columns={"magnetic_activity": "magnetic_activity_act"}
                ),
                on=["ra", "dec"],
                how="left",
            )
            if "magnetic_activity_act" in b.columns:
                base["magnetic_activity"] = b["magnetic_activity_act"].fillna(
                    base["magnetic_activity"]
                )
    return base
