"""
Filename:    load_shapefiles.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Functions for loading the various shapefiles with the different HUC boundaries
"""

# Standard Python modules
import os, sys
import yaml
import pandas as pd
import xarray as xr
import geopandas as gpd
import global_vars

# Global variable
path_to_data = global_vars.path_to_data
path_to_repo = global_vars.path_to_repo

def load_HUC8():
    ## load PRISM watershed precip dataset
    fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO_sp.nc'
    PRISM = xr.open_dataset(fname)
    precthres_lst = []
    for i, HUC8 in enumerate(PRISM.HUC8.values):
        ds = PRISM.sel(HUC8=HUC8)
            
        ## select dates where SWE is > 0.1 inches/2.54 mm
        tmp = ds.where(ds.prec > 2.54, drop=True) ## keep all precipitating events
        ## calculate the 90th percentile of precipitation
        PRISM_prec = tmp['prec'].to_dataframe()
        ## calculate the 90th percentile of precipitation
        prec_thres = PRISM_prec['prec'].describe(percentiles=[.90]).loc['90%'] # 90th percentile precipitation threshold
        precthres_lst.append(prec_thres)
    
    ## put into a dataframe to merge with gpd
    d = {'prec_thres': precthres_lst, 'HUC8': PRISM.HUC8.values}
    prec_df = pd.DataFrame(d)


    # import configuration file for region list of HUC8s
    yaml_doc = path_to_repo+'data/HUC8_regions.yml'
    config = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)
    
    region_lst = ['northwestern_CO', 'southwestern_CO', 'rio_grande', 'eastern_CO']
    df_lst = []
    for i, region in enumerate(region_lst):
        HUC8_lst = config[region]
        d = {'HUC8': HUC8_lst, 'region_name': region}
        df = pd.DataFrame(d)
        df_lst.append(df)
    region_df = pd.concat(df_lst)

    ## load watershed shapefile
    ## use geopandas to import the shapefile
    fp = path_to_data + 'downloads/CO_HUC8/wbdhu8.shp'
    polys = gpd.read_file(fp, crs="epsg:3857") # have to manually set the projection
    
    ## add the specified region name and prec_thres as a column
    polys = polys.merge(region_df, on='HUC8')
    polys = polys.merge(prec_df, on='HUC8')

    return polys

def load_region_shp(polys):
    polys_subset = polys[['region_name', 'geometry']]    ## create a shapefile of the 4 regions using dissolve
    regions = polys_subset.dissolve(by='region_name')

    return regions

def load_continental_divide():
    ## load continental divide shapefile
    fp = path_to_data + 'downloads/continental_divide_shapefile/pw312bv3382.shp'
    divide = gpd.read_file(fp, crs="ESPG:4326")

    return divide

def load_HUC2():
    ## load HU2 shapefile for regions 10, 11, 13, 14
    region_lst = [10, 11, 13, 14]
    WBD_lst = []
    for i, region in enumerate(region_lst):
        fp = path_to_data + 'downloads/WBD_HU2_{0}/Shape/WBDHU2.shp'.format(region)
        WBD = gpd.read_file(fp, crs="ESPG:3857")
        WBD_lst.append(WBD)

    return WBD_lst