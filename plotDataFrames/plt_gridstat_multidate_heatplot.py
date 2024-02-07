##################################################################################
# Description
##################################################################################
# This script is designed to generate heat plots in Matplotlib from MET grid_stat
# output files, preprocessed with the companion script proc_gridstat.py. This
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
# Copyright 2023 CW3E, Contact Colin Grudzien cgrudzien@ucsd.edu
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

# Execute configuration file supplied as command line argument
CFG = sys.argv[1]
cmd = 'from ' + CFG + ' import *'
print(cmd)
exec(cmd)

##################################################################################
# Make data checks and determine all lead times over all files
##################################################################################
if not STRT_DT.isdigit() or len(STRT_DT) != 10:
    print('ERROR: STRT_DT\n' + STRT_DT + '\n is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    iso = STRT_DT[:4] + '-' + STRT_DT[4:6] + '-' + STRT_DT[6:8] + '_' +\
            STRT_DT[8:]
    strt_dt = dt.fromisoformat(iso)

if not STRT_DT.isdigit() or len(STOP_DT) != 10:
    print('ERROR: STOP_DT\n' + STOP_DT + '\n is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    iso = STOP_DT[:4] + '-' + STOP_DT[4:6] + '-' + STOP_DT[6:8] + '_' +\
            STOP_DT[8:]
    stop_dt = dt.fromisoformat(iso)

if not CYC_INC.isdigit():
    print('ERROR: CYC_INC\n' + CYC_INC + '\n is not in HH format.')
    sys.exit(1)
else:
    cyc_inc = CYC_INC + 'H'

if not MAX_LD.isdigit():
    print('ERROR: MAX_LD, ' + MAX_LD + ', is not HH format.')
    sys.exit(1)
else:
    max_ld = int(MAX_LD)

try:
    if DYN_SCL:
        if ALPHA <= 0 or ALPHA >= 100:
            print('ERROR: ALPHA must be between 0 and 100 to define the'+\
                    ' inner 100 - ALPHA range of data.')
            sys.exit(1)

    elif not DYN_SCL:
        if MIN_SCALE >= MAX_SCALE:
            print('ERROR: MIN_SCALE must be less than MAX_SCALE for valid'+\
                    ' color bar.')
except:
    print('ERROR: DYN_SCL, ' + str(DYN_SCL) + ' must be equal to True or False.')
    print('If True supply ALPHA value or if False supply min / max scale.')
    sys.exit(1)

# generate the date range and forecast leads for the analysis, parse binary files
# for relevant fields
plt_data = {}
fcst_zhs = pd.date_range(start=strt_dt, end=stop_dt, freq=cyc_inc).to_pydatetime()

fcst_leads = []
# define derived data paths 
data_root = IN_ROOT + '/' + CTR_FLW + '/' + MET_TOOL

if len(MEM) > 0:
    ens = '_' + MEM
else:
    ens = ''

if len(GRD) > 0:
    grd = '_' + GRD
else:
    grd = ''

key = CTR_FLW + ens + grd
for fcst_zh in fcst_zhs:
    # define the input name
    zh_str = fcst_zh.strftime('%Y%m%d%H')
    in_path = data_root + '/' + zh_str + '/' + PRFX + ens + grd +\
              '_' + zh_str + '.bin'
    
    try:
        with open(in_path, 'rb') as f:
            data = pickle.load(f)
            data = data[TYPE]

    except:
        print('WARNING: input data ' + in_path + ' statistics ' + TYPE +\
                ' does not exist, skipping this configuration.')
        continue

    # load the values to be plotted along with landmask and lead
    vals = [
            'VX_MASK',
            'FCST_LEAD',
            'FCST_VALID_END',
            STAT,
           ]

    # cut down df to specified valid date / region / relevant stat
    stat_data = data[vals]
    stat_data = stat_data.loc[(stat_data['VX_MASK'] == MSK)]

    # check if there is data for this configuration and these fields
    if not stat_data.empty:
        leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                       key=lambda x:(len(x), x))

        if key in plt_data.keys():
            # if there is existing data, concatenate dataframes
            plt_data[key]['data'] = pd.concat([plt_data[key]['data'],
                stat_data], axis=0)
        else:
            # if this is a first instance, create fields
            plt_data[key] = {'data': stat_data, 'label': line_lab}

        # obtain leads of data 
        fcst_leads += leads

# find all unique values for forecast leads, sorted for plotting, less than max lead
fcst_leads = sorted(list(set(fcst_leads)), key=lambda x:(len(x), x))
i_fl = 0
while i_fl < len(fcst_leads):
    ld = fcst_leads[i_fl][:-4]
    i_fl += 1

num_leads = len(fcst_leads)

##################################################################################
# Begin plotting
##################################################################################
# Create a figure
fig = plt.figure(figsize=(12,9.6))

# Set the axes
ax0 = fig.add_axes([.92, .18, .03, .77])
ax1 = fig.add_axes([.07, .18, .84, .77])

num_leads = len(fcst_leads)
# NOTE: need to continue revising here to handle forecast valid date range
num_dates = len(anl_dates)

# create array storage for stats
tmp = np.empty([num_leads, num_dates])
tmp[:] = np.nan
fcst_dates = []

# reverse order for plotting
fcst_leads = fcst_leads[::-1]

for i_nd in range(num_dates):
    for i_nl in range(num_leads):
        if i_nl == 0:
            # on the first lead-loop of each date pack the date tick labels
            if ( i_nd % 2 ) == 0 or num_dates < 10:
              # if 10 or more dates, only use every other as a label
              fcst_dates.append(anl_dates[i_nd].strftime('%Y%m%d'))
            else:
                fcst_dates.append('')

        try:
            # try to load data for the date / lead combination
            val = plt_data.loc[(plt_data['FCST_LEAD'] == fcst_leads[i_nl]) &
                                (plt_data['FCST_VALID_END'] == anl_dates[i_nd].strftime('%Y%m%d_%H%M%S'))]
            
            if not val.empty:
                tmp[i_nl, i_nd] = val[STAT]

        except:
            continue

if DYN_SCL:
    # find the max / min value over the inner 100 - ALPHA range of the data
    scale = tmp[~np.isnan(tmp)]
    max_scale, min_scale = np.percentile(scale, [100 - ALPHA / 2, ALPHA / 2])

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
    fcst_leads[i] = fcst_leads[i][:-4]

ax0.set_yticklabels(ax0.get_yticklabels(), rotation=270, va='top')
ax1.set_xticklabels(fcst_dates, rotation=45, ha='right')
ax1.set_yticklabels(fcst_leads)

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
