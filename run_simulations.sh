#!/bin/bash

prj_dir=/storage/homefs/km21a901/NetworkMaterial
script_dir=$prj_dir/SwineNet-model
intBeg="2014.01"
intEnd="2014.03"

module load R/4.0.0-foss-2020a

num_simulations=(0:100)

for run in ${num_simulations[@]}; do
  job_file="${run}.job"

    echo "#!/bin/bash
#SBATCH --job-name=network-simulation-${run}
#SBATCH --time=0:30:00
#SBATCH --cpus-per-task=5
#SBATCH --output=ojob_%j.txt
#SBATCH --error=ejob_%j.txt
Rscript --vanilla $script_dir/cli.py $intBeg $intEnd" > $job_file
    sbatch $job_file

  done
done