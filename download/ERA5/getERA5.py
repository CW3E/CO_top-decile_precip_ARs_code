"""
Filename:    getERA5_batch.py
Author:      Tessa Montini, tmontini@ucsb.edu & Deanna Nash, dlnash@ucsb.edu
Description: Download ERA5 data based on input configuration dictionary. Use in conjunction with ERA5_config for input variables. 

"""
import sys
import cdsapi
import yaml


### Imports config name from argument when submit
yaml_doc = sys.argv[1]
config_name = sys.argv[2]

# import configuration file for season dictionary choice
config = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)
ddict = config[config_name]

outpath = "/expanse/lustre/scratch/dnash/temp_project/downloaded/ERA5/{0}/".format(ddict['year'])
# Download hourly data files for each day
outfile = outpath + "era5_nhemi_025dg_1hr_uvwq_{0}{1}{2}.nc".format(ddict['year'], ddict['month'], ddict['day'])
c = cdsapi.Client()
c.retrieve(ddict['data_type'], 
           {'product_type'  : 'reanalysis',
            'variable'      : ddict['var_name'],
            'pressure_level': ddict['levels'],
            'year'          : ddict['year'],
            'month'         : ddict['month'],
            'day'           : ddict['day'],
            'time'          : ddict['time'],
            'area'          : ddict['area'],
            'grid'          : ddict['grid'],
            'format'        : 'netcdf'}, 
           outfile)
print("Download complete: {filename} \n".format(filename=outfile))