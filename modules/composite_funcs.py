######################################################################
# Filename:    composite_lst.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Functions to help create list of datetimes when trajectories are in certain domains 
#
######################################################################

import xarray as xr
import pandas as pd
import numpy as np

## personal modules
from utils import select_months_ds, generate_ptlst_from_start_end, roundPartial
from statistical_tests import ttest_1samp_new

def get_startmon_and_endmon(ssn):
    ## set start_mon and end_mon based on ssn
    if ssn == 'DJF':
        start_mon, end_mon = (12, 2)
    elif ssn == 'MAM':
        start_mon, end_mon = (3, 5)
    elif ssn == 'JJA':
        start_mon, end_mon = (6, 8)
    elif ssn == 'SON':
        start_mon, end_mon = (9, 11)
    elif ssn == 'NDJFMA':
        start_mon, end_mon = (11, 4)
    elif ssn == 'MJJASO':
        start_mon, end_mon = (5, 10)

    return start_mon, end_mon

def compute_freezing_level_composites(varname, ar_dates, ssn, region):
   ## load data
    path_to_data = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5/cross_section/sfc_prs_deg0l/'
    out_path = '/home/dnash/DATA/preprocessed/ERA5_composites/cross_section/'
    
    fname_pattern = path_to_data + "era5_{0}_025dg_hourly_sp_deg0l_*.nc".format(region)
    ds = xr.open_mfdataset(fname_pattern, engine='netcdf4', combine='by_coords')
    
    ## subset to AR dates
    ds = ds.sel(time=ar_dates)
    
    ## subset to start_month and end_month based on ssn
    start_mon, end_mon = get_startmon_and_endmon(ssn)
    tmp = select_months_ds(ds, start_mon, end_mon, 'time')
    tmp = tmp.load()
    print(len(tmp.time.values))

    if len(tmp.time.values) == 0:
        quantile = 0
        pass
    else:
        ## Calculate the percentiles
        quantile_arr = np.array([0.1, .5, .9])
        quantile = tmp.quantile(quantile_arr, dim=['time'], skipna=True)
        
        ## save as netcdf
        out_path = '/home/dnash/DATA/preprocessed/ERA5_composites/cross_section/'
        out_fname = out_path + 'composite_{0}_{1}_{2}.nc'.format(varname, ssn, region)
        quantile.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')

    return quantile
    
def compute_vertical_composites(varname, anomaly, ar_dates, ssn, region):
    ## function that computes composites (anomaly or non-anomaly) for defined start_mon and end_mon    
    ## for DJF, MAM, JJA, SON, NDJFMA, and MJJASON
    ## compute anomaly composites - anomaly = True
    ## compute non-anomaly composites - anomaly=False

    ## load data
    path_to_data = '/expanse/nfs/cw3e/cwp140/preprocessed/ERA5/cross_section/'
    out_path = '/home/dnash/DATA/preprocessed/ERA5_composites/cross_section/'
    
    if anomaly == True:
        fname_pattern = path_to_data + 'anomalies/daily_filtered_anomalies_{0}_*.nc'.format(region)
    else:
        fname_pattern = path_to_data + 'daily/era5_{0}_025dg_daily_uvwq_*.nc'.format(region)

    ds = xr.open_mfdataset(fname_pattern, engine='netcdf4', combine='by_coords')

    ## subset to AR dates
    ds = ds.sel(time=ar_dates)

    ## subset to start_month and end_month
    start_mon, end_mon = get_startmon_and_endmon(ssn)
    ds = select_months_ds(ds, start_mon, end_mon, 'time')
    ds = ds.load()
    ## run students t-test if anomaly == True
    if anomaly == True:    
        popmean = np.zeros([len(ds.level), len(ds.location)]) ## population mean
        ndays = len(ds.time) # number of unique days
        # calculate t-value based on ndays
        a_mean, tval_mask = ttest_1samp_new(a=ds, popmean=popmean, dim='time', n=ndays)

        ## write to netCDF
        out_fname = out_path + 'filtered_anomaly_composite_{0}_{1}_{2}.nc'.format(varname, ssn, region)
        a_mean.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')

        out_fname = out_path + 'filtered_anomaly_composite_tvals_{0}_{1}_{2}.nc'.format(varname, ssn, region)
        tval_mask.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')

    else:
        a_mean = ds.mean('time')
        out_fname = out_path + 'composite_{0}_{1}_{2}.nc'.format(varname, ssn, region)
        a_mean.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')

    return a_mean

def compute_horizontal_composites(varname, anomaly, ar_dates, ssn, region, lag):
    ## function that computes composites (anomaly or non-anomaly) for defined start_mon and end_mon    
    ## for DJF, MAM, JJA, SON, NDJFMA, and MJJASON
    ## compute anomaly composites - anomaly = True
    ## compute non-anomaly composites - anomaly=False

    ## set start_mon and end_mon based on ssn
    start_mon, end_mon = get_startmon_and_endmon(ssn)

    ## load data
    path_to_data = '/expanse/nfs/cw3e/cwp140/downloads/ERA5/'
    out_path = '/home/dnash/DATA/preprocessed/ERA5_composites/'
    
    if anomaly == True:
        fname_pattern = path_to_data + '{0}/anomalies/daily_filtered_anomalies_{0}_*.nc'.format(varname)
    else:
        fname_pattern = path_to_data + '{0}/daily/era5_namerica_025dg_daily_{0}_*.nc'.format(varname)

    ds = xr.open_mfdataset(fname_pattern, engine='netcdf4', combine='by_coords')

    ## subset to AR dates
    ds = ds.sel(time=ar_dates)

    ## subset to start_month and end_month
    ds = select_months_ds(ds, start_mon, end_mon, 'time')
    ds = ds.load()
    ndays = len(ds.time) # number of unique days
    print(ndays)

    ## run students t-test if anomaly == True
    if anomaly == True:    
        popmean = np.zeros([len(ds.latitude), len(ds.longitude)]) ## population mean
        
        # calculate t-value based on ndays
        a_mean, tval_mask = ttest_1samp_new(a=ds, popmean=popmean, dim='time', n=ndays)
        a_mean = a_mean.assign(ndays=ndays)
        ## write to netCDF
        out_fname = out_path + '{0}/{2}/filtered_anomaly_composite_{0}_{1}_lag{3}.nc'.format(varname, ssn, region, lag)
        a_mean.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')

        out_fname = out_path + '{0}/{2}/filtered_anomaly_composite_tvals_{0}_{1}_lag{3}.nc'.format(varname, ssn, region, lag)
        tval_mask.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')

    else:
        a_mean = ds.mean('time')
        a_mean = a_mean.assign(ndays=ndays)
        out_fname = out_path + '{0}/{2}/composite_{0}_{1}_lag{3}.nc'.format(varname, ssn, region, lag)
        a_mean.to_netcdf(path=out_fname, mode = 'w', format='NETCDF4')

    return a_mean

def flatten(xss):
    return [x for xs in xss for x in xs]
    
def find_time_bbox(ERA5, lats, lons):
    ## a function that gets the start dates and HUC8 ID 
    ## for the times when a trajectory is within the bbox
    
    ## create a dataset of the trajectory points that match ERA5 spacing
    t = xr.DataArray(ERA5.time.values, dims=['location'], name='time')
    
    # create a list of lat/lons that match ERA5 spacing
    x = xr.DataArray(roundPartial(ERA5.lon.values, 0.25), dims=['location'])
    y = xr.DataArray(roundPartial(ERA5.lat.values, 0.25), dims=['location'])
    
    x = xr.DataArray(ERA5.lon.values, dims=("location"), coords={"lon": x}, name='traj_lons')
    y = xr.DataArray(ERA5.lat.values, dims=("location"), coords={"lat": y}, name='traj_lats')
    
    # create a new dataset that has the trajectory lat and lons and the closest ERA5 lat/lons as coords
    z = xr.merge([x, y, t])
    
    ## Now loop through the lat/lon pairs and see where they match
    idx_lst = []
    for i, (x, y) in enumerate(zip(z.lon.values, z.lat.values)):
        for j, lon in enumerate(lons):
            for k, lat in enumerate(lats):
            
                ## test if lat/lon pair matches
                result_variable = (lon == x) & (lat == y)
        
                if (result_variable == True):
                    idx = (i, j, k) # (index of z, index of txtpts)
                    idx_lst.append(idx)
    ts_lst = []
    if len(idx_lst) > 0:
        for m, idx in enumerate(idx_lst):
            ## this is the time of the trajectory within the bounding box
            time_match = z.sel(location=idx_lst[m][0]).time.values
            ts = pd.to_datetime(str(time_match)).strftime('%Y-%m-%d %H')
            ts_lst.append(ts)

    return ts_lst

def find_time_line(ERA5, coord_pairs):
    ## create a dataset of the trajectory points that match ERA5 spacing
    t = xr.DataArray(ERA5.time.values, dims=['location'], name='time')
    lev = xr.DataArray(ERA5.level.values, dims=['location'], name='level')
    st_time = xr.DataArray(ERA5.start_date.values, dims=[], name='start_time')
    
    # create a list of lat/lons that match ERA5 spacing
    x = xr.DataArray(roundPartial(ERA5.lon.values, 0.25), dims=['location'])
    y = xr.DataArray(roundPartial(ERA5.lat.values, 0.25), dims=['location'])
    
    x = xr.DataArray(ERA5.lon.values, dims=("location"), coords={"lon": x}, name='traj_lons')
    y = xr.DataArray(ERA5.lat.values, dims=("location"), coords={"lat": y}, name='traj_lats')
    
    # create a new dataset that has the trajectory lat and lons and the closest ERA5 lat/lons as coords
    z = xr.merge([x, y, t, lev, st_time])
    
    idx_lst = []
    for i, (x, y) in enumerate(zip(z.lon.values, z.lat.values)):
        for j, pair in enumerate(coord_pairs):
            lat, lon = pair
            ## test if lat/lon pair matches
            result_variable = (lon == x) & (lat == y)
    
            if (result_variable == True):
                idx = (i, j) # (index of z, index of txtpts)
                idx_lst.append(idx)
    
    ts_lst = []
    if len(idx_lst) > 0:
        for m, idx in enumerate(idx_lst):
            ## this is the time of the trajectory when it crosses the transect
            time_match = z.sel(location=idx_lst[m][0])
            ts_lst.append(time_match) ## append the entire xr dataset
    
    return ts_lst