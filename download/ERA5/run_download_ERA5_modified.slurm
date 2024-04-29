#!/bin/bash
#SBATCH --account=CWP162
#SBATCH --partition=cw3e-shared
#SBATCH -N 1 # Ensure that all cores are on one machine
#SBATCH --nodes=1 # specifies how many nodes to use (each node has 24 cores)
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH -t 48:00:00 # Runtime in HH:MM:SS
#SBATCH -o slurm_out/output_%a # File to which STDOUT will be written
#SBATCH -e slurm_out/output_err%a # File to which STDERR will be written
#SBATCH --job-name=download_ERA5
#SBATCH --mail-type=ALL # Type of email notification- BEGIN,END,FAIL,ALL
#SBATCH --mail-user=dnash@ucsd.edu # Email to which notifications will be sent

# Activate Anaconda work environment
source /home/${USER}/.bashrc
source activate cds 
 
outer=874      # set outer loop counter
start_job='874'
end_job='999'
# Loop to extract single variable from netCDF files, then concatenate into yearly files
# Begin outer loop (e.g. each job)
for jobID in $(seq $start_job $end_job)
do
    echo "${jobID} download started"
    linevar="python getERA5.py config_1.yaml 'job_${jobID}'"
    echo $linevar
    eval " $linevar"
    let "outer+=1" # Increment outer loop counter
    echo "${jobID} download complete"
    echo           # Space between output blocks in pass of outer loop
done
