"""
Filename:    era5_6hr_to_daily_mean.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Resample 6hr ERA5 to daily data and save netCDF. To run: `conda activate SEAK-impacts`, then `python era5_6hr_to_daily_mean.py`

"""

import xarray as xr
import numpy as np

varname = 'ivt' ## 700z or ivt
start_year = 2000
end_year = 2023

for i, yr in enumerate(range(start_year, end_year+1)):
    print(yr)
    path_to_data = '/expanse/nfs/cw3e/cwp140/downloads/ERA5/'
    fname = path_to_data + '{0}/6hr/era5_namerica_025dg_6hr_{0}_{1}.nc'.format(varname, yr)
    
    ds = xr.open_dataset(fname)

    if varname == 'ivt':
        ## rename ivtv and ivtu
        ds = ds.rename({'p71.162': 'ivtu', 'p72.162': 'ivtv'})
        ## add ivt magnitude
        ds = ds.assign(ivt=np.sqrt(ds['ivtu']**2 + ds['ivtv']**2))

    ds = ds.resample(time='1D').mean()
    
    out_fname = path_to_data + '{0}/daily/era5_namerica_025dg_daily_{0}_{1}.nc'.format(varname, yr)
    ds.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')