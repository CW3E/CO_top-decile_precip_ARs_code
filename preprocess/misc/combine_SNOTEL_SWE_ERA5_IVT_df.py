######################################################################
# Filename:    combine_SNOTEL_SWE_ERA5_IVT_df.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: script to take .csv file of raw downloaded SNOTEL SWE data and combine it with ERA5 IVT for the grid cell closest to the station
#
######################################################################

# Standard Python modules
import xarray as xr
import pandas as pd
import numpy as np

path_to_data = '/data/projects/Comet/cwp140/'
path_to_out  = '../out/'       # output files (numerical results, intermediate datafiles) -- read & write
path_to_figs = '../figs/'      # figures

## read the SNOTEL data
station_name = 'Beartown' ## Beartown.csv  Schofield_Pass.csv  Whiskey_Park.csv
fname = path_to_data + 'downloads/SNOTEL/{0}.csv'.format(station_name)
df = pd.read_csv(fname)
# convert column names to a list
cols_list = df.columns.tolist()
# drop last 10 columns of summary information
df = df.drop(columns = cols_list[-10:])
## melt the dataframe to be a single column of values
df = pd.melt(df, id_vars=['date'], value_vars=cols_list[1:-10],var_name='year', value_name='SWE_accum')
## remove rows where date doesn't make sense (e.g., Feb 29, 1987)
df = df.dropna(subset='SWE_accum')
## set up time as index
df['year'] = df['year'].astype('str')
df['time'] = pd.to_datetime(df['date'].values + df['year'], format='%m-%d%Y')
df = df.set_index('time')
df = df.drop(columns = ['date', 'year'])
df = df.sort_index()

if station_name == 'Beartown':
    lat = 37.75
    lon = -107.50
    loc = 2
elif station_name == 'Schofield_Pass':
    lat = 39.00
    lon = -107.00
    loc = 1
elif station_name == 'Whiskey_Park':
    lat = 41.00
    lon = -107.00
    loc = 0
    
## read IVT
fname = '/data/projects/Comet/cwp140/preprocessed/ERA5/IVT_clim/*.nc'
ds = xr.open_mfdataset(fname, engine='netcdf4')
ds = ds.sel(location=loc, time=slice(df.index[0], df.index[-1]))
ds1 = ds.resample(time="1D").mean('time')
ds1 = ds1.compute()
df['mean_ivt'] = ds1.IVT.values ## add IVT values

ds2 = ds.resample(time="1D").max('time')
ds2 = ds2.compute()
df['max_ivt'] = ds2.IVT.values ## add IVT values

df['SWE_diff'] = df['SWE_accum'].diff() ## compute daily SWE accumulation

df.to_csv('../out/SNOTEL-SWE_ERA5-IVT_{0}.csv'.format(station_name))