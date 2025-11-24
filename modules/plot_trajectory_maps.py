######################################################################
# Filename:    plot_trajectory_maps.py
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to create figures of heatmaps and spaghetti plots
#
######################################################################

## import modules
import os, sys
import xarray as xr
import numpy as np
import geopandas as gpd
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
from trajectory_post_funcs import calculate_heatmaps_from_trajectories
import customcmaps as ccmap
from utils import select_months_ds, select_months_df, get_startmon_and_endmon
from plotter import draw_basemap, plot_arscale_cbar
from load_shapefiles import load_region_shp, load_HUC8

def plot_heatmaps(ax, cbax, data, ARDT, AR=False, normalize=None, HUC8=False, cbar_orientation='horizontal'):
    '''
    Given a plot Axes and data, this returns the plot with a heatmap
    
    Parameters
    ----------
    ax : 
        plot Axes on which to draw the data
    
    data : 
        data to plot as heatmap using geopandas

    AR : bool
        whether the data being plotted is based on ARs or non-ARs

    normalize : bool
        whether you want to normalize the heatmaps
        
    Returns
    -------
    ax :
        plot Axes with heatmap
    
    '''

    ## now calculate heatmaps from remaining trajectories
    cell = calculate_heatmaps_from_trajectories(data, ARDT, normalize=normalize, AR=AR)
    print(cell['n_traj'].max())
    if normalize == None:
        if HUC8 == True:
            cmap, norm, bnds = ccmap.cmap_segmented(cmo.deep, np.arange(0, 25, 5))
        else:
            cmap, norm, bnds = ccmap.cmap_segmented(cmo.deep, np.arange(0, 110, 10))
        cmap_lbl = "Trajectory Frequency (count)"
    elif normalize == 'percent':
        cmap, norm, bnds = ccmap.cmap_segmented(cmo.deep, np.arange(0, 12, 2))
        cmap_lbl = "Trajectory Frequency (% of landfalling AR trajectories)"
        
    ## plotting based off of https://geopandas.org/en/stable/docs/user_guide/mapping.html
    cf = cell.plot(ax=ax, column='n_traj', cmap=cmap, vmin=bnds[0], vmax=bnds[-1], 
                   norm=norm, edgecolor=None, legend=True, cax=cbax,
                  legend_kwds={"label": cmap_lbl, "orientation": cbar_orientation})

    return ax

def plot_spaghetti_maps(ax, gdf, datacrs):
    '''
    Given a plot Axes and data, this returns the plot with the trajectories colored by AR scale
    
    Parameters
    ----------
    ax : 
        plot Axes on which to draw the data
    
    gdf : 
        pandas geodataframe to plot data
        
    Returns
    -------
    ax :
        plot Axes with trajectories
    '''
    

    colors = ['#A9A9A9', '#0ac1ff', '#04ff03', '#ffff03', '#ffa602', '#ff0100']
    ## Loop through AR scale values
    for k in range(0, 6):
        try:
            idx = (gdf['ar_scale'] == k)
            subset = gdf.loc[idx]
            for index, row in subset.iterrows():
                # Extract coordinates
                x_coords = row['geometry'].coords.xy[1].tolist()
                y_coords = row['geometry'].coords.xy[0].tolist()
                ax.plot(x_coords, y_coords, c=colors[k], transform=datacrs, alpha=0.2)
                cf = ax.scatter(x_coords, y_coords, c=colors[k], marker='.', transform=datacrs, alpha=0.7, s=6)
        except IndexError:
            pass

    return ax

def subset_data_to_plot(ds, ARDT, ssn, AR, region=None, basin=None, HUC8=None):
    '''
    Subset the trajectories to a given ARDT, season, 
    and whether or not you want the trajectories to be associated with an AR at the coast
    
    Parameters
    ----------
    ARDT : str
        the ARDT you want to subset by - tARget:'tARgetv4', ar:'Rutz AR', or arscale:'AR scale'
    
    ssn : str
        the season you want to subset by - 'NDJFMA', 'MJJASO', 'DJF', 'MAM', 'JJA', 'SON'

    ar : str
        whether or not you want the trajectories to be associated with an AR at the coast
        'AR' or 'non AR'

    region : str
        the region you want to subset to

    basin : str
        the basin you want to subset to

    HUC8 : str
        the HUC8 you want to subset to
        
    Returns
    -------
    data : xarray dataset object
        dataset object subset to the specified parameters
    '''

    ## subset to start_month and end_month based on ssn
    start_mon, end_mon = get_startmon_and_endmon(ssn)
    ds = select_months_ds(ds, start_mon, end_mon, 'start_date')

    ## subset to region, basin, or HUC8
    if basin is not None:
        ds = ds.where(ds.basin==basin, drop=True)
    if region is not None:
        ds = ds.where(ds.region==region, drop=True)
    if HUC8 is not None:
        ds = ds.where(ds.HUC8==str(HUC8), drop=True).squeeze()

    if AR == True:
        ## subset to ARDT
        ds = ds.where(ds[ARDT] > 0, drop=True)
    elif AR == False:
        ds = ds.where(ds[ARDT].isnull(), drop=True)
    
    return ds

def subset_gdf_to_plot(gdf, ARDT, ssn, AR, region=None, basin=None, HUC8=None):
    '''
    Subset the trajectories to a given ARDT, season, 
    and whether or not you want the trajectories to be associated with an AR at the coast
    
    Parameters
    ----------
    gdf : 
        a geopandas dataframe of all of the trajectories ran
    
    ARDT : str
        the ARDT you want to subset by - tARget:'tARgetv4', ar:'Rutz AR', or arscale:'AR scale'
    
    ssn : str
        the season you want to subset by - 'NDJFMA', 'MJJASO', 'DJF', 'MAM', 'JJA', 'SON'

    ar : str
        whether or not you want the trajectories to be associated with an AR at the coast
        'AR' or 'non AR'

    region : str
        the region you want to subset to

    basin : str
        the basin you want to subset to

    HUC8 : str
        the HUC8 you want to subset to
        
    Returns
    -------
    data : xarray dataset object
        dataset object subset to the specified parameters
    '''
    
    ## subset to region, basin, or HUC8
    if basin is not None:
        idx = (gdf['basin'] == basin)
        gdf = gdf.loc[idx]
    if region is not None:
        idx = (gdf['region'] == region)
        gdf = gdf.loc[idx]
    if HUC8 is not None:
        idx = (gdf['HUC8'] == str(HUC8))
        gdf = gdf.loc[idx]
    
    if ssn is not None:    
        ## subset to start_month and end_month based on ssn
        start_mon, end_mon = get_startmon_and_endmon(ssn)
        gdf = select_months_df(gdf, start_mon, end_mon)

    if AR == True:
        ## subset to ARDT
        idx = (gdf[ARDT] > 0)
    elif AR == False:
        idx = (gdf[ARDT].isnull())

    gdf = gdf.loc[idx]

    # Subtract 1 from 'ar_scale' to fix error
    gdf['ar_scale'] = gdf['ar_scale'] - 1
    # Replace NaN values with 0
    gdf['ar_scale'] = gdf['ar_scale'].fillna(0)
    
    return gdf

def plot_trajectory_heatmaps(ds, gdf, ddict):

    ssn = ddict['SSN']
    ARDT = ddict['ARDT']
    ar = ddict['AR']
    region_lst = ddict['region_lst']

    left_lbl = ['Upper Yampa', 'Roaring Fork', 'Upper Gunnison', 'Upper San Juan']
    left_lbl = ['Northwestern', 'Southwestern', 'Rio Grande', 'Eastern']

    ## load watershed shapefile and predefined regions shapefile
    polys = load_HUC8()
    plot_poly = load_region_shp(polys)

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
    fname = path_to_figs + 'trajectory_heatmaps_{0}_{1}_AR-{2}'.format(ssn, ARDT, ar)
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

        subset = subset_data_to_plot(ds, ARDT, ssn, ar, region=region_lst[i], basin=None, HUC8=None)
        ax = plot_heatmaps(ax, cbax, subset, ARDT, AR=ar, normalize=None)
        
        ## add in subbasin shapefile
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
        subset_gdf = subset_gdf_to_plot(gdf, ARDT, ssn, ar, region=region_lst[i], basin=None, HUC8=None)
        subset_gdf = subset_gdf.reset_index(drop=True)
        ax = plot_spaghetti_maps(ax, subset_gdf, datacrs)
                
        ## add in shapefile
        plot_poly.crs = 'epsg:3857'
        plot_poly.plot(ax=ax, edgecolor='k', color='None', zorder=99, lw=0.75)
        ## add in a, b, c label
        ax.text(0.03, 0.96, titlestring[1][i], ha='left', va='top', transform=ax.transAxes, fontsize=11., backgroundcolor='white', zorder=101)
    
    ## Add color bar
    cbax = plt.subplot(gs[-1,-1]) # colorbar axis
    plot_arscale_cbar(cbax, orientation='horizontal')
    
    fig.savefig('%s.%s' %(fname, fmt), bbox_inches='tight', dpi=fig.dpi, transparent=True)
    fig.clf()