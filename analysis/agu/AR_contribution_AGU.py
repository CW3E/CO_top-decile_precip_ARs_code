## import libraries
import sys
import glob
import re

import geopandas as gpd
import cartopy
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import pandas as pd
import cmocean.cm as cmo
from matplotlib.gridspec import GridSpec

# cartopy
import cartopy.crs as ccrs
import cartopy.feature as cfeature

# import personal modules
# Path to modules
sys.path.append('../../modules')
# Import my modules
import global_vars
from plotter import draw_basemap, plot_terrain
from utils import select_months_ds, select_months_df, get_startmon_and_endmon
import customcmaps as ccmap
from load_shapefiles import load_region_shp, load_HUC8
from plot_trajectory_maps import subset_gdf_to_plot

pd.options.display.float_format = "{:,.2f}".format # makes it so pandas tables display only first two decimals

path_to_data = global_vars.path_to_data
path_to_repo = global_vars.path_to_repo
path_to_out  = '../../out/'       # output files (numerical results, intermediate datafiles) -- read & write
path_to_figs = '../../figs/'      # figures

polys = load_HUC8()
regions = load_region_shp(polys)

ssn = 'NDJFMA'
start_mon, end_mon = get_startmon_and_endmon(ssn)
## load PRISM watershed precip dataset to get list of HUC8s
fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO_sp.nc'
PRISM = xr.open_dataset(fname)
## add water year to data as coordinate
water_year = (PRISM.date.dt.month >= 10) + PRISM.date.dt.year
PRISM.coords['water_year'] = water_year
HUC8_ID_lst = PRISM.HUC8.values ## get list of HUC8 IDs

## subset to ssn
PRISM = select_months_ds(PRISM, start_mon, end_mon, 'date')
## for each HUC8, what is the total WY precipitation?
PRISM_WY = PRISM.prec.groupby(PRISM.water_year).sum(dim="date").sum('water_year')

## for each HUC8, what is the total WY top-decile precipitation?
PRISM_90 = PRISM.where(PRISM.extreme == 1, drop=True)
PRISM_90WY = PRISM_90.prec.groupby(PRISM_90.water_year).sum(dim="date").sum('water_year')

# Load trajectory GeoJSON data
gdf = gpd.read_file(path_to_repo+"out/trajectories.geojson")
gdf.crs = 'epsg:3857'
gdf = gdf.set_index(pd.to_datetime(gdf['start_date']))

ARDT_lst = ['tARget', 'ar', 'ar_scale']
AR = True
df_lst = []
for j, ARDT in enumerate(ARDT_lst):
    prec_val = []
    for i, HUC8 in enumerate(HUC8_ID_lst):
        tmp = subset_gdf_to_plot(gdf, ARDT, ssn, AR, region=None, basin=None, HUC8=HUC8)
        prec_val.append(tmp.prec.sum())
    
    d = {ARDT: prec_val}
    df = pd.DataFrame(d)
    df_lst.append(df)

df = pd.concat(df_lst, axis=1)
df['HUC8'] = HUC8_ID_lst
df['WY'] = PRISM_WY.values
df['WY90'] = PRISM_90WY.values

for j, ARDT in enumerate(ARDT_lst):
    col_name = ARDT + '_WY_contr'
    df[col_name] = (df[ARDT] / df['WY']) * 100.

    col_name = ARDT + '_WY90_contr'
    df[col_name] = (df[ARDT] / df['WY90']) * 100.

# Perform the join using the 'merge' function
merged_gdf = polys.merge(df, on='HUC8')

# Set up projection
datacrs = ccrs.PlateCarree()  ## the projection the data is in
mapcrs = ccrs.PlateCarree() ## the projection you want your map displayed in

# Set tick/grid locations
ext1 = [-110.5, -100.5, 35.5, 42.] # extent of CO
dx = np.arange(-109., -102.,2)
dy = np.arange(36, 42,1)

# Create figure
fig = plt.figure(figsize=(6., 4.5))
fig.dpi = 300
fname = path_to_figs + 'choropleth_map_{0}_tARget_AGU'.format(ssn)
fmt = 'png'

# Grid layout
gs = GridSpec(
    1,
    2,
    height_ratios=[1],
    width_ratios=[1, 0.05],
    wspace=0.15,
    hspace=0.03,
)

# Add color bar axis
cbax = fig.add_subplot(gs[0,-1])
ARDT = 'tARget'

## Add axis for plot
ax = fig.add_subplot(gs[0,0], projection=mapcrs)
ax = draw_basemap(ax, extent=ext1, xticks=dx, yticks=dy,left_lats=True, right_lats=False, bottom_lons=True, mask_ocean=False, coastline=False)

## topo with gray shading
# cs = plot_terrain(ax, ext1)

# add choropleth watershed fraction
cbarticks = [10, 20, 30, 40, 50, 60, 70, 80, 90]
lgnd_kwds={"label": "Fraction of top-decile precipitation (%)", "orientation": "vertical", "ticks": cbarticks}
cmap, norm, bnds = ccmap.cmap_segmented(cmo.rain, np.arange(0, 110, 10))
col_name = ARDT + '_WY90_contr'
cf = merged_gdf.plot(ax=ax, column=col_name, cmap=cmap, vmin=0, vmax=80, norm=norm, alpha=0.8, legend=True, cax=cbax, legend_kwds=lgnd_kwds)
polys.plot(ax=ax, edgecolor='grey', color='None', linewidth=0.5, zorder=98)

ax.add_feature(cfeature.STATES, edgecolor='0.4', linewidth=0.8, zorder=199)

## add in region watershed shape - first time full opacity, second low opacity
# opac_lst = [1., 0.9]
# zord_lst = [98, 100]
# lw_lst = [0.75, 0.3]
opac_lst = [1.]
zord_lst = [98]
lw_lst = [0.75]
for (opac, zord, lw) in zip(opac_lst, zord_lst, lw_lst):
    regions.plot(ax=ax, edgecolor='k', color='None', linewidth=lw, zorder=zord, alpha=opac)

        
fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi)
