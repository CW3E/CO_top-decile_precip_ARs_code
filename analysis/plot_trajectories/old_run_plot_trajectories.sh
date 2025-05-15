#!/bin/bash

# Activate Anaconda work environment
source /home/${USER}/.bashrc
source activate SEAK-impacts 
 
outer=1      # set outer loop counter
start_job='1'
end_job='36'
# Loop to extract single variable from netCDF files, then concatenate into yearly files
# Begin outer loop (e.g. each job)
for jobID in $(seq $start_job $end_job)
do
    echo "${jobID} plot started"
    linevar="python plot_trajectories.py config_1.yaml 'job_${jobID}'"
    echo $linevar
    eval " $linevar"
    let "outer+=1" # Increment outer loop counter
    echo "${jobID} plot complete"
    echo           # Space between output blocks in pass of outer loop
done
