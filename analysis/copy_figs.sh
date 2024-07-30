#!/bin/bash
######################################################################
# Filename:    copy_figs.sh
# Author:      Deanna Nash dlnash@ucsb.edu
# Description: Script to copy final figures to one folder and save as pdf
#
######################################################################

# Input parameters
maindir="../figs/" # main figure folder
finaldir="../figs/final_figs/" # final figure folder
overleafdir="/home/dnash/repos/CO_top-decile_precip_ARs/"

# fig names in main folder
array=(
ar_freq_overhead
sensitivity_test_trajectory_mar2003
choropleth_map_portrait
time_series_extreme
ARScale_basin_WY
heatmaps_basin_WY
## horizontal composites
## vertical composites
## schematic
)

# new names to be fig<name given in array2>
array2=(
1
2
3
4
5
6
)



for i in ${!array[*]}
do 
    ## copy to final_figs dir
    infile="${maindir}${array[$i]}.png"
    outfile="${finaldir}fig${array2[$i]}.png"
#     echo "${infile} to ${outfile}"
    cp -v ${infile} ${outfile}
    ## copy to overleaf dir
    outfile="${overleafdir}fig${array2[$i]}.png"
    cp -v ${infile} ${outfile}
done

# ### supplemental figs
# supp_array=(
# composite_ar_types_bias
# )

# ## new names to be given
# supp_array2=(
# 1
# )
# for i in ${!supp_array[*]}
# do 
#     infile="${maindir}${supp_array[$i]}.png"
#     outfile="${finaldir}figS${supp_array2[$i]}.png"
# #     echo "${infile} to ${outfile}"
#     cp -v ${infile} ${outfile}
# done

## convert png to pdf
# python png_to_pdf.py

## zip to single file
cd ../figs/final_figs
zip figs.zip fig*