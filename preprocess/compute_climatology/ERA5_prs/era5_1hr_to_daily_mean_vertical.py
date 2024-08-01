"""
Filename:    era5_1hr_to_daily_mean_vertical.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Resample 1hr ERA5 pressure level data to daily data and save netCDF. To run: `conda activate SEAK-impacts`, then `python era5_1hr_to_daily_mean_vertical.py`
"""

import sys
import os
import itertools
import xarray as xr
import numpy as np
import pandas as pd
from functools import partial
import yaml
import glob
import shutil

# import personal modules
# Path to modules
sys.path.append('../../../modules')
# Import my modules
from utils import generate_ptlst_from_start_end

region = 'baja' ## 'san_juan' 'baja' 'gulf_of_mexico'

config_file = str(sys.argv[1]) # this is the config file name
job_info = str(sys.argv[2]) # this is the job name

config = yaml.load(open(config_file), Loader=yaml.SafeLoader) # read the file
ddict = config[job_info] # pull the job info from the dict

year = ddict['year']
month = ddict['month']

## create bounding boxes for regions
d = {'baja': {'ext': [-115., -110., 27., 32.],
              'start_pt': [33.0, -118.],
              'end_pt': [29.0, -110.]},
     
     'san_juan': {'ext': [-109., -105., 37., 39.],
              'start_pt': [38.0, -112.],
              'end_pt': [38.0, -102.]},

     'gulf_of_mexico': {'ext': [-99., -93., 25., 31.],
              'start_pt': [28.0, -100.],
              'end_pt': [31.0, -93.]}
    }

coord_pairs = generate_ptlst_from_start_end(d[region]['start_pt'][1], d[region]['start_pt'][0], d[region]['end_pt'][1], d[region]['end_pt'][0], pairs=False)

def _preprocess(x, coord_pairs):
    lon_pairs = xr.DataArray(coord_pairs[1], dims=['location'])
    lat_pairs = xr.DataArray(coord_pairs[0], dims=['location'])
    return x.sel(longitude=lon_pairs, latitude=lat_pairs, level=slice(1000., 200.))

path_to_data = '/expanse/nfs/cw3e/cwp140/downloads/ERA5/ERA5/{0}/'.format(year)
fname_pattern = "era5_nhemi_025dg_1hr_uvwq_{0}{1}*.nc".format(year, month)
list_of_files = glob.glob(path_to_data+fname_pattern)

print('copying files to scratch space..')
## copy files to /dev/shm/${SLURM_JOB_ID}
job_ID = os.environ["SLURM_JOB_ID"]
# self.scratch_path = '/dev/shm/{0}/'.format(int(job_ID))
scratch_path = '/expanse/lustre/scratch/dnash/temp_project/trajs/{0}/'.format(int(job_ID))
os.makedirs(os.path.dirname(scratch_path), exist_ok=True)

for i, fname in enumerate(list_of_files):
    shutil.copy(fname, scratch_path) # copy file over to data folder

print('computing daily mean..')
partial_func = partial(_preprocess, coord_pairs=coord_pairs)
ds = xr.open_mfdataset(scratch_path+fname_pattern, engine='netcdf4', combine='by_coords', preprocess=partial_func)  
ds = ds.resample(time='1D').mean()

print('writing to netcdf..')
ds = ds.load()
path_to_out = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5/cross_section/daily/'
out_fname = "era5_{2}_025dg_daily_uvwq_{0}{1}.nc".format(year, month, region)
ds.to_netcdf(path=path_to_out+out_fname, mode = 'w', format='NETCDF4')

## remove temporary files in /dev/shm/job_ID
print('removing tmp files...')
shutil.rmtree(scratch_path)