# Enrichment data sources (VizieR and others)

Author: Vasiliy Zdanovskiy  
email: vasilyvz@gmail.com

Catalogs used or available to fill missing fields in the stellar seismic catalog.

## Mode width (line width of radial modes)

| Catalog | VizieR ID | Content | Merge key |
|---------|-----------|---------|-----------|
| Vrard+ 2018, KIC red giants radial modes | **J/A+A/616/A94** | Gamma0 (global radial mode width), e_Gamma0, numax, Dnu, KIC | star_id (KIC) |
| Tables: dataprob, datafreq | | ~5000 red giants, Kepler | |

**Used in pipeline:** J/A+A/616/A94/dataprob → mode_width = Gamma0.

## Magnetic activity (chromospheric)

| Catalog | VizieR ID | Content | Merge key |
|---------|-----------|---------|-----------|
| Boro Saikia+ 2018, cool stars chromospheric activity | **J/A+A/616/A108** | Smean, Smed, logRpHK; _RA, _DE | position (ra, dec) |
| Table: catalog | | 4454 cool stars, Ca II H&K | |

**Used in pipeline:** J/A+A/616/A108/catalog → magnetic_activity = Smean via positional match. Overlap with Kepler/APOKASC-2 may be zero (catalog is Hipparcos-oriented).

## Uncertainties (Teff, numax, delta_nu)

- **APOKASC-2** (J/ApJS/239/32/table5): has s_M(cor), s_R(cor) (fractional mass/radius errors). No e_Teff, e_Numax, e_Dnu columns in the published VizieR table5.
- **J/A+A/616/A94** (Vrard): has e_Gamma0, e_M; no e_Numax, e_Dnu in the global-parameter tables.
- Teff_err, nu_max_err, delta_nu_err: no single VizieR catalog identified that provides these for the full APOKASC-2 set; left empty or to be added from literature/other tables later.

## Already used

- **APOKASC-2** J/ApJS/239/32/table5: evolutionary_stage (ES), stellar_class (ES), mass_err (s_M(cor)), radius_err (s_R(cor)).
- **Gaia DR3** I/355/gaiadr3: distance (from Plx), rotation (Vbroad) via CDS XMatch.
- **NIST ASD**: atomic_reference_raw.csv.
