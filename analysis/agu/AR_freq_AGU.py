"""
Refactored AR Frequency Map Plot
--------------------------------
This version organizes the plotting into modular functions and centralized 
configuration, allowing easy swapping of variables, extents, styles, etc.
"""

# =============================
# Standard Python modules
# =============================
import os
import sys
import yaml
from pathlib import Path
import numpy as np
import pandas as pd
import xarray as xr
import geopandas as gpd
import textwrap

# =============================
# Plot styles/formatting
# =============================
import cmocean.cm as cmo
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colorbar import Colorbar
import matplotlib.patheffects as pe

# =============================
# Cartopy
# =============================
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.feature import ShapelyFeature

# =============================
# Custom local modules
# =============================
sys.path.append("../../modules")
import global_vars
from plotter import draw_basemap
import customcmaps as ccmap
from load_shapefiles import load_region_shp, load_HUC8

# ======================================================
# CONFIGURATION
# ======================================================

class PlotConfig:
    """Centralized plotting configuration."""
    # Geographic extents
    extent = [-127., -90., 20, 50]

    # Tick/grid spacing
    ticks_x = np.arange(-120., -80., 10)
    ticks_y = np.arange(20, 55., 5)

    # Annotation positions
    label_positions = {
        'Northwestern CO': (-112, 41.),
        'Southwestern CO': (-112., 33.5),
        'Rio Grande': (-103., 34),
        'Eastern CO': (-96.5, 39.),
    }

    # Variable to plot
    varname = "kidmap"

    # Color levels
    cmap_levels = np.arange(0, 13, 1)
    cmap = cmo.rain

    # Text and figure styling
    style = {"size": 9, "color": "black", "fontweight": "normal"}

    # Paths
    path_to_data = global_vars.path_to_data
    path_to_figs = "../../figs/"
    output_file = "AR_frequency.png"


# ======================================================
# DATA LOADING
# ======================================================

def load_data(config):
    """Load all necessary datasets: ARDT frequency + shapefiles."""
    polys = load_HUC8()
    regions = load_region_shp(polys)
    regions = regions.to_crs(epsg=4326)

    ds = xr.open_dataset(
        Path(config.path_to_data) / "preprocessed/ARDT_count/tARgetv4_count.nc"
    )

    return ds, regions


# ======================================================
# DATA EXTRACTION
# ======================================================

def select_variable(ds, varname):
    """Extract a variable from the dataset, with validation."""
    if varname not in ds:
        raise ValueError(f"Variable '{varname}' not found in dataset.")
    da = ds[varname]
    return da.values, da.lon.values, da.lat.values


# ======================================================
# PLOTTING UTILITIES
# ======================================================

def make_colormap(levels, cmap):
    """Wrapper for custom colormap builder."""
    return ccmap.cmap_segmented(cmap, levels)


def annotate_regions(ax, label_dict, transform, style):
    """Add region labels to a map."""
    for lbl, xy in label_dict.items():
        ax.annotate(
            textwrap.fill(lbl, 12),
            xy,
            xycoords=transform,
            textcoords="offset points",
            xytext=(0, 0),
            ha="center",
            zorder=200,
            path_effects=[pe.withStroke(linewidth=1.25, foreground="white")],
            **style,
        )


def add_colorbar(fig, mappable, gs_loc, label=""):
    """Add a vertical colorbar to the figure."""
    cbax = fig.add_subplot(gs_loc)
    cb = Colorbar(ax=cbax, mappable=mappable, orientation="vertical")
    cb.set_label(label, fontsize=11)
    cb.ax.tick_params(labelsize=11)
    return cb


# ======================================================
# MAIN PLOT PANEL
# ======================================================

def plot_main_panel(ax, lon, lat, data, config):
    """Draw the main AR frequency map panel."""
    # Draw base map
    ax = draw_basemap(
        ax,
        extent=config.extent,
        xticks=config.ticks_x,
        yticks=config.ticks_y,
        left_lats=True,
        right_lats=False,
        bottom_lons=True,
        mask_ocean=False,
        coastline=False,
    )

    # Create colormap
    cmap, norm, bounds = make_colormap(config.cmap_levels, config.cmap)

    # Filled contours
    cf = ax.contourf(
        lon,
        lat,
        data,
        transform=ccrs.PlateCarree(),
        levels=bounds,
        cmap=cmap,
        norm=norm,
        alpha=0.7,
        extend="max",
    )

    # States boundaries
    ax.add_feature(cfeature.STATES, edgecolor="0.4", linewidth=0.8, zorder=4)

    # Example point
    ax.plot(
        -104.9903,
        39.7392,
        "ro",
        markersize=3,
        transform=ccrs.PlateCarree(),
        zorder=201,
    )

    return cf


def plot_regions(ax, regions):
    """Add region outlines (properly reprojected)."""
    for idx, (i, poly) in enumerate(regions.iterrows()):
        feature = ShapelyFeature([poly.geometry], ccrs.PlateCarree(),
                                 edgecolor='k', facecolor='none', linewidth=1.)
        ax.add_feature(feature, zorder=200)


# ======================================================
# FIGURE CREATION
# ======================================================

def create_figure(config):
    fig = plt.figure(figsize=(7., 5.0), dpi=300)

    # Grid layout
    gs = GridSpec(
        1,
        2,
        height_ratios=[1],
        width_ratios=[1, 0.05],
        wspace=0.01,
        hspace=0.03,
    )

    ax_map = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
    cbar_slot = gs[0, 1]

    return fig, ax_map, cbar_slot


# ======================================================
# DRIVER FUNCTION
# ======================================================

def make_plot(config=PlotConfig()):
    """High-level function to generate and save the AR frequency map."""
    # Load data
    ds, regions = load_data(config)

    # Extract selected variable
    data, lon, lat = select_variable(ds, config.varname)

    # Create figure
    fig, ax, cbar_slot = create_figure(config)

    # Main map plot
    mappable = plot_main_panel(ax, lon, lat, data, config)

    # Region outlines
    plot_regions(ax, regions)

    # Region labels
    annotate_regions(
        ax,
        config.label_positions,
        transform=ccrs.PlateCarree()._as_mpl_transform(ax),
        style=config.style,
    )

    # Add colorbar
    add_colorbar(fig, mappable, cbar_slot, label="AR Frequency (%)")

    # Save
    outpath = Path(config.path_to_figs) / config.output_file
    fig.savefig(outpath, bbox_inches="tight", dpi=fig.dpi)

    plt.show()


# ======================================================
# RUN SCRIPT
# ======================================================

if __name__ == "__main__":
    make_plot()
