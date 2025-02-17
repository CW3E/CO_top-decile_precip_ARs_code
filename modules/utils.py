"""
Filename:    utils.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: utility functions
"""

import math
import glob
import re
import numpy as np

def roundPartial(value, resolution):
    return np.round(value / resolution) * resolution

def round_latlon_degree(df, res):

    df['lon-round'] = roundPartial(df['longitude'], res)
    df['lat-round'] = roundPartial(df['latitude'], res)
    
    return df

def haversine(lat1, lon1, lat2, lon2):
    '''
    # Example usage:
    lat1 = 52.5200
    lon1 = 13.4050
    lat2 = 48.8566
    lon2 = 2.3522

    distance = haversine(lat1, lon1, lat2, lon2)
    print(f"The distance between the two points is {distance} kilometers.")
    '''
    # Radius of the Earth in kilometers
    earth_radius = 6371  # You can also use 3958.8 for miles

    # Convert latitude and longitude from degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = earth_radius * c

    return distance

def list_of_processed_files(year):
    '''
    Returns a list of ERA5 files that have been downloaded
    '''
    processed_dates = []
    list_of_files = glob.glob('/expanse/nfs/cw3e/cwp140/downloads/ERA5/ERA5/*/*')
    for fname in list_of_files:

        # pull the initialization date from the filename
        regex = re.compile(r'\d+')
        date_string = regex.findall(fname)
        date_string = date_string[-1]
        processed_dates.append(date_string)

    return processed_dates

def find_closest_MERRA2_lon(lon):
    ## MERRA2 longitudes are every 0.625 degree
    merra2_lons = np.arange(-180.0, 180., 0.625)
    
    myList = merra2_lons
    myNumber = lon
    final = min(myList, key=lambda x:abs(x-myNumber))
    
    return final

def find_closest_MERRA2_lon_df(row):
    ## MERRA2 longitudes are every 0.625 degree
    merra2_lons = np.arange(-180.0, 180., 0.625)
    
    myList = merra2_lons
    myNumber = row['longitude']
    final = min(myList, key=lambda x:abs(x-myNumber))
    
    return final

def select_closest_value(myList, myNumber):
    final = min(myList, key=lambda x:abs(x-myNumber))
    idx  = min(range(len(myList)), key=lambda i: abs(myList[i]-myNumber))
    
    return (idx, final)

def MERRA2_range(row):
    ## MERRA2 longitudes are every 0.625 degree
    merra2_lons = np.arange(-180.0, 180., 0.625)
    merra2_lats = np.arange(-90.0, 90., 0.5)
    
    lat = row['latitude']
    lon = row['longitude']
    
    idx, final = select_closest_value(merra2_lons, lon)
    idx2, final2 = select_closest_value(merra2_lats, lat)
    ## get surrounding grid cells
    lon_lst = merra2_lons[idx-2:idx+3] 
    lat_lst = merra2_lats[idx2-2:idx2+3]
    
    return lat_lst, lon_lst

def select_months_ds(ds, mon_s, mon_e, time_varname):    
    # Select months from xarray dataset
    if mon_s > mon_e:
        idx = (ds[time_varname].dt.month >= mon_s) | (ds[time_varname].dt.month <= mon_e)
    else:
        idx = (ds[time_varname].dt.month >= mon_s) & (ds[time_varname].dt.month <= mon_e)
    
    if time_varname == 'time':
        ds = ds.sel(time=idx)
    elif time_varname == 'start_date':
        ds = ds.sel(start_date=idx)
    elif time_varname == 'date':
        ds = ds.sel(date=idx)
    return ds

def select_months_df(df, mon_s, mon_e):
    # Select months from pandas dataframe
    if mon_s > mon_e:
        idx = (df.index.month >= mon_s) | (df.index.month <= mon_e)
    else:
        idx = (df.index.month >= mon_s) & (df.index.month <= mon_e)

    df = df.loc[idx]
    
    return df 
    
def generate_ptlst_from_start_end(x1, y1, x2, y2, pairs=True):
    deltay = (y2-y1)
    deltax = (x2-x1)
    rise = deltay
    run = deltax

    if rise == 0: ## if the line is horizontal straight
        ## ensure we are getting a point every 0.25 degrees
        lon_pairs = np.arange(x1, x2+0.25, 0.25)
        lat_pairs = np.repeat(y1, len(lon_pairs))
    else:
        small = min([np.abs(rise), np.abs(run)]) # get the smaller of the two numbers
        divisor = small / 0.25 ## get our divisor to ensure we are getting a point every 0.25 degree in at least one direction
        lat_pairs = np.arange(y1, y2+(rise/divisor), rise/divisor)
        lon_pairs = np.arange(x1, x2+(run/divisor), run/divisor)

    if pairs==True:
        pair_lst = []
        for i, pair in enumerate(zip(lat_pairs, lon_pairs)):
            pair_lst.append(pair)
        coord_pairs = pair_lst
        
    else:
        coord_pairs = lat_pairs, lon_pairs
    
    return coord_pairs