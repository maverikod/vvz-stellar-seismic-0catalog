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
    out["stellar_class"] = ""  # APOKASC-2 has no spectral class
    # Errors: fractional where applicable; convert to absolute where needed
    for vizier_col, our_col in [
        ("e_Teff", "Teff_err"),
        ("e_Numax", "nu_max_err"),  # fractional
        ("e_Dnu", "delta_nu_err"),  # fractional
        ("e_M(cor)", "mass_err"),  # fractional
        ("e_R(cor)", "radius_err"),  # fractional
    ]:
        if vizier_col in df.columns:
            out[our_col] = df[vizier_col]
        else:
            out[our_col] = float("nan")
    out["luminosity_err"] = float("nan")  # not in APOKASC-2
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
    ra_dec_df[["star_id", "ra", "dec"]].head(10000).to_csv(upload_path, index=False)
    try:
        result = XMatch.query(
            cat1=str(upload_path),
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
        if plx_col not in df.columns or "star_id" not in df.columns:
            out = pd.DataFrame(columns=["star_id", "distance", "rotation"])
        else:
            df = df[df[plx_col].notna() & (df[plx_col] > 0.1)]
            df["distance"] = 1000.0 / df[plx_col]
            rot_col = "Vbroad" if "Vbroad" in df.columns else "vbroad"
            if rot_col in df.columns:
                df["rotation"] = df[rot_col]
            else:
                df["rotation"] = float("nan")
            out = df[["star_id", "distance", "rotation"]].drop_duplicates(
                subset=["star_id"], keep="first"
            )
    except Exception:
        out = pd.DataFrame(columns=["star_id", "distance", "rotation"])
    out.to_csv(output_dir / "enrichment_gaia.csv", index=False)
    return out


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
