## Download Data

1. Download the Global Atmospheric Rivers Database, Version 3

Navigate to https://dataverse.ucla.edu/dataverse/ar and select **[Data] Global Atmospheric Rivers Database, Version 3** to download. You will need to provide information regarding the use of this dataset.

1. Download the Rutz et al. (2014) AR detection data based on MERRA2

Navigate to https://cw3e-datashare.ucsd.edu/Rutz_AR_Catalog/ and download the files titled **Rutz_ARCatalog_MERRA2_*.nc** to download.

1. Download the PRISM precipitation data

Navigate to [https://prism.oregonstate.edu](https://prism.oregonstate.edu/), then select ‘Recent Years’, then select the radio buttons for precipitation, then daily data, then select the year and click **Download All Data for Year (.bil).** Repeat this for all other years.

1. Download the Colorado Watershed Boundary Dataset (WBD) Hydrologic Unit 8 data

Navigate to https://geo.colorado.edu/catalog/47540-5c8ff914a84a6c000a68f3a8 and then click on **Original Shapefile** to download.

1. Navigate and login to Earth Explorer https://earthexplorer.usgs.gov/. Select the "Data Sets" tab and type in "GMTED2010" in the "Data Set Search" box. From the drop-down box, select GMTED2010. Next, select the "Additional Criteria" tab and click the + icon by Entity ID. Type "GMTED2010N50W150" into the box. Select the Results >> button and wait for the results to load. The correct tile should show up in the results and can be confirmed by clicking the footprint icon. To download, select the icon with the green down arrow and then select the Download button under the "7.5 ARC SEC (711.85 MiB)" download option.
2. Download ERA5 pressure level data using cds-api.

In the `downloads/ERA5` directory, run `create_job_configs.py` to create a series of config_X.yaml and calls_X.txt files to run downloads in parallel. Then submit the jobs using sbatch and the `run_download_ERA5.slurm` script. This will download u, v, and w wind, and specific humidity on pressure levels

1. Download ERA5 surface level data using cds-api.

In the `downloads/ERA_sfc` directory, run `create_job_configs.py` to create a series of config_X.yaml and calls_X.txt files to run downloads in parallel. Then submit the jobs using sbatch and the `run_download_ERA5.slurm` script. This will download meridional and zonal IVT, geopotential at 700 hPa and surface pressure.

---

Here is what your data/downloads directory should look like after all of the above are downloaded.

```
../data/downloads/
├── globalARcatalog_ERA5_1940-2023_v4.0.nc
├── Rutz_AR_Catalog
│   └──  Rutz_ARCatalog_MERRA2_*.nc
├── PRISM
│   ├── *.bil
├── CO_HUC8
│   ├── wbdhu8.cst
│   ├── wbdhu8.dbf
│   ├── wbdhu8.prj
│   ├── wbdhu8.shp
│   └── wbdhu8.shx
├──ETOPO1_Bed_c_gmt4.grd
├── ERA5_prs
│   ├── 2000
│       └── era5_nhemi_025dg_1hr_uvwq_2000*.nc
│   ├── ...
│   └── 2024
└── ERA5_sfc
    ├── ivt
        └── 20*_IVT.nc
    ├── gph
        └── era5_namerica_025dg_daily_700z_*.nc
    └── surface_pressure
        └── 20*_sp.nc
```