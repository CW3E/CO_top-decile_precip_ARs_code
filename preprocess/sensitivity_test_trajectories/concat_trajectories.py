######################################################################
# Filename:    concat_trajectories.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to concatenate trajectories from each watershed
#
######################################################################

import sys
import xarray as xr
import numpy as np
import pandas as pd
import glob

## get list of HUC8 IDs
HUC8_lst = [14050001, ## upper yampa
            14030002, ## upper dolores
            10190002, ## 'Upper South Platte'
            11020001 ## Arkansas Headwaters
            ]

## loop through all HUC8s
for i, HUC8_ID in enumerate(HUC8_lst):
    print('Processing HUC8 {0}'.format(HUC8_ID))
    fname_pattern = '/expanse/lustre/scratch/dnash/temp_project/preprocessed/ERA5_sensitivity_test_trajectories/PRISM_HUC8_{0}*.nc'.format(HUC8_ID)
    fname_lst = glob.glob(fname_pattern)
    # print(fname_lst)
    ds_lst = []
    for i, fname in enumerate(fname_lst):
        ds = xr.open_dataset(fname)
        ds_lst.append(ds)
    
    ds = xr.merge(ds_lst)

    ## save file
    fname = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5_trajectories/sensitivity_tests/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    ds.to_netcdf(path=fname, mode = 'w', format='NETCDF4')