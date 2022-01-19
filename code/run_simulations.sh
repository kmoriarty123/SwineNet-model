#!/bin/bash

prj_dir=/storage/homefs/km21a901/NetworkMaterial/SwineNet-model
script_dir=$prj_dir/code
output_dir=$prj_dir/output
start_date="2014-01-01"
end_date="2014-03-30"
#num_runs=5

module load Python/3.9.5-GCCcore-10.3.0

#for run_id in {1..10}; do
for run_id in {1..1000}; do
  job_file="network-simulation-${run_id}.job"

    echo "#!/bin/bash
#SBATCH --job-name=network-simulation-${run_id}
#SBATCH --time=7:00:00
#SBATCH --cpus-per-task=1
#SBATCH --output=ojob_%j.txt
#SBATCH --error=ejob_%j.txt
python $script_dir/cli.py --start_date=$start_date --end_date=$end_date --curr_run=$run_id --output_dir=$output_dir" > $job_file
    sbatch $job_file
done
