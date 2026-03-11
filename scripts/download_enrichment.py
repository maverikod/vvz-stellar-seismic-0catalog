#!/usr/bin/env python3
"""
Download enrichment data: VizieR (ES, errors), Gaia (distance), NIST atomic reference.
Writes to output_enriched/enrichment_data/ and output_enriched/atomic_reference_raw.csv.

Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com
"""

import os
from pathlib import Path

from stellar_seismic_catalog.enrichment.download_data import (
    fetch_atomic_reference,
    fetch_gaia_distance,
    fetch_vizier_enrichment,
)


def main() -> None:
    output = Path(os.environ.get("STELLAR_SEISMIC_ENRICHED_OUTPUT", "output_enriched"))
    enrich_dir = output / "enrichment_data"
    viz_df = fetch_vizier_enrichment(enrich_dir)
    fetch_gaia_distance(viz_df[["star_id", "ra", "dec"]], enrich_dir)
    fetch_atomic_reference(output)
    print(f"Enrichment data written to {enrich_dir}")


if __name__ == "__main__":
    main()
