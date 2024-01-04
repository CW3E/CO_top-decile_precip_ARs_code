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
import math
import glob
import yaml

server='expanse'
if server == 'comet':
    path_to_data = '/data/projects/Comet/cwp140/'
elif server == 'expanse':
    path_to_data = '/expanse/lustre/scratch/dnash/temp_project/'


config_file = '../preprocess/calculate_trajectories/config_1.yaml'
job_info = 'job_1' # this is the job name

## change to list of HUC8 IDs
config = yaml.load(open(config_file), Loader=yaml.SafeLoader) # read the file
ddict = config[job_info] # pull the job info from the dict
HUC8_ID = ddict['HUC8_ID']

fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO.nc'
ds = xr.open_dataset(fname)
# get list of event dates from first HUC8
ds = ds.sel(HUC8=HUC8_ID)
ds = ds.where(ds.extreme == 1, drop=True)
event_dates = ds.date.values
nevents = len(event_dates)

## append filenames to a list
print('Gathering filenames ...')
fname_lst = []
for i, dt in enumerate(event_dates):
    ts = pd.to_datetime(str(dt)) 
    d = ts.strftime("%Y%m%d")
    fname = path_to_data + 'preprocessed/ERA5_trajectories/PRISM_HUC8_{0}_{1}.nc'.format(HUC8_ID, d)
    fname_lst.append(fname)


## open all files for current HUC8
# final_ds = xr.open_mfdataset(fname_lst, combine='nested', concat_dim=pd.Index(event_dates[9:], name="start_date"), engine='netcdf4')
# final_ds
ds_lst = []
for i, fname in enumerate(fname_lst):
    ds = xr.open_dataset(fname)
    ds_lst.append(ds)

## save all trajectories for current HUC8 as single netcdf
final_ds = xr.concat(ds_lst, pd.Index(event_dates, name="start_date"))

out_fname = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5_trajectories/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
final_ds.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')