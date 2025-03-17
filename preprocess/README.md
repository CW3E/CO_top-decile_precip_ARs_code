## Preprocess Data

These scripts can be run after downloading the data required as outlined in `../downloads/` .

1. Calculate areal mean precipitation for each HUC8 subbasin using PRISM and the HUC8 shapefile.
2. Get a list of top-decile precipitation dates for each HUC8 subbasin and add surface pressure information to data.
    - `preprocess_PRISM_watershed_data.ipynb`
    - `combine_surface_pressure_PRISM.ipynb`
3. Compute the AR Scale values using ERA5 IVT.
    - scripts in `preprocess/ERA5_AR_Scale/`
4. Create a subset of Rutz et al., (2014) ARDT 
    - `preprocess_MERRA2_Rutz_latlon.ipynb`
5. Create a subset of Guan and Waliser (2022) ARDT
    - `preprocess_tARgetv4_AR.ipynb`
6. Run sensitivity tests on trajectories. 
    - scripts in `preprocess/sensitivity_test_trajectories/`
7. Run all top-decile trajectories.
    - scripts in `preprocess/calculate_trajectories`
8. Concat trajectories for each HUC8 **(MUST WAIT UNTIL ALL TRAJECTORIES ARE COMPLETE TO RUN)**
    - `preprocess/calculate_trajectories/concat_trajectories.py`
9. Compute anomalies for ERA5 data
    - scripts in `preprocess/compute_climatology/`
10. Compute composites.
    - scripts in `preprocess/compute_composites/`