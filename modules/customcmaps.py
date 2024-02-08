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
         
          "ivt": [[255, 255, 3], # 100-150
                  [255, 229, 3], # 150-200
                  [255, 201, 2], # 200-250
                  [255, 175, 2], # 250-300
                  [255, 131, 1], # 300-400
                  [255, 79, 1], # 400-500
                  [255, 24, 1], # 500-600
                  [235, 1, 7], # 600-700
                  [185, 0, 55], # 700-800
                  [134, 0, 99], # 700-800
          ]
         } 

bounds = {"arscale": [1, 2, 3, 4, 5],
          "ivt": [0, 100, 150, 200, 250, 300, 400, 500, 600, 700, 800]}


def cmap(name):
    data = np.array(colors[name])
    data = data / np.max(data)
    cmap = ListedColormap(data, name=name)
    bnds = bounds[name]
    norm = mcolors.BoundaryNorm(bnds, cmap.N)
    return cmap, norm, bnds