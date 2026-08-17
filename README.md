# la_crime

Los Angeles temperature–crime–ENSO pilot analysis (Alliance / Fir HPC).

This repository contains analysis **code**, **SLURM job scripts**, and **results** (tables/figures). Raw downloads and large processed panels stay on Scratch (`$SCRATCH/la_crime_data`) and are not versioned.

Licensed under the [MIT License](LICENSE).

<!-- RESULTS-LINKS:START -->
## Latest results

_Auto-updated on push. Snapshot commit `5ac3bc8` · 2026-08-17 08:02 UTC_

### Findings reports
- [MECHANISM FINDINGS](results/MECHANISM_FINDINGS.md)
- [SPATIAL WEATHER FINDINGS](results/SPATIAL_WEATHER_FINDINGS.md)
- [FULL SAMPLE FINDINGS](results/FULL_SAMPLE_FINDINGS.md)
- [PILOT FINDINGS](results/PILOT_FINDINGS.md)
- [RESULTS SUMMARY](results/RESULTS_SUMMARY.md)

### Key tables
- [crime_type_temperature_bins.csv](results/crime_type_temperature_bins.csv)
- [crime_type_hot_p95.csv](results/crime_type_hot_p95.csv)
- [crime_mechanism_classification.csv](results/crime_mechanism_classification.csv)
- [spatial_main_models.csv](results/spatial_main_models.csv)
- [lax_vs_spatial.csv](results/lax_vs_spatial.csv)
- [main_models.csv](results/main_models.csv)
- [temperature_bins.csv](results/temperature_bins.csv)
- [extreme_heat.csv](results/extreme_heat.csv)

### Figures
- [fig10_spatial_crime_type_comparison.png](results/figures/fig10_spatial_crime_type_comparison.png)
- [fig11_lax_vs_spatial.png](results/figures/fig11_lax_vs_spatial.png)
- [fig12_crime_type_temperature_response.png](results/figures/fig12_crime_type_temperature_response.png)
- [fig13_interpersonal_vs_property_heat.png](results/figures/fig13_interpersonal_vs_property_heat.png)
- [fig1_temperature_crime.png](results/figures/fig1_temperature_crime.png)
- [fig2_temperature_bins.png](results/figures/fig2_temperature_bins.png)
- [fig3_extreme_heat.png](results/figures/fig3_extreme_heat.png)
- [fig4_oni_temperature.png](results/figures/fig4_oni_temperature.png)
- [fig5_oni_first_stage.png](results/figures/fig5_oni_first_stage.png)
- [fig6_placebo_leads.png](results/figures/fig6_placebo_leads.png)
- [fig7_distributed_lags.png](results/figures/fig7_distributed_lags.png)
- [fig8_spatial_temperature_support.png](results/figures/fig8_spatial_temperature_support.png)
- [fig9_spatial_temperature_bins_violent.png](results/figures/fig9_spatial_temperature_bins_violent.png)
<!-- RESULTS-LINKS:END -->

## Setup

```bash
module load StdEnv/2023 python/3.11.5
bash setup.sh   # creates ~/la_crime_env and installs requirements.txt

# Once per clone: auto-update README result links on git push
git config core.hooksPath hooks
chmod +x hooks/pre-push
```

## Run (city-level pipeline)

```bash
cd /path/to/la_crime
sbatch slurm/run.sbatch
```

Uses account `def-ncoops_cpu` and stores downloads under `$SCRATCH/la_crime_data`.

## Run (spatial weather pipeline)

```bash
sbatch slurm/run_spatial.sbatch
```

## Scripts

| Script | Role |
|--------|------|
| `01_download.py` | LAPD crime, NOAA weather, ONI |
| `02_build.py` | Daily/monthly panels + offense-code classification |
| `03_analyze.py` | Preferred models, placebos, lags, robustness |
| `04_diagnose_dates.py` | Date-range diagnostics |
| `05_diagnostics.py` | Temperature-bin / heat-episode support |
| `06_spatial_weather_download.py` | Multi-station NOAA weather |
| `07_build_area_panel.py` | LAPD area × day panel |
| `08_spatial_analysis.py` | Area + date FE spatial models |
| `09_mechanism_analysis.py` | Crime-type temperature response curves |
| `offense_codes.py` | Violent / property / mechanism Crm Cd crosswalk |
| `config.py` | Paths and sample windows |

## Notes

- Preferred violent outcome uses the offense-code crosswalk (not keyword proxies).
- Large inputs live under `$SCRATCH/la_crime_data` (gitignored). Analysis tables/figures are in `results/`.
- The **Latest results** section above is refreshed automatically on each `git push` (see `hooks/pre-push`).
- Licensed under MIT.