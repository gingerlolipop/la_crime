#!/bin/bash
#SBATCH --job-name=la_spatial
#SBATCH --account=def-ncoops_cpu
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --output=slurm-spatial-%j.out

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
module purge
module load StdEnv/2023
module load python/3.11.5
source ~/la_crime_env/bin/activate

export DATA_DIR="$SCRATCH/la_crime_data"
export PYTHONPATH="$SLURM_SUBMIT_DIR/scripts:${PYTHONPATH:-}"

python scripts/06_spatial_weather_download.py
python scripts/07_build_area_panel.py
python scripts/08_spatial_analysis.py
