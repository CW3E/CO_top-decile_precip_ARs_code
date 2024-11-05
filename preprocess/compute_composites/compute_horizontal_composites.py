######################################################################
# Filename:    compute_horizontal_composites.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create horizontal composites of 2D data (ivt and 700 hPa geopotential heights)
#
######################################################################

import sys
import itertools
import xarray as xr
import numpy as np
import pandas as pd
# import wrf


# import personal modules
# Path to modules
sys.path.append('../../modules')
# Import my modules
import composite_funcs as cfuncs


## load ar dates within region
region_lst = ['san_juan', 'gulf_of_mexico'] ## 'san_juan' 'baja' 'gulf_of_mexico'
lag_lst = [0, 1]
ar_varname = 'ar_scale'

for i, region in enumerate(region_lst):
    for j, lag in enumerate(lag_lst):
        ## load ar dates with region (include HUC8 and start date for adding trajectories)
        fname = '../../out/bbox_dates_{0}_full_{1}.csv'.format(region, ar_varname)
        df = pd.read_csv(fname)
        df['day'] = pd.to_datetime(df['time']).dt.normalize()
        
        ## make a copy of the df but keep only time/index
        d = {'datetime': df.day.values}
        ar_dates = pd.DataFrame(d)
        ar_dates = ar_dates.drop_duplicates(subset=['datetime'])
        ar_dates = ar_dates.sort_values(by='datetime')
        ar_dates = ar_dates.datetime.values + pd.Timedelta(days=lag)
        
        ## iterate through options
        varname_lst = ['700z', 'ivt']
        ssn_lst = ['DJF', 'MAM', 'JJA', 'SON', 'NDJFMA', 'MJJASO']
        anom_lst = [True, False]
        
        a = [varname_lst, ssn_lst, anom_lst]
        
        option_lst = list(itertools.product(*a))
        for i, lst in enumerate(option_lst):
            anomaly = lst[2]
            ssn = lst[1]
            varname = lst[0]
            print('Anomaly:', anomaly, 'Season:', ssn, 'Variable:', varname)
            tmp = cfuncs.compute_horizontal_composites(varname, anomaly, ar_dates, ssn, region, lag)