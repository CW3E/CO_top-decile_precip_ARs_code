######################################################################
# Filename:    combine_trajectory_ARscale_IVT.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to add in IVT data and AR Scale data to the trajectories from Skyriver
#
######################################################################

# Standard Python modules
import os, sys
import glob
import numpy as np
import pandas as pd
import xarray as xr
import re

# import personal modules
# Path to modules
sys.path.append('../modules')
# Import my modules
from utils import roundPartial, find_closest_MERRA2_lon
from trajectory import combine_IVT_and_trajectory, combine_arscale_and_trajectory, combine_coastal_IVT_and_trajectory

path_to_data = '/data/projects/Comet/cwp140/' 
path_to_out  = '../out/'       # output files (numerical results, intermediate datafiles) -- read & write
path_to_figs = '../figs/'      # figures


## load Rutz AR
fname = path_to_data + 'preprocessed/MERRA2/MERRA2_Rutz_US-West.nc'
ar = xr.open_dataset(fname)

## load AR scale
fname = path_to_data + 'preprocessed/MERRA2/MERRA2_ARScale_US-West.nc'
arscale = xr.open_dataset(fname)

## load HUC8 IDs
fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO.nc'
ds = xr.open_dataset(fname)
HUC8_IDs = ds.HUC8.values ## get list of HUC8 IDs

## loop through all HUC8s
for i, HUC8_ID in enumerate(HUC8_IDs):
    print(i, HUC8_ID)
    ## load watershed trajectories
    fname = path_to_data + 'preprocessed/ERA5_trajectories/final/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    ERA5 = xr.open_dataset(fname)
    # ERA5 = ERA5.assign_coords({"lon": ERA5.longitude, "lat": ERA5.latitude, "time": ERA5.time})
    # ERA5 = ERA5.drop_vars(["latitude", "longitude"])

    ds_lst = []
    ## loop through all trajectories for that watershed
    for i, st_date in enumerate(ERA5.start_date.values):
        tmp = ERA5.sel(start_date=st_date)
        # ## combine IVT data   
        # tmp = combine_IVT_and_trajectory(tmp)
        # ## add arscale
        # tmp = combine_arscale_and_trajectory(tmp, arscale, ar)
        
        ## add coastal IVT
        tmp = combine_coastal_IVT_and_trajectory(tmp, arscale)
        ds_lst.append(tmp)

    ## merge final dataset
    final_ds = xr.concat(ds_lst, dim="start_date")

    out_fname = '/home/dnash/comet_data/preprocessed/ERA5_trajectories/latest/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    final_ds.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')
