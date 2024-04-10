######################################################################
# Filename:    compute_IVT_climatology_intwest.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to compute IVT climatology along interior west transect using ERA5 data
#
######################################################################

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
    ds = ds.drop_vars(["uIVT", "vIVT", "IWV"])
    ds = ds.sel(lon=x, lat=y, method='nearest')
    return ds

ds_lst = []
ntime_lst = []
path_to_ERA5 = '/data/downloaded/Reanalysis/ERA5/IVT/' 
for i, yr in enumerate(range(1979, 2024)):
    print(yr)
    fname = path_to_ERA5 + '{0}/ERA5_IVT_{0}*.nc'.format(yr)
    ds = xr.open_mfdataset(fname, engine='netcdf4', preprocess=preprocess)

    ## calculate maximum and average IVT
    max_IVT = ds.max('time')
    mean_IVT = ds.sum('time')
    ntime_lst.append(len(ds.time.values))

    max_IVT = max_IVT.rename({'IVT': 'maxIVT'})
    mean_IVT = mean_IVT.rename({'IVT': 'meanIVT'})
    
    ds = xr.merge([max_IVT, mean_IVT])
    ds = ds.compute() # compute
    
    ds_lst.append(ds)

## concat all datasets along time axis
final_ds = xr.concat(ds_lst, pd.Index(range(1979, 2024), name="time"))

## along all the years
## calculate maximum and average IVT
max_IVT = final_ds.maxIVT.max('time')
ntimes =  np.sum(ntime_lst)
mean_IVT = final_ds.meanIVT.sum('time') / ntimes

write_ds = xr.merge([max_IVT, mean_IVT])

## write to a netCDF
out_fname = path_to_data + 'preprocessed/ERA5_IVT_clim_{0}.nc'.format(loc_name)
write_ds.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')