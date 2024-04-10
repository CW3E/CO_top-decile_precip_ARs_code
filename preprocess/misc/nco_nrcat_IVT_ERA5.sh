#!/bin/bash
######################################################################
# Filename:    nco_nrcat_IVT_ERA5.sh
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to get extract single variables and save as monthly/yearly files
#
# - From ERA5 surface data, selects variable and concats from daily to monthly/yearly files
# - To run: change input parameters, then go to preprocess directory
# - "conda activate nco-env", then run "bash nco_nrcat_ERA5.sh"
######################################################################
varname="IVT" ## IVT, uIVT, vIVT
longname="ivt" ## ivt, ivtu, ivtv
datadir="/data/downloaded/Reanalysis/ERA5/IVT/"
outdir="/data/projects/Comet/cwp140/preprocessed/ERA5/${longname}/"
start_yr=2000
end_yr=2023
start_mon=01
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
        
        ## statement to get the correct end day for each month
        ## if month == 1, 3, 5, 7, 8, 10, 12, then end_day == 31
        if [ $month == '01' -o  $month == '03' -o  $month == '05' -o  $month == '07' -o  $month == '08' -o  $month == '10' -o  $month == '12' ]
        then
        end_day='31'
        ## if month == 4, 6, 9, 11, then end_day == 30
        elif [ $month == '04' -o  $month == '06' -o  $month == '09' -o  $month == '11' ]
        then
        end_day='30'
        ## if month == 2 and year % 4 == 0 then end_day = 29
        elif [ $month == '02' -a $(( $year % 4 )) -eq 0 ]
        then
        end_day='29'
        ## else
        else
        end_day='28'
        fi
        
        inner2=1 # set counter for inner2 loop
        
        ## begin inner2 loop (e.g., each day)
        for day in $(seq -w '01' $end_day)
        do
            echo "Pass $inner2 in inner2 loop."
            
            infile="${datadir}${year}/ERA5_IVT_${year}${month}${day}.nc"
            echo "$infile"
            outfile="${outdir}tmp_${year}${month}${day}_${varname}.nc"
            echo "$outfile"
            
            # extract single variable from netCDF file and make time record dimension
            ncks -v ${varname} -O --mk_rec_dmn time ${infile} ${outfile}
            echo "${year}${month}${day} extraction complete"
            
            let "inner2+=1" # Increment inner2 loop counter
            # End of inner2 loop
        done
        
        # Concatentate files along the time dimension for each month
        inpattern="${outdir}tmp_${year}${month}*_${varname}.nc"
        outfile="${outdir}${year}${month}_${varname}.nc"
        ncrcat -h ${inpattern} ${outfile}
        echo "${year}${month} concatenation complete"
        
        ## remove temporary file
        rm -f ${inpattern}
        
        let "inner+=1" # Increment inner loop counter
    # End of inner loop
    done
    
    let "outer+=1" # Increment outer loop counter
    echo "$year complete"
    echo           # Space between output blocks in pass of outer loop

done
# End of outer loop

exit 0