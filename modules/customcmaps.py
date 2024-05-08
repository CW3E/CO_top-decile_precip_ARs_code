"""
Filename:    customcmaps.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Functions for custom cmaps adapted from from https://github.com/samwisehawkins/nclcmaps
"""

import numpy as np
import matplotlib.colors as mcolors
from matplotlib.colors import ListedColormap

__all__ = ['cw3ecmaps']

colors = {"arscale": [[10, 193, 255], # blue
                            [4, 255, 3], # green
                            [255, 255, 3], # yellow
                            [255, 166, 2], # orange
                            [255, 1, 0]], # red

          "sens": [[255,255,204], # yellow
                            [161,218,180], # green
                            [65,182,196], # light blue
                            [34,94,168] # blue
                         ], 
          
          "ivt": [[12, 255, 255], # 100-150
                  [16, 185, 6], # 150-200
                  [140, 220, 2], # 200-250
                  [255, 255, 3], # 250-300
                  [255, 229, 3], # 300-400
                  [255, 201, 2], # 400-500
                  [255, 175, 2], # 500-600
                  [255, 131, 1], # 600-700
                  [255, 79, 1],  # 700-800
                  [255, 24, 1],  # 800-1000
                  [235, 1, 7],   # 1000-1200
                  [185, 0, 55],  # 1200-1400
                  [234, 234, 234], # 1400-1600
                  [86, 0, 137]   # 1600+
          ],
          
          "mclimate": [[0.969, 0.988, 0.725], # 0-5
                            [0.851, 0.941, 0.639], #5-10
                            [0.678, 0.867, 0.557], #10-15
                            [0.471, 0.776, 0.475], #15-20
                            [0.255, 0.671, 0.365], #20-25
                            [0.137, 0.518, 0.263], #25-30
                            [0.000, 0.408, 0.216], #30-35
                            [0.000, 0.271, 0.161]], #35-40

          "pressure": [[237,248,251], # 600-700
                            [179,205,227], # 700-800
                            [140,150,198], # 800-900
                            [136,65,157], # 900-1000
                      ], 
          
          "ar_freq": [[237,248,251], #0-1
                      [178,226,226], # 1-2
                      [102,194,164], #2-3
                      [44,162,95], #3-4
                      [0,109,44]] #4-5
         } 

bounds = {"arscale": [1, 2, 3, 4, 5],
          "sens": [1, 2, 3, 4],
          "ivt": [100, 150, 200, 250, 300, 400, 500, 600, 700, 800, 1000, 1200, 1400, 1600],
          "mclimate": [0, 5, 10, 15, 20, 25, 30, 35, 40],
          "pressure": [600., 700., 800., 900., 1000.],
          "ar_freq": [0, 1, 2, 3, 4, 5]}


def cmap(name):
    data = np.array(colors[name])
    data = data / np.max(data)
    cmap = ListedColormap(data, name=name)
    bnds = bounds[name]
    norm = mcolors.BoundaryNorm(bnds, cmap.N)
    return cmap, norm, bnds