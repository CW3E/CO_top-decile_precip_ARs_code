import yaml
import numpy
import xarray as xr

path_to_data = '/cw3e/mead/projects/cwp162/data/'
path_to_data  = '../data/'

## load PRISM watershed precip dataset
fname = path_to_data + 'preprocessed/PRISM/PRISM_HUC8_CO_sp.nc'
PRISM = xr.open_dataset(fname)
arr = PRISM.HUC8.values
# Convert NumPy strings to plain Python strings
arr = arr.astype(str)

# Build categories
eastern_CO = [str(x) for x in arr if x.startswith(("10", "11"))]
rio_grande = [str(x) for x in arr if x.startswith("13")]

northwestern_CO = [
    str(x) for x in arr 
    if x.startswith(("1401", "1404", "1405", "1406")) or x == "14030001"
]

southwestern_CO = [
    str(x) for x in arr
    if (
        x.startswith(("1408", "1402")) 
        or (x.startswith("1403") and x != "14030001")
    )
]

# Combine into config dict
config = {
    "eastern_CO": eastern_CO,
    "rio_grande": rio_grande,
    "northwestern_CO": northwestern_CO,
    "southwestern_CO": southwestern_CO,
}

# Write to YAML
with open(path_to_data+"HUC8_regions2.yml", "w") as f:
    yaml.safe_dump(config, f, sort_keys=False, default_flow_style=False)