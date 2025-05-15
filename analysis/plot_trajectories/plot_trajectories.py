######################################################################
# Filename:    plot_trajectories.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create figures of trajectory heatmaps and spaghetti maps based on config file
#
######################################################################

import os, sys
import yaml
import geopandas as gpd
import pandas as pd

sys.path.append('/home/dnash/repos/eaton_scripps_CO_ARs/modules')
from load_trajectories import load_trajectories_based_on_region
from plot_trajectory_maps import plot_trajectory_heatmaps

### Imports config name from argument when submit
yaml_doc = sys.argv[1]
config_name = sys.argv[2]

# import configuration file for season dictionary choice
config = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)
ddict = config[config_name]

path_to_data = '/expanse/nfs/cw3e/cwp140/' 
path_to_out  = '../out/'       # output files (numerical results, intermediate datafiles) -- read & write

## load all trajectories categorized by region
ds = load_trajectories_based_on_region()

# Load trajectory GeoJSON data
gdf = gpd.read_file("/home/dnash/repos/eaton_scripps_CO_ARs/out/trajectories.geojson")
gdf.crs = 'epsg:3857'
gdf = gdf.set_index(pd.to_datetime(gdf['start_date']))

## create plot based on current config
plot_trajectory_heatmaps(ds, gdf, ddict)