"""
Filename:    load_composites.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: scripts to load composite nc into single nc for different regions, variables, and lag values
"""

import xarray as xr
import pandas as pd

def load_non_anomaly_composites(ssn, ext):
    ## iterate through options
    region_lst = ['baja', 'san_juan', 'gulf_of_mexico', 'pnw']
    varname_lst = ['700z', 'ivt']
    lag_lst = [0, 1]
    ds_lst3 = []
    for h, region in enumerate(region_lst):  
        tmp_lst = []
        for i, varname in enumerate(varname_lst):  
            ds_hc_lst = []
            for j, lag in enumerate(lag_lst):
                ## load non-anomaly composite data
                path = '/home/dnash/DATA/preprocessed/ERA5_composites/'
                fname = path + '{0}/{2}/composite_{0}_{1}_lag{3}.nc'.format(varname, ssn, region, lag)
            
                ds = xr.open_dataset(fname)
                ds = ds.sel(latitude=slice(ext[3], ext[2]), longitude=slice(ext[0], ext[1]))
                ds_hc_lst.append(ds)
        
            ## concat ds_lst along ssn
            tmp = xr.concat(ds_hc_lst, pd.Index(lag_lst, name="lag"))
            tmp_lst.append(tmp)
        
        ## merge two datasets
        ds3 = xr.merge(tmp_lst)
        ds_lst3.append(ds3)
    
    ds_hc = xr.concat(ds_lst3, pd.Index(region_lst, name="region"))
    return ds_hc

def load_anomaly_composites(ssn, ext):
    ## iterate through options
    region_lst = ['baja', 'san_juan', 'gulf_of_mexico', 'pnw']
    varname_lst = ['700z', 'ivt']
    lag_lst = [0, 1]
    
    ds_lst3 = []
    ds_lst4 = []
    for h, region in enumerate(region_lst):  
        tmp_lst = []
        tmp_lst2 = []
        for i, varname in enumerate(varname_lst):  
            ds_lst = []
            ds_lst2 = []
            for j, lag in enumerate(lag_lst):
                ## load anomaly composite data
                path = '/home/dnash/DATA/preprocessed/ERA5_composites/'
                fname1 = path + '{0}/{2}/filtered_anomaly_composite_{0}_{1}_lag{3}.nc'.format(varname, ssn, region, lag)
                fname2 = path + '{0}/{2}/filtered_anomaly_composite_tvals_{0}_{1}_lag{3}.nc'.format(varname, ssn, region, lag)
            
                ds = xr.open_dataset(fname1)
                ds = ds.sel(latitude=slice(ext[3], ext[2]), longitude=slice(ext[0], ext[1]))
                ds_lst.append(ds)
        
                ds2 = xr.open_dataset(fname2)
                ds2 = ds2.sel(latitude=slice(ext[3], ext[2]), longitude=slice(ext[0], ext[1]))
                ds_lst2.append(ds2)
        
            ## concat ds_lst along ssn
            tmp = xr.concat(ds_lst, pd.Index(lag_lst, name="lag"))
            tmp_lst.append(tmp)
        
            tmp2 = xr.concat(ds_lst2, pd.Index(lag_lst, name="lag"))
            tmp_lst2.append(tmp2)
    
        ## merge two datasets
        ds3 = xr.merge(tmp_lst)
        ds_lst3.append(ds3)
    
        ## merge tvalue anomaly datasets
        ds4 = xr.merge(tmp_lst2)
        ds_lst4.append(ds4)
    
    ds_hc = xr.concat(ds_lst3, pd.Index(region_lst, name="region"))
    ds_tval = xr.concat(ds_lst4, pd.Index(region_lst, name="region"))

    return ds_hc, ds_tval