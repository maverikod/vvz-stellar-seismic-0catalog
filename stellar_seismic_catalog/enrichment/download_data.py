"""
Download enrichment data: VizieR (ES, errors), Gaia (distance), NIST atomic reference.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

from pathlib import Path

import pandas as pd


def _fetch_vizier_apokasc2() -> pd.DataFrame:
    """Fetch APOKASC-2 table5: KIC, ES, Teff, Numax, Dnu, M(cor), R(cor), errors."""
    from astroquery.vizier import Vizier

    Vizier.ROW_LIMIT = -1
    cat = Vizier.get_catalogs("J/ApJS/239/32/table5")[0]
    df = cat.to_pandas()
    return df


def _map_evolutionary_stage(es: str) -> str:
    """Map APOKASC-2 ES code to evolutionary_stage."""
    if pd.isna(es) or not isinstance(es, str):
        return ""
    es = es.strip().upper()
    if es in ("RG", "RGB", "RC"):
        return "red_giant"
    if es in ("MS",):
        return "main_sequence"
    if es in ("SG", "SGB"):
        return "subgiant"
    if es in ("CLUMP", "RED_CLUMP"):
        return "red_giant"
    return es.lower().replace(" ", "_") if es else ""


def fetch_vizier_enrichment(output_dir: Path) -> pd.DataFrame:
    """
    Fetch VizieR APOKASC-2 for ES and errors; save enrichment_vizier.csv.
    Returns DataFrame with star_id (KIC), ra, dec, evolutionary_stage, error columns.
    """
    df = _fetch_vizier_apokasc2()
    out = pd.DataFrame()
    out["star_id"] = df["KIC"].astype(int)
    out["ra"] = df["_RA"] if "_RA" in df.columns else float("nan")
    out["dec"] = df["_DE"] if "_DE" in df.columns else float("nan")
    out["evolutionary_stage"] = (
        df["ES"].map(_map_evolutionary_stage) if "ES" in df.columns else ""
    )
    # Stellar class: use ES code (e.g. RGB, RC) when evolutionary_stage is set
    out["stellar_class"] = (
        df["ES"].fillna("").astype(str).str.strip() if "ES" in df.columns else ""
    )
    # Errors: s_M(cor), s_R(cor) (fractional); Teff/numax/Dnu errs not in table5
    for vizier_col, our_col in [
        ("s_M(cor)", "mass_err"),
        ("s_R(cor)", "radius_err"),
    ]:
        if vizier_col in df.columns:
            out[our_col] = df[vizier_col]
        else:
            out[our_col] = float("nan")
    for our_col in ["Teff_err", "nu_max_err", "delta_nu_err", "luminosity_err"]:
        if our_col not in out.columns:
            out[our_col] = float("nan")
    output_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(output_dir / "enrichment_vizier.csv", index=False)
    return out


def fetch_gaia_distance(ra_dec_df: pd.DataFrame, output_dir: Path) -> pd.DataFrame:
    """
    Cross-match ra,dec with Gaia DR3 via CDS XMatch. Saves enrichment_gaia.csv.
    Includes distance (from parallax) and rotation (from Vbroad/vsini when present).
    ra_dec_df must have columns ra, dec, star_id.
    """
    try:
        from astroquery.xmatch import XMatch
        import astropy.units as u
    except ImportError:
        output_dir.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(columns=["star_id", "distance", "rotation"]).to_csv(
            output_dir / "enrichment_gaia.csv", index=False
        )
        return pd.DataFrame()
    output_dir.mkdir(parents=True, exist_ok=True)
    upload_path = output_dir / "upload_ra_dec.csv"
    upload_df = ra_dec_df[["star_id", "ra", "dec"]].head(10000)
    upload_df.to_csv(upload_path, index=False)
    try:
        from astropy.table import Table

        cat1_table = Table.from_pandas(upload_df)
        result = XMatch.query(
            cat1=cat1_table,
            cat2="I/355/gaiadr3",
            max_distance=2 * u.arcsec,
            colRA1="ra",
            colDec1="dec",
        )
    except Exception:
        pd.DataFrame(columns=["star_id", "distance", "rotation"]).to_csv(
            output_dir / "enrichment_gaia.csv", index=False
        )
        return pd.DataFrame()
    try:
        df = result.to_pandas()
        plx_col = "parallax" if "parallax" in df.columns else "Plx"
        if plx_col not in df.columns:
            out = pd.DataFrame(columns=["star_id", "distance", "rotation"])
        else:
            df = df[df[plx_col].notna() & (df[plx_col] > 0.1)].copy()
            if df.empty:
                out = pd.DataFrame(columns=["star_id", "distance", "rotation"])
            else:
                df["distance"] = 1000.0 / df[plx_col]
                rot_col = "vbroad" if "vbroad" in df.columns else "Vbroad"
                df["rotation"] = df[rot_col] if rot_col in df.columns else float("nan")
                if "star_id" not in df.columns:
                    ra_col = (
                        "ra"
                        if "ra" in df.columns
                        else next(
                            (
                                c
                                for c in df.columns
                                if "ra" in c.lower() and "rad" not in c.lower()
                            ),
                            None,
                        )
                    )
                    dec_col = (
                        "dec"
                        if "dec" in df.columns
                        else next((c for c in df.columns if "dec" in c.lower()), None)
                    )
                    if ra_col and dec_col and not ra_dec_df.empty:
                        match = (
                            ra_dec_df[["star_id", "ra", "dec"]]
                            .drop_duplicates(subset=["ra", "dec"], keep="first")
                            .copy()
                        )
                        match["ra"] = match["ra"].round(6)
                        match["dec"] = match["dec"].round(6)
                        df = df.copy()
                        df["ra"] = df[ra_col].astype(float).round(6)
                        df["dec"] = df[dec_col].astype(float).round(6)
                        df = df.merge(match, on=["ra", "dec"], how="left")
                    else:
                        df["star_id"] = float("nan")
                out = df[["star_id", "distance", "rotation"]].drop_duplicates(
                    subset=["star_id"], keep="first"
                )
                out = out[out["star_id"].notna()]
    except Exception:
        out = pd.DataFrame(columns=["star_id", "distance", "rotation"])
    out.to_csv(output_dir / "enrichment_gaia.csv", index=False)
    return out


def fetch_vizier_mode_width(output_dir: Path) -> pd.DataFrame:
    """
    Fetch mode width (Gamma0) from Vrard+ 2018, J/A+A/616/A94/dataprob.
    Saves enrichment_mode_width.csv with star_id (KIC), mode_width (Gamma0).
    """
    from astroquery.vizier import Vizier

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "enrichment_mode_width.csv"
    try:
        Vizier.ROW_LIMIT = -1
        cat = Vizier.get_catalogs("J/A+A/616/A94/dataprob")[0]
        df = cat.to_pandas()
        out = pd.DataFrame()
        out["star_id"] = df["KIC"].astype(int)
        out["mode_width"] = df["Gamma0"] if "Gamma0" in df.columns else float("nan")
        out.to_csv(out_path, index=False)
        return out
    except Exception:
        pd.DataFrame(columns=["star_id", "mode_width"]).to_csv(out_path, index=False)
        return pd.DataFrame()


def fetch_vizier_magnetic_activity(output_dir: Path) -> pd.DataFrame:
    """
    Fetch chromospheric activity from Boro Saikia+ 2018, J/A+A/616/A108/catalog.
    Saves enrichment_activity.csv with ra, dec, magnetic_activity (Smean).
    Merge in pipeline by position (ra, dec).
    """
    from astroquery.vizier import Vizier

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "enrichment_activity.csv"
    try:
        Vizier.ROW_LIMIT = -1
        cat = Vizier.get_catalogs("J/A+A/616/A108/catalog")[0]
        df = cat.to_pandas()
        out = pd.DataFrame()
        out["ra"] = df["_RA"] if "_RA" in df.columns else float("nan")
        out["dec"] = df["_DE"] if "_DE" in df.columns else float("nan")
        out["magnetic_activity"] = (
            df["Smean"]
            if "Smean" in df.columns
            else (df["logRpHK"] if "logRpHK" in df.columns else float("nan"))
        )
        out.to_csv(out_path, index=False)
        return out
    except Exception:
        pd.DataFrame(columns=["ra", "dec", "magnetic_activity"]).to_csv(
            out_path, index=False
        )
        return pd.DataFrame()


def fetch_atomic_reference(output_dir: Path) -> Path:
    """Download minimal atomic reference; save atomic_reference_raw.csv."""
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "atomic_reference_raw.csv"
    try:
        import urllib.request

        # NIST ASD line list - minimal query for H I
        url = (
            "https://physics.nist.gov/cgi-bin/ASD/line1.pl?spectra=H+I&"
            "limits_type=0&low_w=300&upp_w=700&show_av=2&unit=1&de=0&format=2"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "stellar_seismic/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
        # Parse HTML table or pre; if no table, write headers only
        lines = [line for line in raw.splitlines() if line.strip()]
        if len(lines) < 5:
            _write_minimal_atomic_reference(out_path)
            return out_path
        # Try to extract table rows (NIST returns HTML)
        import re

        data_rows = []
        for line in lines:
            if re.search(r"^\d+\.\d+", line) or re.search(r"\d+\.\d+e[+-]?\d+", line):
                parts = line.split()
                if len(parts) >= 4:
                    data_rows.append(parts)
        if data_rows:
            cols = [
                "species",
                "wavelength_nm",
                "frequency_Hz",
                "energy_upper_eV",
                "energy_lower_eV",
                "Aki",
            ]
            ncol = min(len(cols), len(data_rows[0]))
            df = pd.DataFrame([r[:ncol] for r in data_rows[:200]], columns=cols[:ncol])
            df.insert(0, "species", "H")
            df.to_csv(out_path, index=False)
        else:
            _write_minimal_atomic_reference(out_path)
    except Exception:
        _write_minimal_atomic_reference(out_path)
    return out_path


def _write_minimal_atomic_reference(path: Path) -> None:
    """Write minimal atomic reference with headers and placeholder row."""
    cols = "species,wavelength,frequency,energy_upper,energy_lower,Aki"
    path.write_text(
        cols + "\nH,656.28,4.57e14,12.09,10.20,6.47e7\n",
        encoding="utf-8",
    )
