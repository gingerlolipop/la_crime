# la_crime

Los Angeles temperature–crime–ENSO pilot analysis (Alliance / Fir HPC).

This repository contains **code only**. Raw data, processed panels, and results are kept on Scratch and are not versioned.

## Setup

```bash
module load StdEnv/2023 python/3.11.5
bash setup.sh   # creates ~/la_crime_env and installs requirements.txt
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
| `offense_codes.py` | Violent / property Crm Cd crosswalk |
| `config.py` | Paths and sample windows |

## Notes

- Preferred violent outcome uses the offense-code crosswalk (not keyword proxies).
- Large inputs/outputs live under `$SCRATCH/la_crime_data` and local `results/` (gitignored).
