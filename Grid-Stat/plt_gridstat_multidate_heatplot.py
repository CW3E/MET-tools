##################################################################################
# Description
##################################################################################
# This script is designed to generate heat plots in Matplotlib from MET grid_stat
# output files, preprocessed with the companion script proc_24hr_QPF.py. This
# plotting scheme is designed to plot forecast lead in the vertical axis and the
# valid time for verification from the forecast initialization in the horizontal
# axis. The global parameters for the script below control the initial times for
# the forecast initializations, as well as the valid date of the verification.
# Stats to compare can be reset in the global parameters with heat map color bar
# changing scale dynamically.
#
##################################################################################
# License Statement
##################################################################################
#
# Copyright 2023 Colin Grudzien, cgrudzien@ucsd.edu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
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
import pandas as pd
import pickle
import os
import sys
from proc_gridstat import OUT_ROOT

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flow to analyze 
CTR_FLW = 'NRT_gfs'

# Define the max number of underscore components of control flow names to include in
# fig title. This includes components of the strings above from last to first. Set to
# number of underscore separated compenents in the string to obtain the full
# name in the fig title. Note: a non-empty prefix value below will always be
# included in the fig title
LAB_LEN = 2

# define if fig title includes grid
GRD_LAB = True

# define optional gridstat prefix 
PRFX = ''

# fig label for output file organization, included in figure file name
FIG_LAB = ''

# fig case directory, includes leading '/', leave as empty string if not needed
FIG_CSE = ''

# verification domain for the forecast data
GRD='d01'

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2022121400'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
END_DT = '2023011800'

# number of hours between zero hours for forecast data (string HH)
CYC_INT = '24'

# first valid time for verification (string YYYYMMDDHH)
ANL_STRT = '2022122400'

# final valid time (string YYYYMMDDHH)
ANL_END = '2023012800'

# cycle interval verification valid times (string HH)
ANL_INT = '24'

# MET stat file type -- should not be leveled data
TYPE = 'cnt'

# MET stat column names to be made to heat plots / labels
STAT = 'RMSE'

# define color map to be used for heat plot color bar
COLOR_MAP = sns.color_palette('viridis', as_cmap=True)

# use dynamic color bar scale depending on data percentiles, True / False
# Use this as True by default unless specifying a specific color bar scale and
# scheme in the below
DYN_SCL = True

# these values will only be used if the DYN_SCL above is set to False
MIN_SCALE = 0.0
MAX_SCALE = 1.0

# landmask for verification region -- need to be set in gridstat options
LND_MSK = 'CALatLonPoints'

# define plot title
TITLE = STAT + ' - '
split_string = CTR_FLW.split('_')
split_len = len(split_string)
lab_len = min(LAB_LEN, split_len)
if lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        TITLE += split_string[-i_ll] + '_'
TITLE += split_string[-1] 

if GRD_LAB:
    TITLE += ' ' + GRD

if PRFX:
    TITLE += ' ' + PRFX

TITLE += ' ' + LND_MSK

# fig saved automatically to OUT_PATH
OUT_DIR = OUT_ROOT + '/figures' + FIG_CSE
OUT_PATH = OUT_DIR + '/' + STRT_DT + '_' + END_DT + '_' + LND_MSK + '_' +\
           STAT + '_' + CTR_FLW + '_' + GRD

if PRFX:
    OUT_PATH += '_' + PRFX

OUT_PATH += FIG_LAB + '_heatplot.png'

##################################################################################
# Begin plotting
##################################################################################
# convert to date times
if len(STRT_DT) != 10:
    print('ERROR: STRT_DT, ' + STRT_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)

if len(END_DT) != 10:
    print('ERROR: END_DT, ' + END_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)

if len(CYC_INT) != 2:
    print('ERROR: CYC_INT, ' + CYC_INT + ', is not in HH format.')
    sys.exit(1)
    
if len(ANL_STRT) != 10:
    print('ERROR: ANL_STRT, ' + ANL_STRT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    s_iso = ANL_STRT[:4] + '-' + ANL_STRT[4:6] + '-' + ANL_STRT[6:8] +\
            '_' + ANL_STRT[8:]
    anl_strt = dt.fromisoformat(s_iso)

if len(ANL_END) != 10:
    print('ERROR: ANL_END, ' + ANL_END + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    e_iso = ANL_END[:4] + '-' + ANL_END[4:6] + '-' + ANL_END[6:8] +\
            '_' + ANL_END[8:]
    anl_end = dt.fromisoformat(e_iso)

if len(ANL_INT) != 2:
    print('ERROR: ANL_INT, ' + ANL_INT + ', is not in HH format.')
    sys.exit(1)
else:
    anl_int = ANL_INT + 'H'
    
# generate the date range for the analyses
anl_dates = pd.date_range(start=anl_strt, end=anl_end,
                          freq=anl_int).to_pydatetime()

# Create a figure
fig = plt.figure(figsize=(12,9.6))

# Set the axes
ax0 = fig.add_axes([.92, .18, .03, .77])
ax1 = fig.add_axes([.07, .18, .84, .77])

# define derived data paths 
if len(PRFX) > 0:
    PRFX += '_'

# define the output name
in_path = OUT_ROOT + '/' + CTR_FLW + '/grid_stats_' + PRFX + GRD + '_' +\
          STRT_DT + '_to_' + END_DT + '.bin'

try:
    with open(in_path, 'rb') as f:
        data = pickle.load(f)
except:
    print('ERROR: input data ' + in_path + ' does not exist.')
    sys.exit(1)

# load the values to be plotted along with landmask, lead and threshold
vals = [
        'VX_MASK',
        'FCST_LEAD',
        'FCST_VALID_END',
       ]
vals += [STAT]

# cut down df to specified region and level of data 
stat_data = data[TYPE][vals]
stat_data = stat_data.loc[(stat_data['VX_MASK'] == LND_MSK)]

# NOTE: sorting below is designed to handle the issue of string sorting with
# symbols and non-left-padded decimals

# sorts first on length of integer expansion for hours, secondly on char
data_leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                    key=lambda x:(len(x), x), reverse=True)
data_dates = []
num_leads = len(data_leads)
num_dates = len(anl_dates)

# create array storage for probs
tmp = np.empty([num_leads, num_dates])
tmp[:] = np.nan

for i_nd in range(num_dates):
    for i_nl in range(num_leads):
        if i_nl == 0:
            # on the first loop pack the tick labels
            if ( i_nd % 2 ) == 0 or num_dates < 10:
              # if 10 or more leads, only use every other as a label
              data_dates.append(anl_dates[i_nd].strftime('%Y%m%d'))
            else:
                data_dates.append('')

        try:
            val = stat_data.loc[(stat_data['FCST_LEAD'] == data_leads[i_nl]) &
                                (stat_data['FCST_VALID_END'] == anl_dates[i_nd].strftime('%Y%m%d_%H%M%S'))]
            
            if not val.empty:
                tmp[i_nl, i_nd] = val[STAT]

        except:
            continue

if DYN_SCL:
    # find the max / min value over the inner 100 - alpha range of the data
    scale = tmp[~np.isnan(tmp)]
    alpha = 1
    max_scale, min_scale = np.percentile(scale, [100 - alpha / 2, alpha / 2])

else:
    # min scale and max scale are set in the above
    min_scale = MIN_SCALE
    max_scale = MAX_SCALE

sns.heatmap(tmp[:,:], linewidth=0.5, ax=ax1, cbar_ax=ax0, vmin=min_scale,
            vmax=max_scale, cmap=COLOR_MAP)

##################################################################################
# define display parameters

# generate tic labels based on hour values
for i in range(num_leads):
    data_leads[i] = data_leads[i][:-4]

ax0.set_yticklabels(ax0.get_yticklabels(), rotation=270, va='top')
ax1.set_xticklabels(data_dates, rotation=45, ha='right')
ax1.set_yticklabels(data_leads)

# tick parameters
ax0.tick_params(
        labelsize=16
        )

ax1.tick_params(
        labelsize=16
        )

lab1='Verification Valid Date'
lab2='Forecast Lead Hrs'
plt.figtext(.5, .02, lab1, horizontalalignment='center',
            verticalalignment='center', fontsize=20)

plt.figtext(.02, .565, lab2, horizontalalignment='center',
            verticalalignment='center', fontsize=20, rotation=90)

plt.figtext(.5, .98, TITLE, horizontalalignment='center',
            verticalalignment='center', fontsize=20)

# save figure and display
plt.savefig(OUT_PATH)
plt.show()

##################################################################################
# end
