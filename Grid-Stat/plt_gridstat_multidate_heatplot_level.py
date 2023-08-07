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
from matplotlib.colors import LogNorm
from matplotlib.cm import get_cmap
from matplotlib.colorbar import Colorbar as cb
import pandas as pd
import seaborn as sns
import numpy as np
import pickle
import os
import sys
from proc_gridstat import OUT_ROOT
import ipdb

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flow to analyze 
CTR_FLW = 'NRT_gfs'

# Define a list of indices for underscore-separated components of control flow
# names to include in fig legend. Note: a non-empty prefix value below will
# always be included in the legend label, and control flows with fewer components
# than indices above will only include those label components that exist
LAB_IDX = [0, 1]

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
FCST_STRT = '2022121400'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
FCST_END = '2023011800'

# number of hours between zero hours for forecast data (string HH)
CYC_INT = '24'

# Max forecast lead to plot in hours
MAX_LD = '240'

# first valid time for verification (string YYYYMMDDHH)
ANL_STRT = '2022122400'

# final valid time (string YYYYMMDDHH)
ANL_END = '2023011900'

# cycle interval verification valid times (string HH)
ANL_INT = '24'

# threshold level to plot
LEV = '>=25.0'

# MET stat file type -- should be leveled data
TYPE = 'nbrcnt'

# MET stat column names to be made to heat plots / labels
STAT = 'FSS'

# define color map to be used for heat plot color bar
COLOR_MAP = sns.cubehelix_palette(20, start=.75, rot=1.50, as_cmap=True,
                                          reverse=True, dark=0.25)

# use dynamic color bar scale depending on data percentiles, True / False
# Use this as True by default unless specifying a specific color bar scale and
# scheme in the below
DYN_SCL = True

# these values will only be used if the DYN_SCL above is set to False
MIN_SCALE = 0.0
MAX_SCALE = 1.0

# landmask for verification region -- needs to be set in gridstat options
LND_MSK = 'CA_All'

# define plot title
TITLE = STAT + ' Precip Thresh ' + LEV + ' mm - '
split_string = CTR_FLW.split('_')
split_len = len(split_string)
idx_len = len(LAB_IDX)
line_lab = ''
lab_len = min(idx_len, split_len)
if lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        i_li = LAB_IDX[-i_ll]
        TITLE += split_string[i_li] + '_'

    i_li = LAB_IDX[-1]
    TITLE += split_string[i_li]

else:
    TITLE += split_string[0]

if len(PRFX) > 0:
    pfx = '_' + PRFX

else:
    pfx = ''

line_lab += PRFX

if len(GRD) > 0:
    grd = '_' + GRD

else:
    grd = ''

if GRD_LAB:
    TITLE += grd

lnd_msk_split = LND_MSK.split('_')
TITLE += ', Region -'
for split in lnd_msk_split:
    TITLE += ' ' + split

# fig saved automatically to OUT_PATH
if len(FIG_LAB) > 0:
    fig_lab = '_' + FIG_LAB
else:
    fig_lab = ''

OUT_DIR = OUT_ROOT + '/figures' + FIG_CSE
OUT_PATH = OUT_DIR + '/' + ANL_STRT + '_' + ANL_END + '_FCST_' + MAX_LD + '_' +\
           LND_MSK + '_' + STAT + '_' + LEV + '_' + CTR_FLW + pfx + grd +\
           fig_lab +'_heatplot.png'

##################################################################################
# Make data checks and determine all lead times over all files
##################################################################################
# convert to date times
if len(FCST_STRT) != 10:
    print('ERROR: FCST_STRT, ' + FCST_STRT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    sd_iso = FCST_STRT[:4] + '-' + FCST_STRT[4:6] + '-' + FCST_STRT[6:8] +\
            '_' + FCST_STRT[8:]
    fcst_strt = dt.fromisoformat(sd_iso)

if len(FCST_END) != 10:
    print('ERROR: FCST_END, ' + FCST_END + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    ed_iso = FCST_END[:4] + '-' + FCST_END[4:6] + '-' + FCST_END[6:8] +\
            '_' + FCST_END[8:]
    fcst_end = dt.fromisoformat(ed_iso)

if len(CYC_INT) != 2:
    print('ERROR: CYC_INT, ' + CYC_INT + ', is not in HH format.')
    sys.exit(1)
else:
    cyc_int = CYC_INT + 'H'

if len(ANL_STRT) != 10:
    print('ERROR: ANL_STRT, ' + ANL_STRT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    as_iso = ANL_STRT[:4] + '-' + ANL_STRT[4:6] + '-' + ANL_STRT[6:8] +\
            '_' + ANL_STRT[8:]
    anl_strt = dt.fromisoformat(as_iso)

if len(ANL_END) != 10:
    print('ERROR: ANL_END, ' + ANL_END + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    ae_iso = ANL_END[:4] + '-' + ANL_END[4:6] + '-' + ANL_END[6:8] +\
            '_' + ANL_END[8:]
    anl_end = dt.fromisoformat(ae_iso)

if len(ANL_INT) != 2:
    print('ERROR: ANL_INT, ' + ANL_INT + ', is not in HH format.')
    sys.exit(1)
else:
    anl_int = ANL_INT + 'H'
    
# generate the date range and forecast leads for the analysis, parse binary files
# for relevant fields
fcst_zhs = pd.date_range(start=fcst_strt, end=fcst_end, freq=cyc_int).to_pydatetime()

fcst_leads = []
# generate the date range for the analyses
anl_dates = pd.date_range(start=anl_strt, end=anl_end,
                          freq=anl_int).to_pydatetime()

data_root = OUT_ROOT + '/' + CTR_FLW
plt_data = pd.DataFrame()
for fcst_zh in fcst_zhs:
    # define the input name
    zh_strng = fcst_zh.strftime('%Y%m%d%H')
    in_path = data_root + '/' + zh_strng + '/grid_stats' + pfx + grd +\
              '_' + zh_strng + '.bin'
    
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
            'FCST_THRESH',
           ]

    # include the statistics and their confidence intervals
    vals += [STAT]
    
    # cut down df to specified region / level / relevant stats
    stat_data = data[vals]
    stat_data = stat_data.loc[(stat_data['FCST_THRESH'] == LEV)]
    stat_data = stat_data.loc[(stat_data['VX_MASK'] == LND_MSK)]

    # check if there is data for this configuration and these fields
    if not stat_data.empty:
        plt_data = pd.concat([plt_data, stat_data], axis=0)

        # obtain leads of data 
        leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                       key=lambda x:(len(x), x))
        fcst_leads += leads

# find all unique values for forecast leads, sorted for plotting, less than max lead
fcst_leads = sorted(list(set(fcst_leads)), key=lambda x:(len(x), x))
i_fl = 0
while i_fl < len(fcst_leads):
    ld = fcst_leads[i_fl][:-4]
    if int(ld) > int(MAX_LD):
        del fcst_leads[i_fl]
    else:
        i_fl += 1

##################################################################################
# Begin plotting
##################################################################################
# Create a figure
fig = plt.figure(figsize=(12,9.6))

# Set the axes
ax0 = fig.add_axes([.92, .18, .03, .77])
ax1 = fig.add_axes([.07, .18, .84, .77])

num_leads = len(fcst_leads)
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
            # on the first loop pack the tick labels
            if ( i_nd % 2 ) == 0 or num_dates < 10:
              # if 10 or more leads, only use every other as a label
              fcst_dates.append(anl_dates[i_nd].strftime('%Y%m%d'))
            else:
                fcst_dates.append('')

        try:
            val = plt_data.loc[(plt_data['FCST_LEAD'] == fcst_leads[i_nl]) &
                                (plt_data['FCST_VALID_END'] == anl_dates[i_nd].strftime('%Y%m%d_%H%M%S'))]
            
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
