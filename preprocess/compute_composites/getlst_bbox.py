######################################################################
# Filename:    getlst_bbox.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create dataframe with list of dates, lats, lons, and levels of trajectories that crossed the domain box and line
#
######################################################################

import sys
import xarray as xr
import numpy as np
import pandas as pd
import yaml

# import personal modules
sys.path.append('../../modules')
# Import my modules
from utils import roundPartial, generate_ptlst_from_start_end
from composite_funcs import flatten, find_time_bbox, find_time_line

## load configuration file
region = 'pnw' ## 'san_juan', 'san_juan2', 'baja' 'gulf_of_mexico'
ar_varname = 'ar_scale'
# import configuration file for case study choice
yaml_doc = '../../data/domains.yml'
d = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)

## load PRISM watershed precip dataset
path_to_data = '/expanse/nfs/cw3e/cwp140/'
fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO_sp.nc'
PRISM = xr.open_dataset(fname)
HUC8_lst = PRISM.HUC8.values ## get list of HUC8 IDs

ds_lst = []
## load final trajectory dataset
for i, HUC8_ID in enumerate(HUC8_lst):
    fname = path_to_data + 'preprocessed/ERA5_trajectories/combined_extreme_AR/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    traj = xr.open_dataset(fname)
    ds_lst.append(traj)

## concat ds_lst along HUC8 index
ds = xr.concat(ds_lst, pd.Index(HUC8_lst, name="HUC8"))

def get_line_csv(method, coord_pairs):
    df_lst = []
    HUC8_final = []
    ## loop through HUC8s and start_dates
    for i, HUC8 in enumerate(HUC8_lst):
        # subset to the current HUC8
        ## keep only trajectories associated with ARs
        tmp = ds.sel(HUC8=HUC8)
        tmp = tmp.where(tmp[ar_varname] > 0, drop=True)
        
        t_lst = []
        ## enumerate through start_dates of current subbasin
        for i, st_date in enumerate(tmp.start_date.values):
            ERA5 = tmp.sel(start_date=st_date)
            time_lst = find_time_line(ERA5, coord_pairs)
            t_lst.append(time_lst)
        
        t_lst = flatten(t_lst)
        if len(t_lst) == 0:
            pass
        elif len(t_lst) == 1:
            HUC8_final.append(HUC8)
            df_full = t_lst[0].expand_dims(dim={"time": 1}).to_dataframe()
            df_full['HUC8'] = HUC8
            df_lst.append(df_full)
        elif len(t_lst) > 1:
            HUC8_final.append(HUC8)
            df_full = xr.concat(t_lst, dim='time').to_dataframe()
            df_full['HUC8'] = HUC8
            df_lst.append(df_full)
    
    ## now we have a list of list of dates when AR trajectories crossed line
    ## concat df_lst
    df = pd.concat(df_lst)
    
    ## create a column with the coord pair
    df['coord_pair'] = list(zip(df.lat, df.lon))
    
    ## save as CSV dates_region-name.csv
    fname_out = '../../out/{2}_dates_{0}_full_{1}.csv'.format(region, ar_varname, method)
    df.to_csv(fname_out)
    
    ## make a copy of the df but keep only time/index
    d = {'datetime': df.index.values}
    times_df = pd.DataFrame(d)
    times_df = times_df.drop_duplicates(subset=['datetime'])
    
    ## save as CSV dates_region-name.csv
    fname_out = '../../out/{2}_dates_{0}_{1}.csv'.format(region, ar_varname, method)
    times_df.to_csv(fname_out)

    return times_df

# #### FOR CROSS SECTION METHOD ####
# print('... Generating list of dates for line...')
# coord_pairs = generate_ptlst_from_start_end(d[region]['start_pt'][1], d[region]['start_pt'][0], d[region]['end_pt'][1], d[region]['end_pt'][0], pairs=True)
# print(coord_pairs)
# times_df = get_line_csv('line', coord_pairs)

#### FOR BBOX METHOD ####     
print('... Generating list of dates for box...')
## create a dataset with lats and lons from ext
ext = d[region]['ext']
lats = np.arange(ext[2], ext[3]+0.25, 0.25)
lons = np.arange(ext[0], ext[1]+0.25, 0.25)

coord_pairs = []
for j, lon in enumerate(lons):
    for k, lat in enumerate(lats):
        coord_pairs.append((lat, lon))

print(coord_pairs)        
times_df = get_line_csv('bbox', coord_pairs)