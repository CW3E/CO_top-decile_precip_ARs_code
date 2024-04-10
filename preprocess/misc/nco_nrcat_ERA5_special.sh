#!/bin/bash
######################################################################
# Filename:    nco_nrcat_ERA5.sh
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to get extract single variables and save as monthly/yearly files
#
# - From ERA5 surface data, selects variable and concats from daily to monthly/yearly files
# - To run: change input parameters, then go to preprocess directory
# - "conda activate nco-env", then run "bash nco_nrcat_ERA5.sh"
######################################################################
varname="sp" ## sp, deg0l
longname="surface_pressure" ## surface_pressure, zero_degree_level
datadir="/data/projects/Comet/cwp140/downloads/ERA5/sp_zerodeg/"
outdir="/data/projects/Comet/cwp140/preprocessed/ERA5/${longname}/"
start_yr=2023
end_yr=2023
start_mon=05
end_mon=12

outer=1      # set outer loop counter

# Loop to extract single variable from netCDF files, then concatenate into yearly files
# Begin outer loop (e.g. each year)
for year in $(seq $start_yr $end_yr)
do
    echo "Pass $outer in outer loop."
    inner=1    # reset inner loop counter
    
    # Begin inner loop (e.g., each month)
    for month in $(seq -w $start_mon $end_mon)
    do
        echo "Pass $inner in inner loop."
        infile="${datadir}${year}${month}_sp.nc"
        echo "$infile"
        outfile="${outdir}tmp_${year}${month}_${varname}.nc"
        echo "$outfile"
        # extract single variable from netCDF file
        ncks -v ${varname} ${infile} ${outfile}
        # make time the record dimension - usually always make time record dimension
        # needed to concatenate files together - probably got an error when initially concatenated
        outfile2="${outdir}upk_${year}${month}_${varname}.nc"
        ncks -O --mk_rec_dmn time ${outfile} ${outfile2}
        
        let "inner+=1" # Increment inner loop counter
        echo "${year}${month} extraction complete"
    # End of inner loop
    done
    
    # # remove temporary files
    # rm -f ${inpattern}
    inpattern2="${outdir}tmp*.nc"
    rm -f ${inpattern2}
    
    let "outer+=1" # Increment outer loop counter
    echo "$year concatenation complete"
    echo           # Space between output blocks in pass of outer loop

done
# End of outer loop
