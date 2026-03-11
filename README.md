# Stellar Seismic Catalog

Download and process stellar asteroseismic catalogs from MAST (Kepler/TESS), VizieR, and Gaia DR3.

- **Sources:** [tech.spec.md](tech.spec.md)
- **Layout and rules:** [docs/LAYOUT_STANDARDS.md](docs/LAYOUT_STANDARDS.md), [docs/PROJECT_RULES.md](docs/PROJECT_RULES.md)

## Install

```bash
pip install stellar-seismic-catalog
```

Or from the repo (with `.venv` activated):

```bash
pip install -e .
```

## Usage

After install:

- `stellar-seismic-download` — download catalogs (writes to `output/`, creates `sources.txt`)
- `stellar-seismic-process` — process and clean data, build plots (writes CSVs and `plots/`)
- `stellar-seismic-pack` — pack results into `stellar_seismic_catalog.zip` (README, CSVs, plots/, scripts/, sources.txt)

Data must be obtained and then packed into the zip archive; run pack after process (or process can call the pack step internally).

From the repo (no install):

```bash
python scripts/download_catalogs.py
python scripts/process_catalogs.py
```

## Outputs

- `stars_raw.csv`, `stars_clean.csv` (in `output/` or configured path)
- Plots (e.g. radius vs luminosity, nu_max vs radius, delta_nu vs mass) in `output/plots/` or equivalent

## License

MIT. See [LICENSE](LICENSE).
