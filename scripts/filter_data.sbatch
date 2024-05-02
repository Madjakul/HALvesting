#!/bin/bash
#
#SBATCH --job-name=threads_filter_data       # Job name
#SBATCH --nodes=1                    # Run all processes on a single node
#SBATCH --ntasks=1                   # Run a single task	
#SBATCH --cpus-per-task=24            # Number of CPU cores per task
#SBATCH --mem=56gb                  # Total memory limit; if unit is not specified MB will be assumed
#SBATCH --partition=cpu_devel
#SBATCH --constraint=amd
#SBATCH --time=48:00:00              # Time limit hrs:min:sec
#SBATCH --output=logs/%x_%j.log            # Standard output and error log. %x denotes the job name, %j the jobid.

module purge
module load cmake

source /home/$USER/.bashrc
conda activate halvesting

mkdir logs

./scripts/filter_data.sh
