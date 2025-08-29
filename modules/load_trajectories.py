"""
Filename:    load_trajectories.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Functions for loading the trajectories
"""
import sys, os
import yaml
import xarray as xr
import pandas as pd
import geopandas as gpd
from shapely import LineString
import numpy as np

# Global variable
path_to_data = "/cw3e/mead/projects/cwp162/data/"
yaml_doc = '/cw3e/mead/projects/cwp162/repos/CO_top-decile_precip_ARs_code/data/HUC8_regions.yml'

def load_trajectories_based_on_basin():
     
    ## load PRISM watershed precip dataset to get list of HUC8s
    fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO_sp.nc'
    PRISM = xr.open_dataset(fname)
    HUC8_lst = PRISM.HUC8.values ## get list of HUC8 IDs
    
    ## a quick function that assigns each watershed a basin value 
    ## based on the first 2 numbers of the HUC8 identifier
    
    basin_lst = []
    for i, HUC8_ID in enumerate(HUC8_lst):
        HUC2 = HUC8_ID[:2]
        if HUC2 == '14':
            basin = 'Upper Colorado'
        elif HUC2 == '13':
            basin = 'Rio Grande'
        elif HUC2 == '11':
            basin = 'Arkansas'
        elif HUC2 == '10':
            basin = 'Missouri'
       
        basin_lst.append(basin)
        
    ds_lst = []
    for i, HUC8_ID in enumerate(HUC8_lst):
        fname = path_to_data +'preprocessed/ERA5_trajectories/combined_extreme_AR/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
        ds = xr.open_dataset(fname)
        ds_lst.append(ds)
        
    ## concat ds_lst along HUC8 index
    ds = xr.concat(ds_lst, pd.Index(HUC8_lst, name="HUC8"))
    ## add the basin name as a coord
    ds = ds.assign_coords({'basin': ("HUC8", basin_lst)})
    
    return ds

def load_trajectories_based_on_region():
    # import configuration file for region list of HUC8s
    config = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)
    
    region_lst = ['northwestern_CO', 'southwestern_CO', 'rio_grande', 'eastern_CO']
    ds_final = []
    for i, region in enumerate(region_lst):
        HUC8_lst = config[region]
        ds_lst = []
        for i, HUC8_ID in enumerate(HUC8_lst):
            fname = path_to_data +'preprocessed/ERA5_trajectories/combined_extreme_AR/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
            ds = xr.open_dataset(fname)
            ds_lst.append(ds)
        
        ## concat ds_lst along HUC8 index
        ds = xr.concat(ds_lst, pd.Index(HUC8_lst, name="HUC8"))
        ## add the region name as a coord
        repeated_lst = [region] * len(HUC8_lst)
        ds = ds.assign_coords({'region': ("HUC8", repeated_lst)})
        ds_final.append(ds)
    
    ds = xr.concat(ds_final, dim='HUC8')

    return ds

def create_geopandas_from_trajectories(ds, region, HUC8):

    nevents = len(ds.start_date)
    gdf_lst = []
    ## LOOP THROUGH TRAJECTORIES
    for i in range(nevents):
        tmp = ds.isel(start_date=i)
        time_match = tmp.time_match.values
        lat_match = tmp.lat_match.values
        lon_match = tmp.lon_match.values
        start_date = tmp.start_date.values
        ar_scale = tmp.ar_scale.values
        rutz_ar = tmp.ar.values
        tARget = tmp.tARget.values
        prec = tmp.prec.values
        
        d = {'landfall_time': time_match, 'lat': lat_match, 'lon': lon_match, 
             'HUC8': HUC8, 'start_date': start_date, 'prec': prec,
             'ar_scale': ar_scale, 'ar': rutz_ar, 'tARget': tARget,
             'region': region}
        df = pd.DataFrame(d, index=[i])
        
        ## pull coord pairs from data
        lons=tmp.lon.values
        lats=tmp.lat.values
        coord_pairs = list(zip(lats, lons))
        # Filter out coordinates containing NaN values
        filtered_coords = [coord for coord in coord_pairs if not any(np.isnan(c) for c in coord)]

        # Create a LineString object
        line = LineString(filtered_coords)
        
        # Create a GeoDataFrame (optional, but common for working with GeoPandas)
        gdf = gpd.GeoDataFrame(df, geometry=[line], crs="EPSG:4326") # Set Coordinate Reference System
        gdf_lst.append(gdf)
    
    gdf_final = pd.concat(gdf_lst)

    return gdf_final


def load_gdf_trajectories_based_on_region():
    
    print('Reading PRISM data')
    fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO_sp.nc'
    PRISM = xr.open_dataset(fname)
    
    # import configuration file for region list of HUC8s
    config = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)
    
    region_lst = ['northwestern_CO', 'southwestern_CO', 'rio_grande', 'eastern_CO']
    gdf_lst = []
    for i, region in enumerate(region_lst):
        HUC8_lst = config[region]
        ds_lst = []
        for i, HUC8_ID in enumerate(HUC8_lst):

            PRISM_tmp = PRISM.sel(HUC8=HUC8_ID)
            PRISM_tmp = PRISM_tmp.sel(date=slice('2000-01-04', '2023-12-31')) ## have to remove Jan 1 and Jan 2 2000 dates bc we don't have Dec 30 and 31, 1999 data
            PRISM_tmp = PRISM_tmp.where(PRISM_tmp.extreme == 1, drop=True) ## keep top-decile precipitating events
    
            fname = path_to_data +'preprocessed/ERA5_trajectories/combined_extreme_AR/PRISM_HUC8_{0}.nc'.format(HUC8_ID)
            ds = xr.open_dataset(fname)
            ds = ds.assign({'prec': (['start_date'], PRISM_tmp.prec.values)})
            
            gdf = create_geopandas_from_trajectories(ds, region, HUC8_ID)
            gdf_lst.append(gdf)

    gdf_final = pd.concat(gdf_lst)

    return gdf_final
