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
elevation_map_with_inset
sensitivity_test_trajectory_mar2003
trajectory_figs/trajectory_heatmaps_NDJFMA_tARget_AR-True
ARScale_trajectory_heatmaps_AR
NDJFMA_IVT_700z_composite_lag0
choropleth_map_portrait_NDJFMA
time_series_extreme
)

# new names to be fig<name given in array2>
array2=(
1
2
3
4
5
6
7
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
array=(
ar_freq_overhead
trajectory_figs/trajectory_heatmaps_MJJASO_tARget_AR-True
trajectory_figs/trajectory_heatmaps_NDJFMA_tARget_AR-False
trajectory_figs/trajectory_heatmaps_MJJASO_tARget_AR-False
trajectory_figs/trajectory_heatmaps_NDJFMA_ar_AR-True
trajectory_figs/trajectory_heatmaps_MJJASO_ar_AR-True
trajectory_figs/trajectory_heatmaps_NDJFMA_ar_scale_AR-True
trajectory_figs/trajectory_heatmaps_MJJASO_ar_scale_AR-True
MJJASO_IVT_700z_composite_lag0
NDJFMA_IVT_700z_composite_lag1
MJJASO_IVT_700z_composite_lag1
choropleth_map_portrait_MJJASO
## choropleth variability
)

# new names to be fig<name given in array2>
array2=(
1
2
3
4
5
6
7
8
9
10
11
12
)
for i in ${!array[*]}
do 
    ## copy to final_figs dir
    infile="${maindir}${array[$i]}.png"
    outfile="${finaldir}figS${array2[$i]}.png"
#     echo "${infile} to ${outfile}"
    cp -v ${infile} ${outfile}
    ## copy to overleaf dir
    outfile="${overleafdir}figS${array2[$i]}.png"
    cp -v ${infile} ${outfile}
done

## convert png to pdf
# python png_to_pdf.py

## zip to single file
cd ../figs/final_figs
zip figs.zip fig*