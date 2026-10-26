#!/bin/bash
#SBATCH --job-name=python-demo
#SBATCH --partition=devel
#SBATCH --time=00:05:00
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --output=job-%j.out
#SBATCH --error=job-%j.err

# Set up the Python environment (jobs start outside any interactive shell)
module reset
module load miniconda
#conda activate workshops

echo "Running on: $(hostname)"
echo "Python path: $(which python)"
python --version

python analysis.py
