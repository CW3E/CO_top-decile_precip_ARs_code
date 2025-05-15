import os, sys

sys.path.append('/home/dnash/repos/eaton_scripps_CO_ARs/modules')
from load_trajectories import load_gdf_trajectories_based_on_region

## load all trajectories categorized by region into a gdf
gdf = load_gdf_trajectories_based_on_region()

## Write to GeoJSON
geojson_path = "/home/dnash/repos/eaton_scripps_CO_ARs/out/trajectories.geojson"
gdf.to_file(geojson_path, driver="GeoJSON")