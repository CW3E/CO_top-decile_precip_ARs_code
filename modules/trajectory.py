"""
Filename:    trajectory.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: class for calculating backwards trajectories with u, v, and w data
"""

import math
import xarray as xr
import pandas as pd
import numpy as np

class calculate_backward_trajectory:
    '''
    Returns an array 
    Parameters
    ----------
    ds : xarray
        xarray with list of dates, lats, and lons for extreme precip days
    idx : int
        integer of the index that is currently being processed
    start_lev: float
        starting level (in hPa) for trajectory
        
    Returns
    -------
    traj : pandas dataframe
        pandas dataframe of the backward trajectory for 72 hours
    
    '''
    
    def __init__(self, ds, idx, start_lev=700.):
    
        ## get start_date, start_lat, and start_lon
        ## start in the middle of the day
        self.start_date = ds.isel(date=idx).date.values + np.timedelta64(12,'h')
        self.start_lat = ds.isel(date=idx).lat.values
        self.start_lon = ds.isel(date=idx).lon.values
        self.start_lev = start_lev
        print(self.start_date, self.start_lat, self.start_lon)
        
        self.varlst = ['time', 'latitude', 'longitude', 'level', 'q', 'u', 'v', 'w']     
        self.calc_vars = ['drying_ratio', 'dq']
        
        self.date_lst = pd.date_range(end=self.start_date, periods=72, freq='H')
    
    def read_data(self):    
        # read ERA5 data
        fpath = '/data/projects/Comet/cwp140/downloads/'
        fname = fpath + 'ERA5/era5_uvwq_prs_20000214_20000218_2000.nc'
        self.ds1 = xr.open_dataset(fname)

        ## read MERRA2 data - not sure if we need this anymore
        # fname = '/data/downloaded/Reanalysis/MERRA2/M2I3NPASM.5.12.4_raw/1980/MERRA2_100.inst3_3d_asm_Np.19801231.nc4'
        # calculate vertical velocity (w) if MERRA2
        # w = mpcalc.vertical_velocity(ds.OMEGA, ds.lev, ds.T, mixing_ratio=0)

    def create_empty_array(self):   
   
        # initial conditions
        t0 = self.ds1.interp(latitude=self.start_lat, longitude=self.start_lon, level=self.start_lev, time=self.start_date)
        
        ## append initial conditions to empty DataFrame
        t0_vals = []
        for i in self.varlst:
            if i == 'time':
                t0_vals.append(t0[i].values)
            else:
                t0_vals.append(float(t0[i].values))
        df = pd.DataFrame(columns = self.varlst, index=np.arange(0, 72, 1))
        df.iloc[0] = t0_vals
        self.df = df
        
    def find_distance_travelled(self, t0):
    
        ## not sure what this is
        nRes = 1.
        nHour = 24.
        nXDay = 4
        timeRatio = ((nHour/nXDay)/nRes)

        # t1 is where the parcel was 1 hour ago if it had been travelling at the speed of t0
        del_x = ((0-t0.u)*3600.)/1000. # convert to km
        del_y = ((0-t0.v)*3600.)/1000. # convert to km 
        del_z = ((0-t0.w)*3600.)/100. # convert to hPa
    
        return del_x, del_y, del_z
    
    def km_to_decimal_degrees(self, distx, disty, latitude):
        '''
        # Example usage:
        disty = 100 ## distance along latitude in km
        distx = 100 ## distance along longitude in km
        latitude = 52.5200 ## latitude to calculate along

        xdeg, ydeg = km_to_decimal_degrees(distx, disty, latitude)
        '''
        ## convert distance north-south to decimal degrees
        ## 111.2 km per degree
        ydeg = disty/111.2 # convert km to degree
        
        ## convert distance east-west to decimal degrees
        # Radius of the Earth in kilometers
        earth_radius = 6371

        # Convert latitude from degrees to radians
        lat_radians = math.radians(latitude)

        # Calculate decimal degrees
        xdeg = distx / (earth_radius * (math.pi / 180))

        return xdeg, ydeg

    
    def get_values_at_current_timestep(self, idx):
        '''
        Given u, v, and w at current lat/lon/lev, 
        what is u/v/w at previous time step
        
        idx: int
            index of current time step
        '''
        # get values of previous time step
        t0 = self.df.iloc[idx-1]
        
        ## find distance travelled between this hour and previous hour
        del_x, del_y, del_z = self.find_distance_travelled(t0)

        ## convert km to degrees
        del_x, del_y = self.km_to_decimal_degrees(del_x, del_y, t0.latitude)

        ## now the new location is the old location plus the distances
        new_lat = t0.latitude + del_y
        # if new_lat <= 0.:
        #     break
        # elif new_lat >= 90.:
        #     break
        new_lon = t0.longitude + del_x
        # if new_lon < -180.:
        #     new_lon = new_lon + 360.
        new_lev = t0.level + del_z
        # if new_lev < 1.:
        #     break
        # elif new_lev > 1000.:
        #     break
        new_date = t0.time - np.timedelta64(1,'h')

        ## interpolate to new point
        t1 = self.ds1.interp(latitude=new_lat, longitude=new_lon, level=new_lev, time=new_date)
        ## put new values in dataframe
        t1_vals = []
        for i in self.varlst:
            if i == 'time':
                t1_vals.append(t1[i].values)
            else:
                t1_vals.append(float(t1[i].values))
        self.df.iloc[idx] = t1_vals
        
    def compute_trajectory(self):
        
        ## read data TODO flexible for date input
        self.read_data()
        
        ## build dataframe with initial conditions
        self.create_empty_array()
        
        ## loop through the remaining 72 hours
        for i, idx in enumerate(np.arange(1, 72, 1)):
            self.get_values_at_current_timestep(idx)
        
        ## convert specific humidity to g kg-1
        self.df['q'] = self.df['q']* 1000
        ## calculate change in q between this step and previous step
        self.df['dq'] = self.df['q'].diff()
        ## using del_q, calculate "drying ratio"
        ## how much water vapor has been lost/gained in between time steps
        self.df['drying_ratio'] = (self.df['dq']/self.df['q'])*100.# convert to %    
        
        return self.df
            
        