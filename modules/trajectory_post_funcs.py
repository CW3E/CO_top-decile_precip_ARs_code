"""
Filename:    trajectory_post_funcs.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: post-processing functions for trajectories
"""

import math
import xarray as xr
import pandas as pd
import numpy as np
import dask
import geopandas as gpd
import shapely.geometry
from utils import  find_closest_MERRA2_lon_df, find_closest_MERRA2_lon, MERRA2_range, roundPartial


dask.config.set(**{'array.slicing.split_large_chunks': True})

def calculate_heatmaps_from_trajectories(HUC8_ID):
    fname = '/home/dnash/comet_data/preprocessed/ERA5_trajectories/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
    ERA5 = xr.open_dataset(fname)
    
    ## open as geopandas dataframe
    df = ERA5.to_dataframe()
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")

    ### Code is based on https://james-brennan.github.io/posts/fast_gridding_geopandas/

    ### BUILD A GRID 
    # total area for the grid
    xmin, ymin, xmax, ymax= gdf.total_bounds
    xmin, ymin, xmax, ymax= [-175., 20., -85.,  63.]
    # how many cells across and down
    n_cells=100
    cell_size = (xmax-xmin)/n_cells
    # projection of the grid
    crs = "EPSG:4326"
    # create the cells in a loop
    grid_cells = []
    for x0 in np.arange(xmin, xmax+cell_size, cell_size ):
        for y0 in np.arange(ymin, ymax+cell_size, cell_size):
            # bounds
            x1 = x0-cell_size
            y1 = y0+cell_size
            grid_cells.append( shapely.geometry.box(x0, y0, x1, y1)  )
    cell = gpd.GeoDataFrame(grid_cells, columns=['geometry'], 
                                     crs=crs)

    merged = gpd.sjoin(gdf, cell, how='left', predicate='within')

    # make a simple count variable that we can sum
    merged['n_traj']=1
    # Compute stats per grid cell -- aggregate fires to grid cells with dissolve
    dissolve = merged.dissolve(by="index_right", aggfunc="count")
    # put this into cell
    cell.loc[dissolve.index, 'n_traj'] = dissolve.n_traj.values
    print(cell['n_traj'].max())
    
    return cell