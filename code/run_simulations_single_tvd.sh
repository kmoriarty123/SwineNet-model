#!/bin/bash

prj_dir=/storage/homefs/km21a901/NetworkMaterial/SwineNet-model
script_dir=$prj_dir/code
output_dir=$prj_dir/output
start_date="2014-01-01"
end_date="2014-03-31"
infected_tvd_id=1593884
run_id=2

module load Python/3.9.5-GCCcore-10.3.0

#for run_id in {1..10}; do
#for run_id in {1..1000}; do
job_file="network-simulation-${run_id}.job"

    echo "#!/bin/bash
#SBATCH --job-name=network-simulation-${run_id}
#SBATCH --time=8:00:00
#SBATCH --cpus-per-task=1
#SBATCH --output=ojob_%j.txt
#SBATCH --error=ejob_%j.txt
python $script_dir/cli_single_tvd.py --start_date=$start_date --end_date=$end_date --curr_run=$run_id --stochastic --index_case_tvd_id=$infected_tvd_id" > $job_file
    sbatch $job_file
#done
