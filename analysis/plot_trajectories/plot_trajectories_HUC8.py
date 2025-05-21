######################################################################
# Filename:    plot_trajectories_HUC8.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create figures of trajectory heatmaps and spaghetti maps based on config file
#
######################################################################

import os, sys
import yaml
import geopandas as gpd
import pandas as pd
import numpy as np
import cmocean.cm as cmo
import cartopy
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colorbar import Colorbar # different way to handle colorbar
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
from cartopy.mpl.geoaxes import GeoAxes
import cartopy.feature as cfeature

## personal modules
sys.path.append('/home/dnash/repos/eaton_scripps_CO_ARs/modules')
from load_trajectories import load_trajectories_based_on_region
from trajectory_post_funcs import calculate_heatmaps_from_trajectories
import customcmaps as ccmap
from utils import select_months_ds, select_months_df, get_startmon_and_endmon
from plotter import draw_basemap, plot_arscale_cbar
from load_shapefiles import load_region_shp, load_HUC8
from plot_trajectory_maps import subset_gdf_to_plot, subset_data_to_plot, plot_heatmaps, plot_spaghetti_maps

### Imports config name from argument when submit
yaml_doc = 'config_1.yaml'
config_name = 'job_37'

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
ssn = ddict['SSN']
ARDT = ddict['ARDT']
ar = ddict['AR']
HUC8_lst = ddict['HUC8_lst']

left_lbl = ['Upper Yampa', 'Roaring Fork', 'Upper Gunnison', 'Upper San Juan']

## load watershed shapefile and predefined regions shapefile
polys = load_HUC8()

# Set up projection
datacrs = ccrs.PlateCarree()  ## the projection the data is in
mapcrs = ccrs.PlateCarree() ## the projection you want your map displayed in

ext = [-140., -90., 20, 50]

# Set tick/grid locations
tx = 10
ty = 5
dx = np.arange(ext[0],ext[1]+tx,tx)
dy = np.arange(ext[2],ext[3]+ty,ty)

titlestring = [['(a)', '(b)', '(c)', '(d)'],
               ['(e)', '(f)', '(g)', '(h)']]

nrows = 6
ncols = 2

## Use gridspec to set up a plot with a series of subplots that is
## n-rows by n-columns
gs = GridSpec(nrows, ncols, height_ratios=[1, 1, 1, 1, 0.05, 0.05], width_ratios = [1, 1], wspace=0.01, hspace=0.1)
## use gs[rows index, columns index] to access grids

fig = plt.figure(figsize=(7.75, 10.))
fig.dpi = 600
path_to_figs = '/home/dnash/repos/eaton_scripps_CO_ARs/figs/trajectory_figs/'
fname = path_to_figs + 'HUC8_trajectory_heatmaps_{0}_{1}_AR-{2}'.format(ssn, ARDT, ar)
fmt = 'png'

#####################
### PLOT HEATMAPS ###
#####################

# Add color bar axis
cbax = plt.subplot(gs[-1,0]) # colorbar axis

col_idx = [0, 0, 0, 0]
row_idx = [0, 1, 2, 3]
blon_lst = [False, False, False, True]
for i, (row, col) in enumerate(zip(row_idx, col_idx)):
    ax = fig.add_subplot(gs[row,col], projection=mapcrs)
    ax = draw_basemap(ax, extent=ext, xticks=dx, yticks=dy,left_lats=True, 
                      right_lats=False, bottom_lons=blon_lst[i])
    
    ax.set_extent(ext, datacrs)
    ax.add_feature(cfeature.STATES, edgecolor='0.4', linewidth=0.8)
    ## add labels
    ax.text(-0.16, 0.5, left_lbl[i], va='bottom', ha='center',
                rotation='vertical', rotation_mode='anchor', fontsize=13,
                transform=ax.transAxes)

    subset = subset_data_to_plot(ds, ARDT, ssn, ar, HUC8=HUC8_lst[i])
    ax = plot_heatmaps(ax, cbax, subset, ARDT, AR=ar, normalize=None, HUC8=True)
    
    ## add in subbasin shapefile
    plot_poly = polys[(polys.HUC8 == str(HUC8_lst[i]))]
    plot_poly.crs = 'epsg:3857'
    plot_poly.plot(ax=ax, edgecolor='k', color='None', zorder=99, lw=0.75)

    ## add in a, b, c label
    ax.text(0.03, 0.96, titlestring[0][i], ha='left', va='top', transform=ax.transAxes, fontsize=11., backgroundcolor='white', zorder=101)

############################
### PLOT AR SCALE VALUES ###
############################

col_idx = [1, 1, 1, 1]
row_idx = [0, 1, 2, 3]
blon_lst = [False, False, False, True]
for i, (row, col) in enumerate(zip(row_idx, col_idx)):
    ax = fig.add_subplot(gs[row,col], projection=mapcrs)
    ax = draw_basemap(ax, extent=ext, xticks=dx, yticks=dy, left_lats=False, 
                      right_lats=False, bottom_lons=blon_lst[i])
    ax.set_extent(ext, datacrs)
    ax.add_feature(cfeature.STATES, edgecolor='0.4', linewidth=0.8, zorder=98)
    
    ## add spaghetti maps
    subset_gdf = subset_gdf_to_plot(gdf, ARDT, ssn, ar, HUC8=HUC8_lst[i])
    subset_gdf = subset_gdf.reset_index(drop=True)
    ax = plot_spaghetti_maps(ax, subset_gdf, datacrs)
            
    ## add in shapefile
    plot_poly = polys[(polys.HUC8 == str(HUC8_lst[i]))]
    plot_poly.crs = 'epsg:3857'
    plot_poly.plot(ax=ax, edgecolor='k', color='None', zorder=99, lw=0.75)
    ## add in a, b, c label
    ax.text(0.03, 0.96, titlestring[1][i], ha='left', va='top', transform=ax.transAxes, fontsize=11., backgroundcolor='white', zorder=101)

## Add color bar
cbax = plt.subplot(gs[-1,-1]) # colorbar axis
plot_arscale_cbar(cbax, orientation='horizontal')

fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi, transparent=True)
fig.clf()