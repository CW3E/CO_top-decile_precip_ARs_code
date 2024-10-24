"""
Filename:    era5_1hr_to_daily_mean_sfc.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Resample 1hr ERA5 surface pressure and freezing level data to daily data and save netCDF. To run: `conda activate SEAK-impacts`, then `python era5_1hr_to_daily_mean_vertical.py`
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

import metpy.calc as mpcalc
from metpy.units import units

# import personal modules
# Path to modules
sys.path.append('../../../modules')
# Import my modules
from utils import generate_ptlst_from_start_end

region = 'gulf_of_mexico2' ## 'san_juan' 'baja' 'gulf_of_mexico'

config_file = str(sys.argv[1]) # this is the config file name
job_info = str(sys.argv[2]) # this is the job name
config = yaml.load(open(config_file), Loader=yaml.SafeLoader) # read the file
ddict = config[job_info] # pull the job info from the dict
year = ddict['year']

# import configuration file for case study choice
yaml_doc = '../../../data/domains.yml'
d = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)

coord_pairs = generate_ptlst_from_start_end(d[region]['start_pt'][1], d[region]['start_pt'][0], d[region]['end_pt'][1], d[region]['end_pt'][0], pairs=False)

def _preprocess(x, coord_pairs):
    lon_pairs = xr.DataArray(coord_pairs[1], dims=['location'])
    lat_pairs = xr.DataArray(coord_pairs[0], dims=['location'])
    return x.sel(longitude=lon_pairs+360, latitude=lat_pairs, method='nearest')
    
## load data
fname = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5/zero_degree_level/{0}_deg0l.nc'.format(year)
ds = xr.open_dataset(fname) # open dataset
ds = _preprocess(ds, coord_pairs) ## subset to coord_pairs
## convert freezing level from m to hPa
heights = units.Quantity(ds.deg0l.values, "m") ## add units to freezing level
deg0l = mpcalc.height_to_pressure_std(heights).magnitude # convert from m to hPa

## load surface pressure data
fname = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5/surface_pressure/{0}_sp.nc'.format(year)
sp = xr.open_dataset(fname)
sp = _preprocess(sp, coord_pairs) ## subset to coord_pairs

## add freezing level data to xarray
ds = sp.assign(deg0l=(['time', 'location'], deg0l)) 
# ds = ds.resample(time='1D').mean()

print('writing to netcdf..')
ds = ds.load()
path_to_out = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5/cross_section/sfc_prs_deg0l/'
out_fname = "era5_{1}_025dg_hourly_sp_deg0l_{0}.nc".format(year, region)
ds.to_netcdf(path=path_to_out+out_fname, mode = 'w', format='NETCDF4')
