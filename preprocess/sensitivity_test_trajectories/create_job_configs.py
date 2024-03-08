######################################################################
# Filename:    create_job_configs.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create .yaml configuration file to run job_array with slurm for running ERA5 CO PRISM HUC8 trajectories
#
######################################################################

import yaml
from itertools import chain
import itertools
import xarray as xr
import pandas as pd

## get list of HUC8 trajectories
path_to_data = '/expanse/lustre/scratch/dnash/temp_project/'
fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO.nc'
ds = xr.open_dataset(fname)

## we only want to test these four watersheds
HUC8_lst = [14050001, ## upper yampa
               14030002, ## upper dolores
               10190002, ## 'Upper South Platte'
               11020001 ## Arkansas Headwaters
              ]

## we want to test these dates
date_lst = ['20030317', '20030318', '20030319', ## March 2003 Blizzard (>50 inches in Denver)
            '20130910', '20130911', '20130912', ## Lyons Flooding
            '20170109', '20170110', ## really strong chinook winds (iconic Sequoia tree cave-in in CA)
            '20190313', '20190314' ## Bomb Cyclone Storm (same as Jerry's case study)
           ]

lev_lst = [800., 700., 600., 500.] # different heights to run through
time_lst = [0, 6, 12, 18] ## different times of the day to initialize
# using the centroid of the watershed, plus 0.25 degree in each direction
grid_offset = ['center', #[0, 0], # center grid
               'north', # [0.25, 0], # north grid
               'south', # [-0.25, 0], # south grid
               'east', # [0, 0.25], # east grid
               'west', # S[0, -0.25] # west grid
              ]


a = [HUC8_lst, date_lst, lev_lst, time_lst, grid_offset]
dict_lst = list(itertools.product(*a))

jobcounter = 0
filecounter = 0
## loop through to create dictionary for each job
d_lst = []
dest_lst = []
njob_lst = []
for i, dlist in enumerate(dict_lst):
    jobcounter += 1
    d = {'job_{0}'.format(jobcounter):
         {'HUC8_ID': dlist[0],
          'date': dlist[1],
          'lev': dlist[2],
          'hour': dlist[3],
          'grid': dlist[4]}}
    d_lst.append(d)
    
    if (jobcounter == 999):
        filecounter += 1
        ## merge all the dictionaries to one
        dest = dict(chain.from_iterable(map(dict.items, d_lst)))
        njob_lst.append(len(d_lst))
        ## write to .yaml file and close
        file=open("config_{0}.yaml".format(str(filecounter)),"w")
        yaml.dump(dest,file, allow_unicode=True, default_flow_style=None)
        file.close()
        
        ## reset jobcounter and d_lst
        jobcounter = 0
        d_lst = []
        
## now save the final config
filecounter += 1
## merge all the dictionaries to one
dest = dict(chain.from_iterable(map(dict.items, d_lst)))
njob_lst.append(len(d_lst))
## write to .yaml file and close
file=open("config_{0}.yaml".format(str(filecounter)),"w")
yaml.dump(dest,file, allow_unicode=True, default_flow_style=None)
file.close()

## create calls.txt for config_1(-8)

for i, njobs in enumerate(njob_lst):
    call_str_lst = []
    for j, job in enumerate(range(1, njobs+1, 1)):
        call_string = "python run_sensitivity_test_trajectories.py config_{0}.yaml 'job_{1}'".format(i+1, j+1)
        call_str_lst.append(call_string)
        
    ## now write those lines to a text file
    with open('calls_{0}.txt'.format(i+1), 'w',encoding='utf-8') as f:
        for line in call_str_lst:
            f.write(line)
            f.write('\n')
        f.close()