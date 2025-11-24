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
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colorbar import Colorbar
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature

sys.path.append("../../modules")
import global_vars
from plotter import draw_basemap, plot_arscale_cbar
from load_shapefiles import load_region_shp, load_HUC8
from load_trajectories import load_trajectories_based_on_region
from plot_trajectory_maps import subset_data_to_plot, subset_gdf_to_plot, plot_heatmaps, plot_spaghetti_maps

path_to_data = global_vars.path_to_data
path_to_figs = "../../figs/"
path_to_out  = '../../out/'       # output files (numerical results, intermediate datafiles) -- read & write

plot_type = 'heatmap' # 'ar_scale' or 'heatmap'
## create plot based on current config
# plot_trajectory_heatmaps(ds, gdf, ddict)
ssn = 'NDJFMA'
ARDT = 'tARget'
ar = True


if plot_type == 'heatmap':
    region = 'northwestern_CO'
    ext = [-140., -90., 20, 50]
    ticks_x = np.arange(-130., -80., 10)
    wspace = 0.01

elif plot_type == 'ar_scale':
    region = 'northern_upper_CO'
    ext = [-137., -100., 20, 50]
    ticks_x = np.arange(-130., -90., 10)
    wspace = 0.15

## load watershed shapefile and predefined regions shapefile
polys = load_HUC8()
plot_poly = load_region_shp(polys)
plot_poly = plot_poly.to_crs(epsg=4326)

## create figure
fig = plt.figure(figsize=(7., 5.0), dpi=300)
# Geographic extents

datacrs = ccrs.PlateCarree()
mapcrs = ccrs.PlateCarree()

# Tick/grid spacing
ticks_y = np.arange(20, 55., 5)

# Grid layout
gs = GridSpec(
    1,
    2,
    height_ratios=[1],
    width_ratios=[1, 0.05],
    wspace=wspace,
    hspace=0.03,
)

ax = fig.add_subplot(gs[0, 0], projection=mapcrs)
cbax = fig.add_subplot(gs[0, 1])

# Draw base map
ax = draw_basemap(
    ax,
    extent=ext,
    xticks=ticks_x,
    yticks=ticks_y,
    left_lats=True,
    right_lats=False,
    bottom_lons=True,
    mask_ocean=False,
    coastline=True,
)

# States boundaries
ax.add_feature(cfeature.STATES, edgecolor="0.4", linewidth=0.8, zorder=4)

if plot_type == 'heatmap':
    fname = f"../figs/single_panel_heatmap_{ssn}_{ARDT}_{region}"
    ds = load_trajectories_based_on_region() ## load all trajectories categorized by region
    subset = subset_data_to_plot(ds, ARDT, ssn, ar, region=region, basin=None, HUC8=None) ## subset based on config
    ax = plot_heatmaps(ax, cbax, subset, ARDT, AR=ar, normalize=None, cbar_orientation="vertical") ## plot heatmap

elif plot_type == 'ar_scale':
    fname = f"../figs/single_panel_trajectories_{ssn}_{ARDT}_{region}"
    # Load trajectory GeoJSON data
    gdf = gpd.read_file("../../out/trajectories.geojson")
    gdf.crs = 'epsg:4326'
    gdf = gdf.set_index(pd.to_datetime(gdf['start_date']))

    ## add spaghetti maps
    subset_gdf = subset_gdf_to_plot(gdf, ARDT, ssn, ar, region=region, basin=None, HUC8=None)
    subset_gdf = subset_gdf.reset_index(drop=True)
    ax = plot_spaghetti_maps(ax, subset_gdf, datacrs)
    plot_arscale_cbar(cbax, orientation='vertical')

for idx, (i, poly) in enumerate(plot_poly.iterrows()):
    feature = ShapelyFeature([poly.geometry], ccrs.PlateCarree(),
                             edgecolor='k', facecolor='none', linewidth=1.)
    ax.add_feature(feature, zorder=200)


fmt = "png"
fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi, transparent=True)
fig.clf()