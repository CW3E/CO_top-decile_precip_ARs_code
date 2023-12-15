######################################################################
# Filename:    calculate_trajectories.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to run backwards trajectories for CO PRISM watershed >90th percentile precipitation events
#
######################################################################

import os, sys
import yaml
import xarray as xr
import pandas as pd

path_to_repo = '/home/dnash/repos/eaton_scripps_CO_ARs/'
sys.path.append(path_to_repo+'modules')
from trajectory import calculate_backward_trajectory

path_to_data = '/expanse/lustre/scratch/dnash/temp_project/'

## get HUC8 from config file
config_file = str(sys.argv[1]) # this is the config file name
job_info = str(sys.argv[2]) # this is the job name

config = yaml.load(open(config_file), Loader=yaml.SafeLoader) # read the file
ddict = config[job_info] # pull the job info from the dict

HUC8_ID = ddict['HUC8']

## set starting lat/lon
## choose this based on extreme precip days
fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO.nc'
ds = xr.open_dataset(fname)
# start with single event from single watershed
ds = ds.sel(HUC8=HUC8_ID)
ds = ds.where(ds.extreme == 1, drop=True)
nevents = len(ds.prec) ## number of events for this HUC8

## loop through the current HUC8 times
ds_lst = []
start_date_lst = []
for i in range(nevents):
    s = calculate_backward_trajectory(ds=ds, idx=i, start_lev=700.)
    df = s.compute_trajectory()
    new_ds = df.to_xarray()
    start_date_lst.append(df.time.iloc[0])
    ds_lst.append(new_ds)

## save all trajectories for current HUC8 as single netcdf
final_ds = xr.concat(ds_lst, pd.Index(start_date_lst, name="start_date"))

## save trajectory data to netCDF file
print('Writing {0} to netCDF ....'.format(HUC8_ID))
out_fname = path_to_data + 'preprocessed/ERA5_trajectories/PRISM_HUC8_{0}.nc'.format(HUC8_ID) 
final_ds.load().to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')