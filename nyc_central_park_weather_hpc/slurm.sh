#!/usr/bin/env bash
#SBATCH --job-name=nyc-weather-intro
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --output=weather-%j.out
#SBATCH --error=weather-%j.err
# IMPORTANT: Specify --partition/--account as required by your cluster site.
set -euo pipefail
cd "$(dirname "$0")"
module load Python 2>/dev/null || true  # Replace with available YCRC Python module if needed
python analyze.py
