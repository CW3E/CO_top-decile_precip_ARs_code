######################################################################
# Filename:    combine_trajectory_ARscale_IVT.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to add in AR Scale data to the trajectories
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
from trajectory import combine_IVT_and_trajectory, combine_arscale_and_trajectory

path_to_data = '/expanse/nfs/cw3e/cwp140/'
path_to_out  = '../out/'       # output files (numerical results, intermediate datafiles) -- read & write
path_to_figs = '../figs/'      # figures


## load Rutz AR
print('Loading Rutz AR data')
fname_pattern = path_to_data + 'preprocessed/MERRA2/MERRA2_Rutz_latlon_*.nc'
ar = xr.open_mfdataset(fname_pattern)

## load AR scale
print('Loading ERA5 AR scale')
fname_pattern = path_to_data + 'preprocessed/ARScale_ERA5/ERA5_ARScale_*.nc'
arscale = xr.open_mfdataset(fname_pattern)

## Load tARgetv4 AR data
fname = path_to_data + 'preprocessed/tARgetv4/globalARcatalog_ERA5_2000-2023_v4.0.nc'
tARgetv4 = xr.open_dataset(fname)

## load HUC8 IDs
print('Loading HUC8 IDs')
fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO_sp.nc'
ds = xr.open_dataset(fname)
HUC8_IDs = ds.HUC8.values ## get list of HUC8 IDs
# HUC8_IDs = ['14050001'] ## Upper Yampa
HUC8_IDs = ['14010001', '14080101', '14050001'] ## Colorado Headwaters and Upper San Juan

## loop through all HUC8s
for i, HUC8_ID in enumerate(HUC8_IDs):
    print(i, HUC8_ID)
    ## load watershed trajectories
    # fname = '/expanse/nfs/cw3e/cwp140/preprocessed/UCRB_trajectories/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    # fname = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5_trajectories/combined_extreme/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    # fname = path_to_data + 'preprocessed/ERA5_trajectories/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    fname = path_to_data + 'preprocessed/ERA5_trajectories/combined/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    ERA5 = xr.open_dataset(fname)
    ERA5 = ERA5.assign_coords({"lon": ERA5.longitude, "lat": ERA5.latitude, "time": ERA5.time})
    ERA5 = ERA5.drop_vars(["latitude", "longitude"])

    ds_lst = []
    ## loop through all trajectories for that watershed
    for i, st_date in enumerate(ERA5.start_date.values):
        tmp = ERA5.sel(start_date=st_date)
        
        # ## add arscale, Rutz AR, and coastal IVT
        print('Combining AR Scale ... {0}'.format(i))
        tmp = combine_arscale_and_trajectory(tmp, arscale, ar, tARgetv4)

        ds_lst.append(tmp)

    ## merge final dataset
    final_ds = xr.concat(ds_lst, dim="start_date")

    # out_fname = path_to_data + 'preprocessed/ERA5_trajectories/combined_extreme_AR/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    out_fname = '/expanse/nfs/cw3e/cwp140/preprocessed/UCRB_trajectories/combined/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    final_ds.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')
