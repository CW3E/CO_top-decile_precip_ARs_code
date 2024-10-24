#!/bin/bash
######################################################################
# Filename:    run_compute_composites.sh
# Author:      Deanna Nash dnash@ucsd.edu
# Description: Script to run the preprocessing steps for composites
#
######################################################################


# Input parameters
domain="baja"

## step 1: run getlst_bbox.py
## this script will create .csv files with the dates, lats, and lons of the trajectories that cross the domain bbox and line

## step 2: 