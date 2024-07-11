"""
Filename:    statistical_tests.py
Author:      Deanna Nash, dnash@ucsd.edu
Description: Functions for running different significance tests on tseries or ds objects
"""

# Import Python modules

import os, sys
import numpy as np
import pandas as pd
import xarray as xr
from scipy import stats
from scipy.stats import ttest_1samp, t, pearsonr, norm, linregress, ttest_ind_from_stats
import scipy.stats.distributions as dist

def ttest_1samp_new(a, popmean, dim, n):
    """
    This is a two-sided test for the null hypothesis that the expected value
    (mean) of a sample of independent observations `a` is equal to the given
    population mean, `popmean`
    
    Inspired here: https://github.com/scipy/scipy/blob/v0.19.0/scipy/stats/stats.py#L3769-L3846
    
    Parameters
    ----------
    a : xarray
        sample observation
    popmean : float or array_like
        expected value in null hypothesis, if array_like than it must have the
        same shape as `a` excluding the axis dimension
    dim : string
        dimension along which to compute test
    
    Returns
    -------
    mean : xarray
        averaged sample along which dimension t-test was computed
    maskt_idx : array, bool
        Boolean array of where the tvalue is greater than the critical value
    """
    df = n - 1
    a_mean = a.mean(dim)
    d = a_mean - popmean
    v = a.var(dim, ddof=1)
    denom = np.sqrt(v / float(n))

    tval = d /denom
    # calculate the critical value
    cv = stats.distributions.t.ppf(1.0 - 0.05, df)
    maskt_idx = (abs(tval) >= cv)
#     prob = stats.distributions.t.sf(xrf.fabs(tval), df) * 2
#     prob_xa = xr.DataArray(prob, coords=a_mean.coords)
    return a_mean, maskt_idx