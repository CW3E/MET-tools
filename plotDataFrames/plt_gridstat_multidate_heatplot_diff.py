##################################################################################
# Description
##################################################################################
# This script is designed to generate heat plots in Matplotlib from MET ASCII
# output files, converted to dataframes with the companion postprocessing routines.
# This plotting scheme is designed to plot forecast lead in the vertical axis and
# the valid time for verification from the forecast initialization in the
# horizontal axis.
#
# Parameters for the script are to be supplied from a configuration file, with
# name supplied as a command line argument.
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
from datetime import datetime as dt
from datetime import timedelta as td
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize as nrm
from matplotlib.cm import get_cmap
from matplotlib.colorbar import Colorbar as cb
import pandas as pd
import seaborn as sns
import numpy as np
import pickle
import os
import sys

# Execute configuration file supplied as command line argument
CFG = sys.argv[1].split('.')[0]
cmd = 'from ' + CFG + ' import *'
print(cmd)
exec(cmd)

##################################################################################
# Make data checks and determine all lead times over all files
##################################################################################
if not ANL_STRT.isdigit() or len(ANL_STRT) != 10:
    print('ERROR: ANL_STRT\n' + ANL_STRT + '\n is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    iso = ANL_STRT[:4] + '-' + ANL_STRT[4:6] + '-' + ANL_STRT[6:8] + '_' +\
            ANL_STRT[8:]
    anl_strt = dt.fromisoformat(iso)

if not ANL_STOP.isdigit() or len(ANL_STOP) != 10:
    print('ERROR: ANL_STOP\n' + ANL_STOP + '\n is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    iso = ANL_STOP[:4] + '-' + ANL_STOP[4:6] + '-' + ANL_STOP[6:8] + '_' +\
            ANL_STOP[8:]
    anl_stop = dt.fromisoformat(iso)

if not ANL_INC.isdigit():
    print('ERROR: ANL_INC\n' + ANL_INC + '\n is not in HH format.')
    sys.exit(1)
else:
    anl_inc = ANL_INC + 'h'

if not MAX_LD.isdigit():
    print('ERROR: MAX_LD, ' + MAX_LD + ', is not HH format.')
    sys.exit(1)
else:
    max_ld = int(MAX_LD)

if not CYC_INC.isdigit():
    print('ERROR: CYC_INC\n' + CYC_INC + '\n is not in HH format.')
    sys.exit(1)
else:
    cyc_inc = CYC_INC + 'h'

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

if not MSK:
    print('ERROR: Landmask variable MSK is not defined.')
    sys.exit(1)

# generate valid date range
anl_dts = pd.date_range(start=anl_strt, end=anl_stop, freq=anl_inc).to_pydatetime()
total_dts = len(anl_dts)

fcst_strt = anl_dts[0] - td(hours=max_ld)
fcst_stop = anl_dts[0] - td(hours=int(CYC_INC))
fcst_zhs = pd.date_range(start=fcst_strt, end=fcst_stop, freq=cyc_inc)
for i_d in range(1, total_dts):
    fcst_strt = anl_dts[i_d] - td(hours=max_ld)
    fcst_stop = anl_dts[i_d] - td(hours=int(CYC_INC))
    fcst_zhs = fcst_zhs.union(pd.date_range(start=fcst_strt,
        end=fcst_stop, freq=cyc_inc))

# generate the date range and forecast leads for the analysis, parse binary files
# for relevant fields
fcst_zhs = fcst_zhs.to_pydatetime()
plt_data = {}

fcst_leads = []
for ctr_flw in CTR_FLWS:
    # define derived data paths 
    data_root = IN_ROOT + '/' + ctr_flw + '/' + MET_TOOL

    for grid in GRDS:
        for mem in MEM_IDS:
            if len(mem) > 0:
                ens = '_' + mem
            else:
                ens = ''

            if len(grid) > 0:
                grd = '_' + grid
            else:
                grd = ''

            key = ctr_flw + ens + grd
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
                        plt_data[key] = {'data': stat_data}

                    # obtain leads of data
                    fcst_leads += leads

# find all unique values for forecast leads, sorted for plotting, less than max lead
fcst_leads = sorted(list(set(fcst_leads)), key=lambda x:(len(x), x))
i_fl = 0
while i_fl < len(fcst_leads):
    ld = fcst_leads[i_fl][:-4]
    if int(ld) <= max_ld:
        i_fl += 1

    else:
        del fcst_leads[i_fl]

##################################################################################
# Begin plotting
##################################################################################
# Create a figure
fig = plt.figure(figsize=(12,9.6))

# Set the axes
ax0 = fig.add_axes([.92, .18, .03, .72])
ax1 = fig.add_axes([.07, .18, .84, .72])

# create array storage for stats
num_leads = len(fcst_leads)
num_dates = len(anl_dts)

tmp = np.empty([num_leads, num_dates])
tmp[:] = np.nan
fcst_dates = []

keys = list(plt_data.keys())
key1, key2 = keys[0], keys[1]

# reverse order for plotting
fcst_leads = fcst_leads[::-1]

for i_nd in range(num_dates):
    for i_nl in range(num_leads):
        if i_nl == 0:
            # on the first lead-loop of each date pack the date tick labels
            if ( i_nd % 2 ) == 0 or num_dates < 10:
              # if 10 or more dates, only use every other as a label
              fcst_dates.append(anl_dts[i_nd].strftime('%Y%m%d'))
            else:
                fcst_dates.append('')

        try:
            # try to load data for the date / lead combination
            val1 = plt_data[key1]['data'].loc[(plt_data[key1]['data']['FCST_LEAD'] ==\
                    fcst_leads[i_nl]) & (plt_data[key1]['data']['FCST_VALID_END'] ==\
                    anl_dts[i_nd].strftime('%Y%m%d_%H%M%S'))]

            val2 = plt_data[key2]['data'].loc[(plt_data[key2]['data']['FCST_LEAD'] ==\
                    fcst_leads[i_nl]) & (plt_data[key2]['data']['FCST_VALID_END'] ==\
                    anl_dts[i_nd].strftime('%Y%m%d_%H%M%S'))]


            val = (val2[STAT] - val1[STAT]) / val2[STAT]

            if not val.empty:
                tmp[i_nl, i_nd] = val

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

plt.figtext(.5, .94, SUBTITLE, horizontalalignment='center',
            verticalalignment='center', fontsize=20)

# save figure and display
plt.savefig(OUT_PATH)
plt.show()

##################################################################################
# end
