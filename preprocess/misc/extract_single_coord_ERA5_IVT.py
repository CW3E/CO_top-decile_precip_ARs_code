######################################################################
# Filename:    extract_single_coord_ERA5_IVT.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to grab single coordinates from ERA5 IVT
#
######################################################################

# Standard Python modules
import xarray as xr
import pandas as pd
import numpy as np

path_to_data = '/data/projects/Comet/cwp140/'
path_to_out  = '../out/'       # output files (numerical results, intermediate datafiles) -- read & write
path_to_figs = '../figs/'      # figures

# subset ds to the select points from int-west transect
loc_name = 'SNOTEL' ## SNOTEL, intwest
df = pd.read_csv('../data/latlon_{0}.txt'.format(loc_name), header=None, sep=' ', names=['latitude', 'longitude'], engine='python')

df['longitude'] = df['longitude']*-1
        
x = xr.DataArray(df['longitude'], dims=['location'])
y = xr.DataArray(df['latitude'], dims=['location'])

## Load ERA5 data
def preprocess(ds):
    # ds = ds.drop_vars(["uIVT", "vIVT", "IWV"])
    ds = ds.sel(lon=x, lat=y, method='nearest')
    return ds

ds_lst = []
ntime_lst = []
path_to_ERA5 = path_to_data + 'preprocessed/ERA5/ivt/' 
for i, yr in enumerate(range(2000, 2024)):
    print(yr)
    fname = path_to_ERA5 + '{0}*_IVT.nc'.format(yr)
    ds = xr.open_mfdataset(fname, engine='netcdf4', preprocess=preprocess)
    ds = ds.compute()
    fname = '/data/projects/Comet/cwp140/preprocessed/ERA5/IVT_clim/{0}.nc'.format(yr)
    ds.to_netcdf(path=fname, mode = 'w', format='NETCDF4')