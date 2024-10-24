######################################################################
# Filename:    compute_cross-section_composites.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create cross section composites of vertical pressure level data
#
######################################################################

import sys
import itertools
import yaml
import xarray as xr
import numpy as np
import pandas as pd
from functools import partial
import metpy.calc as mpcalc
from metpy.units import units


# import personal modules
# Path to modules
sys.path.append('../../modules')
import composite_funcs as cfuncs
from utils import generate_ptlst_from_start_end

## load configuration file
region = 'baja' ## 'san_juan' 'baja' 'gulf_of_mexico'
# import configuration file for case study choice
yaml_doc = '../../data/domains.yml'
d = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)

coord_pairs = generate_ptlst_from_start_end(d[region]['start_pt'][1], d[region]['start_pt'][0], d[region]['end_pt'][1], d[region]['end_pt'][0], pairs=False)

## read AR dates from csv file
fname = '../../out/line_dates_{0}.csv'.format(region)
df = pd.read_csv(fname)
df['day'] = pd.to_datetime(df['datetime']).dt.normalize()
df = df.sort_values(by=['datetime'])
# df = df.set_index(pd.to_datetime(df['datetime'])) ## set daily values as index
ar_dates = df['day'].values
## create year month columns in dataframe 
# df['yearmonth'] = df.index.strftime("%Y%m")
new = df.drop_duplicates('day')
ar_dates = new['day'].values


## iterate through options for freezing level
varname = 'sp_deg0l'
ssn_lst = ['DJF', 'MAM', 'JJA', 'SON', 'NDJFMA', 'MJJASO']

for i, ssn in enumerate(ssn_lst):
    print('Season:', ssn, 'Variable:', varname)
    tmp = cfuncs.compute_freezing_level_composites(varname, df['datetime'].values, ssn, region)

## iterate through options for uvwq data
varname_lst = ['uvwq']
ssn_lst = ['DJF', 'MAM', 'JJA', 'SON', 'NDJFMA', 'MJJASO']
anom_lst = [True, False]

a = [varname_lst, ssn_lst, anom_lst]

option_lst = list(itertools.product(*a))
for i, lst in enumerate(option_lst):
    anomaly = lst[2]
    ssn = lst[1]
    varname = lst[0]
    print('Anomaly:', anomaly, 'Season:', ssn, 'Variable:', varname)
    tmp = cfuncs.compute_vertical_composites(varname, anomaly, ar_dates, ssn, region)