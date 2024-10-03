"""
Filename:    contribution.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: functions for calculation precipitation contribution during the Water Year
"""

import os
import math
import xarray as xr
import pandas as pd
import numpy as np


def calculate_WY_contribution(path_to_data, PRISM, HUC8_ID, varname, thres):
    PRISM = PRISM.sel(HUC8=HUC8_ID)
    
    fname = path_to_data + 'PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    ds = xr.open_dataset(fname)
    ds['ar_scale'] = ds.ar_scale.fillna(0) 
    
    ## calculate the total top-decile precipitation in each WY
    extreme_days = PRISM.where(PRISM.extreme > 0, drop=True).date.values
    ext_prec = PRISM.sel(date = extreme_days)
    extreme_prec = ext_prec.prec.groupby(ext_prec.water_year).sum(dim="date")

    extreme_prec = extreme_prec.to_dataframe()
    extreme_prec = extreme_prec.rename(columns={"prec": "Total Precipitation"})
    
    ## calculate the AR-related top-decile prec
    extreme_AR = ds.sel(start_date = extreme_days)
    extreme_AR = extreme_AR.where(extreme_AR[varname] > thres, drop=True).start_date.values
    
    ## select those dates from the PRISM dataset
    tmp = PRISM.sel(date=extreme_AR)
    ## convert to pandas df
    tmp = tmp.prec.to_dataframe()
    
    extreme_ar_prec = tmp.groupby(["water_year"], dropna=False).sum("date")
    extreme_ar_prec = extreme_ar_prec.rename(columns={"prec": "AR Associated"})
    
    ## calculate the total contribution fraction
    # extreme_contr = (extreme_ar_prec / extreme_prec)*100
    
    ## put into a dataframe
    df = pd.concat([extreme_prec, extreme_ar_prec], axis=1)
    # df = pd.DataFrame({'Total Precipitation': extreme_prec.values,
    #                    'AR Associated': extreme_ar_prec.prec.values},
    #                   index=extreme_prec.water_year.values)

    df['Percent'] = (df['AR Associated']/df['Total Precipitation'])*100
    
    return df

def calculate_WY_contribution_total(path_to_data, PRISM, HUC8_ID, varname, thres):
    PRISM = PRISM.sel(HUC8=HUC8_ID)
    
    fname = path_to_data + 'PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    ds = xr.open_dataset(fname)
    ds['ar_scale'] = ds.ar_scale.fillna(0) 
    
    ## calculate the total precipitation in each WY
    annual_prec = PRISM.prec.groupby(PRISM.water_year).sum(dim="date") 
    annual_prec = annual_prec.to_dataframe()
    annual_prec = annual_prec.rename(columns={"prec": "Total Precipitation"})
    
    ## calculate the AR-related prec
    ar_days = ds.where(ds[varname] > thres, drop=True).start_date.values
    
    ## select those dates from the PRISM dataset
    tmp = PRISM.sel(date=ar_days)
    ## convert to pandas df
    tmp = tmp.prec.to_dataframe()
    
    ar_prec = tmp.groupby(["water_year"], dropna=False).sum("date")
    ar_prec = ar_prec.rename(columns={"prec": "AR Associated"})
    
    ## put into a dataframe
    df = pd.concat([annual_prec, ar_prec], axis=1)

    df['Percent'] = (df['AR Associated']/df['Total Precipitation'])*100
    
    return df