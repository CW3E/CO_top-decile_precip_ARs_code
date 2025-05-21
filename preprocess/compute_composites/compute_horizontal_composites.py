######################################################################
# Filename:    compute_horizontal_composites.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create horizontal composites of 2D data (ivt and 700 hPa geopotential heights)
#
######################################################################

import sys
import yaml
import itertools
import xarray as xr
import numpy as np
import pandas as pd

# import personal modules
# Path to modules
sys.path.append('../../modules')
# Import my modules
import composite_funcs as cfuncs

## get dict info for job
config_file = str(sys.argv[1]) # this is the config file name
job_info = str(sys.argv[2]) # this is the job name

config = yaml.load(open(config_file), Loader=yaml.SafeLoader) # read the file
ddict = config[job_info] # pull the job info from the dict

region = ddict['region']
lag = ddict['lag']
ARDT = ddict['ARDT']
ssn = ddict['ssn']
anomaly = ddict['anom']
varname = ddict['varname']


## load ar dates with region (include HUC8 and start date for adding trajectories)
fname = '../../out/bbox_dates_{0}_full_{1}.csv'.format(region, ARDT)
df = pd.read_csv(fname)
df['day'] = pd.to_datetime(df['time']).dt.normalize() ## the time the trajectory crosses the box
# df['day'] = pd.to_datetime(df['start_time']).dt.normalize() ## the time the trajectorie is in Colorado

## make a copy of the df but keep only time/index
d = {'datetime': df.day.values}
ar_dates = pd.DataFrame(d)
ar_dates = ar_dates.drop_duplicates(subset=['datetime'])
ar_dates = ar_dates.sort_values(by='datetime')
ar_dates = ar_dates.datetime.values + pd.Timedelta(days=lag)

tmp = cfuncs.compute_horizontal_composites(varname, anomaly, ar_dates, ssn, region, lag)