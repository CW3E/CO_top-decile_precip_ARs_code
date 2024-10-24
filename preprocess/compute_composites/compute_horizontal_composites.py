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
%matplotlib inline
# import wrf


# import personal modules
# Path to modules
sys.path.append('../../modules')
# Import my modules
import composite_funcs as cfuncs


## load ar dates within region
region = 'baja' ## 'san_juan' 'baja' 'gulf_of_mexico'
fname = '../out/bbox_dates_{0}.csv'.format(region)
df = pd.read_csv(fname)
df['day'] = pd.to_datetime(df['datetime']).dt.normalize()
df = df.sort_values(by=['datetime'])
# df = df.set_index(pd.to_datetime(df['datetime'])) ## set daily values as index
ar_dates = df['day'].values
## create year month columns in dataframe 
# df['yearmonth'] = df.index.strftime("%Y%m")
new = df.drop_duplicates('day')
ar_dates = new['day'].values


%%time
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
    tmp = cfuncs.compute_horizontal_composites(varname, anomaly, ar_dates, ssn, region)