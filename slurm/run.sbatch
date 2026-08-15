#!/bin/bash
#SBATCH --job-name=la_crime
#SBATCH --account=def-ncoops_cpu
#SBATCH --time=02:00:00
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --output=slurm-%j.out

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
module purge
module load StdEnv/2023
module load python/3.11.5
source ~/la_crime_env/bin/activate

# Keep raw downloads outside the project tree (project lives at $SCRATCH/la_crime).
export DATA_DIR="$SCRATCH/la_crime_data"
export PYTHONPATH="$SLURM_SUBMIT_DIR/scripts:${PYTHONPATH:-}"

python scripts/01_download.py
python scripts/04_diagnose_dates.py
python scripts/02_build.py
python scripts/05_diagnostics.py
python scripts/04_diagnose_dates.py
python scripts/03_analyze.py
