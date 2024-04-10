#!/bin/bash
######################################################################
# Filename:    rsync_ERA5.sh
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to copy ERA5 subset files from Skyriver to Expanse
# To run, type "bash rsync_ERA5.sh"
######################################################################

datadir="/data/projects/Comet/cwp140/preprocessed/ERA5/"
outdir="/expanse/nfs/cw3e/cwp140/preprocessed/ERA5/"

# names of files to loop through
array=(
# surface_pressure
zero_degree_level
# ivt
)

outer=1 # set outer loop counter
# Begin outer loop (e.g. each variable)
for i in ${!array[*]}
do 
    echo "Pass $outer in outer loop."
    varname="${array[$i]}"

    indir="${datadir}/${varname}/"
    out="${outdir}/${varname}"
    # rsync -anv --progress ${indir} dnash@login.expanse.sdsc.edu:/${out} # to test the list of files being sent
    rsync -avh --progress ${indir} dnash@login.expanse.sdsc.edu:/${out}

    echo "${varname} copy complete"
        
    let "outer+=1" # Increment outer loop counter
    echo "$varname copy complete"
    echo           # Space between output blocks in pass of outer loop
    
done

exit 0