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

- `stellar-seismic-download` — download catalogs
- `stellar-seismic-process` — process and clean data, build plots

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
