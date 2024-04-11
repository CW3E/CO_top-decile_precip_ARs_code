# Activate Anaconda work environment
source /home/${USER}/.bashrc
source activate cds

outer=106      # set outer loop counter
start_job='106'
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