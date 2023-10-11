"""
Filename:    utils.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: utility functions
"""

def roundPartial(value, resolution):
    return round(value / resolution) * resolution

def round_latlon_degree(df, res):

    df['lon-round'] = roundPartial(df['longitude'], res)
    df['lat-round'] = roundPartial(df['latitude'], res)
    
    return df