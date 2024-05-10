######################################################################
# Filename:    preprocess_ERA5_arscale.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to compute AR Scale (Ralph et al., 2019) for annual ERA5 IVT files
#
######################################################################

import os, sys
import yaml
import xarray as xr
import pandas as pd
import numpy as np

path_to_data = '/expanse/nfs/cw3e/cwp140/'

## get year from config file
config_file = str(sys.argv[1]) # this is the config file name
job_info = str(sys.argv[2]) # this is the job name
config = yaml.load(open(config_file), Loader=yaml.SafeLoader) # read the file
ddict = config[job_info] # pull the job info from the dict

year = ddict['year']

def preprocess(ds):
    latmin, latmax, lonmin, lonmax = 10., 70., -140., -80.
    ds = ds.sel(lat=slice(latmin, latmax), lon=slice(lonmin, lonmax))
    return ds


year = int(year)
print(year)
## create list of IVT filenames for the year plus month prior
if year > 2000:
    start_date='{0}-12-01'.format(year-1) # we want December from the previous year
elif year == 2000: 
    start_date='{0}-01-01'.format(year) # start with Jan 1
    
end_date='{0}-12-31'.format(year)

dates = pd.date_range(start=start_date, end=end_date, freq='1MS')
# put into pandas df
d ={"date": dates}
df = pd.DataFrame(data=d)
df['month']= df['date'].dt.month.map("{:02}".format)
df['year']= df['date'].dt.year

# create list of daily ERA5 files for each AR
filenames = []
for j, row in df.iterrows():
    filenames.append('/expanse/nfs/cw3e/cwp140/preprocessed/ERA5/ivt/{0}{1}_IVT.nc'.format(row['year'], row['month']))
    
# open all files within the AR period
era = xr.open_mfdataset(filenames, combine='by_coords', preprocess=preprocess)
ds = era.compute()

## compute duration of IVT >= 250.
AR = xr.where(ds.IVT >= 250, 1, 0)
a = AR != 0 # this will place True for all rows where AR is not 0

# get the temporal resolution in hours
t = ds['time'].isel(time=1) - ds['time'].isel(time=0) 
nhrs = t.values.astype('timedelta64[h]') # convert to hours

## this grabs the start and stop indices of each AR
tmp = a.cumsum()-a.cumsum().where(~a).ffill(dim='time').fillna(0).astype(int) # cumulative sum where not 0
duration = tmp*nhrs.astype(int)
duration = duration.rename("duration")
# duration = duration.compute()
ds = xr.merge([ds, duration])

## compute preliminary rank
pr1 = xr.where((ds.IVT >= 250.) & (ds.IVT < 500.), 1, np.nan)
pr2 = xr.where((ds.IVT >= 500.) & (ds.IVT < 750.), 2, np.nan)
pr3 = xr.where((ds.IVT >= 750.) & (ds.IVT < 1000.), 3, np.nan)
pr4 = xr.where((ds.IVT >= 1000.) & (ds.IVT < 1250.), 4, np.nan)
pr5 = xr.where((ds.IVT >= 1250.), 5, np.nan)

prelim_rank = xr.merge([pr1, pr2, pr3, pr4, pr5], compat='no_conflicts')
prelim_rank = prelim_rank.rename({"IVT": "prelim_rank"})
# prelim_rank = prelim_rank.compute()
## put into ds
ds = xr.merge([ds, prelim_rank])

## compute final rank
rank24 = xr.where((ds.duration < 24.), ds.prelim_rank - 1, np.nan)
rank48 = xr.where((ds.duration >= 48.), ds.prelim_rank + 1, np.nan)
rank0 = xr.where((ds.duration >= 24.) & (ds.duration <48.), ds.prelim_rank, np.nan)

rank = xr.merge([rank24.rename('rank'), rank48.rename('rank'), rank0.rename('rank')], compat='no_conflicts')
ds = xr.merge([ds, rank])
ds = ds.drop_vars(["duration", "prelim_rank"]) # drop unnecessary variables
ds = ds.sel(time=slice('{0}-01-01'.format(year), '{0}-12-31'.format(year))) # slice down to the current year
print('ds size in GB {:0.2f}\n'.format(ds.nbytes / 1e9))
path_to_data = '/expanse/nfs/cw3e/cwp140/preprocessed/ARScale_ERA5/'
fname_out = path_to_data + 'ERA5_ARScale_{0}.nc'.format(year)
ds.to_netcdf(path=fname_out, mode = 'w', format='NETCDF4')