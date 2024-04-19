##################################################################################
# Description
##################################################################################
# This script is designed to generate heat plots in Matplotlib from MET grid_stat
# output files, preprocessed with the companion script proc_24hr_QPF.py.  This
# plotting scheme is designed to plot precipitation threshold level in the
# vertical axis and the number of lead hours to the valid time for verification
# from the forecast initialization in the horizontal axis. The global parameters
# for the script below control the initial times for the forecast initializations,
# as well as the valid date of the verification. Stats to compare can be reset 
# in the global parameters with heat map color bar changing scale dynamically.
#
##################################################################################
# License Statement:
##################################################################################
# This software is Copyright © 2024 The Regents of the University of California.
# All Rights Reserved. Permission to copy, modify, and distribute this software
# and its documentation for educational, research and non-profit purposes,
# without fee, and without a written agreement is hereby granted, provided that
# the above copyright notice, this paragraph and the following three paragraphs
# appear in all copies. Permission to make commercial use of this software may
# be obtained by contacting:
#
#     Office of Innovation and Commercialization
#     9500 Gilman Drive, Mail Code 0910
#     University of California
#     La Jolla, CA 92093-0910
#     innovation@ucsd.edu
#
# This software program and documentation are copyrighted by The Regents of the
# University of California. The software program and documentation are supplied
# "as is", without any accompanying services from The Regents. The Regents does
# not warrant that the operation of the program will be uninterrupted or
# error-free. The end-user understands that the program was developed for
# research purposes and is advised not to rely exclusively on the program for
# any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED
# HEREUNDER IS ON AN “AS IS” BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO
# OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
# MODIFICATIONS.
# 
# 
##################################################################################
# Imports
##################################################################################
import matplotlib
# use this setting on COMET / Skyriver for x forwarding
matplotlib.use('TkAgg')
from datetime import datetime as dt
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize as nrm
from matplotlib.cm import get_cmap
from matplotlib.colorbar import Colorbar as cb
import seaborn as sns
import numpy as np
import pickle
import os
from py_plt_utilities import USR_HME

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flow to analyze 
#CTR_FLW = 'deterministic_forecast_lag00_b0.00'
#CTR_FLW = 'deterministic_forecast_lag06_b0.00'
#CTR_FLW = 'deterministic_forecast_lag00_b1.00'
CTR_FLW = 'ECMWF'
#CTR_FLW = 'GFS'

# define case-wise sub-directory
CSE = 'VD'

# verification domain for the forecast data
#GRD='d02'
GRD='0.25'

# starting date and zero hour of forecast cycles
START_DT = '2019-02-11T00:00:00'

# final date and zero hour of data of forecast cycles
END_DT = '2019-02-14T00:00:00'

# valid date for the verification
VALID_DT = '2019-02-15T00:00:00'

# number of hours between zero hours for forecast data
CYCLE_INT = 24

# MET stat file type -- should be leveled data
#TYPE = 'cts'
#TYPE = 'nbrcts'
TYPE = 'nbrcnt'

# MET stat column names to be made to heat plots / labels
#STATS = ['HK', 'GSS']
#STATS = ['PODY', 'POFD']
#STATS = ['CSI', 'FBIAS']
#STATS = ['FAR', 'POFD']
STATS = ['FSS', 'AFSS']

# landmask for verification region -- need to be set in earlier preprocessing
LND_MSK = 'CALatLonPoints'
#LND_MSK = 'FULL'

##################################################################################
# Begin plotting
##################################################################################
# Create a figure
fig = plt.figure(figsize=(11.25,8.63))

# Set the axes
ax0 = fig.add_axes([.885, .10, .03, .8])
ax1 = fig.add_axes([.085, .10, .39, .8])
ax2 = fig.add_axes([.485, .10, .39, .8])

# define derived data paths 
param = CTR_FLW.split('_')[-1]
cse = CSE + '/' + CTR_FLW
data_root = USR_HME + '/data/analysis/' + cse + '/MET_analysis'
stat1 = STATS[0]
stat2 = STATS[1]

# create date time object from string
valid_dt = dt.fromisoformat(VALID_DT)

# define the output name
in_path = data_root + '/grid_stats_' + GRD + '_' + START_DT +\
          '_to_' + END_DT + '.bin'

out_path = data_root + '/' + VALID_DT + '_' + LND_MSK + '_' + stat1 + '_' +\
           stat2 + '_heatplot.png'

f = open(in_path, 'rb')
data = pickle.load(f)
f.close()

# load the values for valid time with landmask, lead and threshold
vals = [
        'VX_MASK',
        'FCST_LEAD',
        'FCST_THRESH',
        'FCST_VALID_END',
       ]
vals += STATS

# cut down df to specified region and valid time, obtain levels of data 
stat_data = data[TYPE][vals]
stat_data = stat_data.loc[(stat_data['VX_MASK'] == LND_MSK)]
stat_data = stat_data.loc[(stat_data['FCST_VALID_END'] ==
                           valid_dt.strftime('%Y%m%d_%H%M%S'))]

# NOTE: sorting below is designed to handle the issue of string sorting with
# symbols and non-left-padded decimals

# sorts first on length of integer expansion with inequalities, secondly on char
data_levels = sorted(list(set(stat_data['FCST_THRESH'].values)),
                     key=lambda x:(len(x.split('.')[0]), x), reverse=True)

# sorts first on length of integer expansion for hours, secondly on char
data_leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                    key=lambda x:(len(x), x))
num_levels = len(data_levels)
num_leads = len(data_leads)

# create array storage for probs
tmp = np.zeros([num_levels, num_leads, 2])

for k in range(2):
    for i in range(num_levels):
        for j in range(num_leads):
            val = stat_data.loc[(stat_data['FCST_THRESH'] == data_levels[i]) &
                                 (stat_data['FCST_LEAD'] == data_leads[j])]
            
            tmp[i, j, k] = val[STATS[k]]

# define the color bar scale depending on the stat
if (stat1 == 'GSS') or\
   (stat1 == 'BAGSS') or\
   (stat1 == 'HK') or\
   (stat2 == 'GSS') or\
   (stat2 == 'BAGSS') or\
   (stat2 == 'HK'):
    min_scale = -0.25
    max_scale = 1.0

elif (stat1 == 'FBIAS') or\
     (stat2 == 'FBIAS'):
    min_scale = 0.0
    max_scale = 1.25

else:
    max_scale = 1.0
    min_scale = 0.0

color_map = sns.cubehelix_palette(20, start=.75, rot=1.50, as_cmap=True,
                                  reverse=True, dark=0.25)
sns.heatmap(tmp[:,:,0], linewidth=0.5, ax=ax1, cbar_ax=ax0, vmin=min_scale,
            vmax=max_scale, cmap=color_map)
sns.heatmap(tmp[:,:,1], linewidth=0.5, ax=ax2, cbar_ax=ax0, vmin=min_scale,
            vmax=max_scale, cmap=color_map)

##################################################################################
# define display parameters

# generate tic labels based on hour values
for i in range(num_leads):
    data_leads[i] = data_leads[i][:2]

ax0.set_yticklabels(ax0.get_yticklabels(), rotation=270, va='top')
ax1.set_xticklabels(data_leads)
ax1.set_yticklabels(data_levels)
ax2.set_xticklabels(data_leads)
ax2.set_yticklabels(data_levels)

# tick parameters
ax0.tick_params(
        labelsize=18
        )

ax1.tick_params(
        labelsize=18
        )

ax2.tick_params(
        labelsize=18,
        left=False,
        labelleft=False,
        right=False,
        labelright=False,
        )

title1='24hr accumulated precip at ' + VALID_DT
title2='Verification region -- ' + LND_MSK + ' ' + param
lab1='Forecast lead hrs'
lab2='Precip Thresh mm'
lab3=STATS[0]
lab4=STATS[1]
plt.figtext(.5, .02, lab1, horizontalalignment='center',
            verticalalignment='center', fontsize=22)

plt.figtext(.02, .5, lab2, horizontalalignment='center',
            verticalalignment='center', fontsize=22, rotation=90)

plt.figtext(.5, .98, title1, horizontalalignment='center',
            verticalalignment='center', fontsize=22)

plt.figtext(.5, .93, title2, horizontalalignment='center',
            verticalalignment='center', fontsize=22)

plt.figtext(.06, .02, lab3, horizontalalignment='left',
            verticalalignment='center', fontsize=22)

plt.figtext(.90, .02, lab4, horizontalalignment='right',
            verticalalignment='center', fontsize=22)

# save figure and display
plt.savefig(out_path)
plt.show()

##################################################################################
# end
