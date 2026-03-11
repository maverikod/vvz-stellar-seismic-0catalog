# Stellar Seismic Catalog

Download, process, and enrich stellar asteroseismic catalogs for analysis. Builds raw/clean tables, optional enriched catalog with solar-normalized and derived observables, and result archives.

**Author:** Vasiliy Zdanovskiy  
**email:** vasilyvz@gmail.com

---

## Data sources

### Base catalog (download + process)

| Source | Description | URL | What we use |
|--------|-------------|-----|-------------|
| **VizieR — APOKASC-2** | APOKASC-2 catalog of Kepler evolved stars (Pinsonneault et al. 2018). Stellar properties from APOGEE spectroscopy and Kepler asteroseismology (KASC). | [VizieR J/ApJS/239/32](https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=J/ApJS/239/32) | Table `table5`: KIC (star_id), coordinates (_RA, _DE), Teff, metallicity (FeH), nu_max (Numax), delta_nu (Dnu), mass (M(cor)), radius (R(cor)), fractional errors e_Numax, e_Dnu, e_R(cor), e_M(cor). ~6676 evolved stars. |

- **VizieR** (CDS): [https://vizier.cds.unistra.fr](https://vizier.cds.unistra.fr) — main catalog access via `astroquery.vizier`.  
- **Kepler** asteroseismic data are taken from the VizieR table above (APOKASC-2); no direct MAST API used in the base pipeline.  
- **Gaia DR3** is used only in the **enrichment** step (see below) for distance/parallax.

### Enrichment pipeline (optional)

| Source | Description | URL | What we use |
|--------|-------------|-----|-------------|
| **VizieR — APOKASC-2** | Same catalog as base. | Same as above | Evolutionary state (ES → evolutionary_stage: main_sequence, subgiant, red_giant), error columns (e_Teff, e_Numax, e_Dnu, e_M(cor), e_R(cor)) for radius_err, mass_err, nu_max_err, delta_nu_err, Teff_err. |
| **Gaia DR3** | ESA Gaia Data Release 3. | [CDS I/355/gaiadr3](https://vizier.cds.unistra.fr/viz-bin/VizieR?-source=I/355/gaiadr3) | Cross-match by position (CDS XMatch) to get parallax → distance (pc). |
| **NIST ASD** | NIST Atomic Spectra Database (lines). | [NIST ASD](https://physics.nist.gov/PhysRefData/ASD/lines_form.html) | Minimal atomic reference table (species, wavelength, frequency, energies, Aki) for downstream use; fallback stub if fetch fails. |

---

## Project layout and rules

- **Spec:** [tech.spec.md](tech.spec.md)  
- **Layout (code, docs, data, logs):** [docs/LAYOUT_STANDARDS.md](docs/LAYOUT_STANDARDS.md)  
- **Project rules:** [docs/PROJECT_RULES.md](docs/PROJECT_RULES.md)

---

## Install

```bash
pip install stellar-seismic-catalog
```

Or from the repo (with `.venv` activated):

```bash
pip install -e .
```

---

## Usage

### 1. Base pipeline (catalog + zip)

```bash
stellar-seismic-download   # writes output/stars_raw.csv, output/sources.txt
stellar-seismic-process   # writes output/stars_clean.csv, output/plots/, builds output/stellar_seismic_catalog.zip
```

Or without install:

```bash
python scripts/download_catalogs.py
python scripts/process_catalogs.py
```

- **Output dir:** set `STELLAR_SEISMIC_OUTPUT` (default: `output`).  
- **Result:** `output/stellar_seismic_catalog.zip` with README, stars_raw.csv, stars_clean.csv, plots/, scripts/, sources.txt.

### 2. Enrichment pipeline (extended catalog + zip)

Takes the base zip (or `output/` with stars_clean.csv) and produces an enriched archive:

```bash
export STELLAR_SEISMIC_INPUT_ZIP=output/stellar_seismic_catalog.zip
export STELLAR_SEISMIC_ENRICHED_OUTPUT=output_enriched
stellar-seismic-enrich
```

Or step by step:

```bash
export STELLAR_SEISMIC_OUTPUT=output
export STELLAR_SEISMIC_ENRICHED_OUTPUT=output_enriched
python scripts/download_enrichment.py
python scripts/merge_enrichment.py
python scripts/compute_observables.py
```

- **Result:** `output_enriched/stellar_seismic_catalog_enriched.zip` with README, stars_raw.csv, stars_enriched.csv, stars_analysis_ready.csv, atomic_reference_raw.csv, constants.json, sources.txt, plots/, scripts/.

---

## Outputs

- **Base:** `stars_raw.csv`, `stars_clean.csv` (cleaned: non-null radius/nu_max, relative errors ≤ 20%), plots (radius vs luminosity, nu_max vs radius, delta_nu vs mass).  
- **Enriched:** Solar-normalized columns, derived observables (mean_density_proxy, surface_gravity_proxy, energy_proxy, q_proxy), luminosity_computed/luminosity_source, evolutionary_stage and error columns where available; constants.json with solar constants; extra plots and atomic reference table.

---

## License

MIT. See [LICENSE](LICENSE).
