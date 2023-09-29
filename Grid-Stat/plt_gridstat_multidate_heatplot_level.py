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
# use this setting on COMET / Skyriver for x forwarding
matplotlib.use('AGG')
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
import post_processing_config as config
from proc_gridstat import OUT_ROOT

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################

# MET stat file type -- should be leveled data
TYPE = 'nbrcnt'

# MET stat column names to be made to heat plots / labels
STAT = 'FSS'

# define color map to be used for heat plot color bar
COLOR_MAP = sns.cubehelix_palette(20, start=.75, rot=1.50, as_cmap=True,
                                          reverse=True, dark=0.25)

# define plot title
TITLE = STAT + ' Precip Thresh ' + config.LEV + ' mm - '
split_string = config.CTR_FLW.split('_')
split_len = len(split_string)
idx_len = len(config.LAB_IDX)
line_lab = ''
lab_len = min(idx_len, split_len)
if lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        i_li = config.LAB_IDX[-i_ll]
        TITLE += split_string[i_li] + '_'

    i_li = config.LAB_IDX[-1]
    TITLE += split_string[i_li]

else:
    TITLE += split_string[0]

if len(config.PRFX) > 0:
    pfx = '_' + config.PRFX

else:
    pfx = ''

line_lab += config.PRFX

if len(config.GRD) > 0:
    grd = '_' + config.GRD

else:
    grd = ''

if config.GRD_LAB:
    TITLE += grd

lnd_msk_split = config.LND_MSK.split('_')
TITLE += ', Region -'
for split in lnd_msk_split:
    TITLE += ' ' + split

# fig saved automatically to OUT_PATH
if len(config.FIG_LAB) > 0:
    fig_lab = '_' + config.FIG_LAB
else:
    fig_lab = ''

OUT_DIR = OUT_ROOT + '/figures' + config.FIG_CSE
OUT_PATH = OUT_DIR + '/' + config.ANL_STRT + '_' + config.ANL_END + '_FCST_' + config.MAX_LD + '_' +\
           config.LND_MSK + '_' + STAT + '_' + config.LEV + '_' + config.CTR_FLW + pfx + grd +\
           fig_lab +'_heatplot.png'

##################################################################################
# Make data checks and determine all lead times over all files
##################################################################################
# convert to date times

if len(config.STRT_DT) != 10:
    print('ERROR: STRT_DT, ' + config.STRT_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    sd_iso = config.STRT_DT[:4] + '-' + config.STRT_DT[4:6] + '-' + config.STRT_DT[6:8] +\
            '_' + config.STRT_DT[8:]
    strt_dt = dt.fromisoformat(sd_iso)

if len(config.END_DT) != 10:
    print('ERROR: END_DT, ' + config.END_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    ed_iso = config.END_DT[:4] + '-' + config.END_DT[4:6] + '-' + config.END_DT[6:8] +\
            '_' + config.END_DT[8:]
    end_dt = dt.fromisoformat(ed_iso)

if len(config.CYC_INT) != 2:
    print('ERROR: CYC_INT, ' + config.CYC_INT + ', is not in HH format.')
    sys.exit(1)
else:
    cyc_int = config.CYC_INT + 'H'

if len(config.ANL_STRT) != 10:
    print('ERROR: ANL_STRT, ' + config.ANL_STRT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    as_iso = config.ANL_STRT[:4] + '-' + config.ANL_STRT[4:6] + '-' + config.ANL_STRT[6:8] +\
            '_' + config.ANL_STRT[8:]
    anl_strt = dt.fromisoformat(as_iso)

if len(config.ANL_END) != 10:
    print('ERROR: ANL_END, ' + config.ANL_END + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    ae_iso = config.ANL_END[:4] + '-' + config.ANL_END[4:6] + '-' + config.ANL_END[6:8] +\
            '_' + config.ANL_END[8:]
    anl_end = dt.fromisoformat(ae_iso)

if len(config.ANL_INT) != 2:
    print('ERROR: ANL_INT, ' + config.ANL_INT + ', is not in HH format.')
    sys.exit(1)
else:
    anl_int = config.ANL_INT + 'H'
    
# generate the date range and forecast leads for the analysis, parse binary files
# for relevant fields
fcst_zhs = pd.date_range(start=strt_dt, end=end_dt, freq=cyc_int).to_pydatetime()

fcst_leads = []
# generate the date range for the analyses
anl_dates = pd.date_range(start=anl_strt, end=anl_end,
                          freq=anl_int).to_pydatetime()

data_root = OUT_ROOT + '/' + config.CTR_FLW
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
    stat_data = stat_data.loc[(stat_data['FCST_THRESH'] == config.LEV)]
    stat_data = stat_data.loc[(stat_data['VX_MASK'] == config.LND_MSK)]

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
    if int(ld) > int(config.MAX_LD):
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

if config.DYN_SCL:
    # find the max / min value over the inner 100 - alpha range of the data
    scale = tmp[~np.isnan(tmp)]
    alpha = 1
    max_scale, min_scale = np.percentile(scale, [100 - alpha / 2, alpha / 2])

else:
    # min scale and max scale are set in the above
    min_scale = config.MIN_SCALE
    max_scale = config.MAX_SCALE

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
#plt.show()

##################################################################################
# end
