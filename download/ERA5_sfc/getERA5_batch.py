"""
Filename:    getERA5_batch.py
Author:      Tessa Montini, tmontini@ucsb.edu & Deanna Nash, dnash@ucs.edu
Description: Download ERA5 data based on input configuration dictionary. Use in conjunction with ERA5_config for input variables. 

"""
import sys
import cdsapi
import yaml


### Imports config name from argument when submit
config_name = sys.argv[1]
print(config_name)


# import configuration file for season dictionary choice
yaml_doc = 'ERA5_config.yml'
config = yaml.load(open(yaml_doc), Loader=yaml.SafeLoader)
ddict = config[config_name]


# Loop for downloading files
outfile = ddict['datadir'] + ddict['outfile']
c = cdsapi.Client()
c.retrieve(ddict['data_type'], 
           {'product_type'  : 'reanalysis',
            'variable'      : ddict['var_name'],
            'pressure_level': ddict['levels'],
            'year'          : ddict['year'],
            'month'         : ddict['month'],
            'day'           : ddict['day'],
            'time'          : ddict['time'],
            'grid'          : ddict['grid'],
            'format'        : 'netcdf'}, 
           outfile)
print("Download complete: {filename} \n".format(filename=outfile))