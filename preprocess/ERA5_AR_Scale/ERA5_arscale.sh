#!/bin/bash
######################################################################
# Filename:    ERA5_arscale.sh
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to compute AR Scale on ERA5 IVT data for yearly files
# To run, activate conda env with "conda activate UCRB-WY2023", then run the script with "bash ERA5_arscale.sh"
######################################################################

### Activate python

source /home/dnash/miniconda3/etc/profile.d/conda.sh 

### Activate conda env

# conda activate cds

# names of configuration dictionaries to loop through
array=(
job_14
job_15
job_16
job_17
job_18
job_19
job_20
job_21
job_22
job_23
)

# now loop through each configuration dictionary to download the ERA5 data

##TODO figure out how to input argument into python run file

for i in ${!array[*]}
do 
    inconfig="${array[$i]}"
    python preprocess_ERA5_arscale.py config_1.yaml ${inconfig}
done