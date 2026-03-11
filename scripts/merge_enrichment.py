#!/usr/bin/env python3
"""
Merge base catalog (stars_clean from zip or output) with enrichment data.
Writes stars_enriched.csv to output_enriched/.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import os
from pathlib import Path

from stellar_seismic_catalog.enrichment.merge_data import (
    load_base_catalog,
    load_base_raw,
    merge_enrichment,
)


def main() -> None:
    zip_path = os.environ.get("STELLAR_SEISMIC_INPUT_ZIP")
    fallback = os.environ.get("STELLAR_SEISMIC_OUTPUT", "output")
    output = Path(os.environ.get("STELLAR_SEISMIC_ENRICHED_OUTPUT", "output_enriched"))
    output.mkdir(parents=True, exist_ok=True)
    base = load_base_catalog(zip_path, fallback)
    base_raw = load_base_raw(zip_path, fallback)
    if not base_raw.empty:
        base_raw.to_csv(output / "stars_raw.csv", index=False)
    enrich_dir = output / "enrichment_data"
    merged = merge_enrichment(base, enrich_dir)
    merged.to_csv(output / "stars_enriched.csv", index=False)
    print(f"Merged {len(merged)} rows -> {output / 'stars_enriched.csv'}")


if __name__ == "__main__":
    main()
