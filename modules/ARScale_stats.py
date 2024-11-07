"""
Filename:    ARScale_stats.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: class for calculating the number of trajectories associated with AR Scale values broken down by season and region.
"""
import os
import math
import xarray as xr
import pandas as pd
import numpy as np
from composite_funcs import get_startmon_and_endmon
from utils import select_months_ds

class build_ar_stat_dataframe:
    '''
    Returns a pandas dataframe
    Parameters
    ----------
    ds : xarray
        xarray of all the final trajectory results
    PRISM : xarray
        xarray with PRISM data
    basin_name : str
        string of basin name - either Colorado, Rio Grande, Arkansas, or Upper Platte
    ssn : str
        season for analysis

    Returns
    -------
    df : pandas dataframe
        pandas dataframe with stats on number of trajectories associated with AR scale

    '''

    def __init__(self, ds, PRISM, basin_name, ssn):
        
        self.basin_name = basin_name
        self.ssn = ssn
        start_mon, end_mon = get_startmon_and_endmon(ssn)
        self.PRISM = select_months_ds(PRISM, start_mon, end_mon, 'date')
        self.ds = select_months_ds(ds, start_mon, end_mon, 'start_date')

    def get_nbasins(self):
        '''
        Returns the number of subbasins within a region and the list of HUC8s within that region
        '''
        
        tmp = self.ds.where(self.ds.basin==self.basin_name, drop=True)
        nbasins = len(tmp.HUC8)
        subbasin_lst = tmp.HUC8.values
    
        return nbasins, subbasin_lst

    def get_total_ntrajs(self, subbasin_lst):
        '''
        Returns the number of trajectories ran for that subbasin and season
        '''
        
        ntraj_lst = []
        for i, subbasin in enumerate(subbasin_lst):
            tmp = self.PRISM.sel(HUC8=subbasin)
            ntrajs = len(tmp.where(tmp.extreme==1, drop=True).date.values)
            ntraj_lst.append(ntrajs)
    
        return sum(ntraj_lst)

    def get_nevents_AR_scale(self):
        tmp = self.ds.where(self.ds.basin==self.basin_name, drop=True)
        nevents_AR = []
        ## Loop through AR scale values
        for k in range(2, 7):
            # print('Counting nevents for AR scale {0}'.format(k-1))
            AR = tmp.where(tmp.ar_scale == k, drop=True)
            nevent_HUC8 = []
            for l, HUC8 in enumerate(AR.HUC8.values):
                tmp2 = AR.sel(HUC8=HUC8)
                tmp2 = tmp2.where(tmp2.ar_scale == k, drop=True)
                ## the number of AR scale events for that HUC8
                nevent_HUC8.append(len(tmp2.start_date))
            nevents = sum(nevent_HUC8)
            nevents_AR.append(nevents)
        return nevents_AR

    def create_dataframe(self):

        ## get numbers
        nbasins, subbasin_lst = self.get_nbasins()
        ntrajs = self.get_total_ntrajs(subbasin_lst)
        nevents_AR = self.get_nevents_AR_scale()
        
        ## make a dataframe to summarize results
        d = {'Basin Name': [self.basin_name], 'Season': self.ssn, 'nsubbasins': [nbasins], 'Total Trajectories': [ntrajs],
             'AR events': [sum(nevents_AR)], 'AR1': [nevents_AR[0]], 'AR2': [nevents_AR[1]], 'AR3': [nevents_AR[2]],
             'AR4': [nevents_AR[3]], 'AR5': [nevents_AR[4]]}
        
        df = pd.DataFrame(d)

        return df