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
from matplotlib.colors import BoundaryNorm, ListedColormap
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

if not ANL_STRT.isdigit() or len(ANL_STOP) != 10:
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

if not FIX_LD.isdigit():
    print('ERROR: FIX_LD, ' + FIX_LD + ', is not HH format.')
    sys.exit(1)
else:
    fix_ld = int(FIX_LD)

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

fcst_zhs = []
for i_d in range(total_dts):
    fcst_zhs.append(anl_dts[i_d] - td(hours=fix_ld))

# generate the date range and forecast levels for the analysis, parse binary files
# for relevant fields
plt_data = {}

for cfg in ['ANL', 'REF']:
    # define storage for the forecast levels per cfg
    exec('%s_fcst_levs = []'%(cfg))

    # define derived data paths 
    exec('data_root = IN_ROOT + \'/\' + %s_CFG + \'/\' + MET_TOOL'%(cfg))
    
    exec('MEM = %s_MEM'%(cfg))
    exec('GRD = %s_GRD'%(cfg))
    
    if len(MEM) > 0:
        ens = '_' + MEM
    else:
        ens = ''
    
    if len(GRD) > 0:
        grd = '_' + GRD
    else:
        grd = ''
    
    exec('key = %s_CFG + ens + grd'%(cfg))
    exec('%s_key = %s_CFG + ens + grd'%(cfg, cfg))
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
                'FCST_THRESH',
                STAT,
               ]
    
        # cut down df to specified valid date / region / relevant stat
        stat_data = data[vals]
        stat_data = stat_data.loc[(stat_data['VX_MASK'] == MSK)]
        stat_data = stat_data.loc[(stat_data['FCST_LEAD'] == FIX_LD + '0000')]
    
        # check if there is data for this configuration and these fields
        if not stat_data.empty:

            levs = sorted(list(set(stat_data['FCST_THRESH'].values)),
                    key=lambda x:(len(x.split('.')[0]), x), reverse=True)
    
            if key in plt_data.keys():
                # if there is existing data, concatenate dataframes
                plt_data[key]['data'] = pd.concat([plt_data[key]['data'],
                    stat_data], axis=0)
            else:
                # if this is a first instance, create fields
                plt_data[key] = {'data': stat_data}

            # obtain levels of data 
            exec('%s_fcst_levs += levs'%(cfg))
    

# find all unique values for forecast levels matching across configurations
fcst_levs = set(ANL_fcst_levs).intersection(set(REF_fcst_levs))
fcst_levs = sorted(list(fcst_levs), key=lambda x:(len(x.split('.')[0]), x),
        reverse=True)
##################################################################################
# Begin plotting
##################################################################################
# Create a figure
fig = plt.figure(figsize=(12,9.6))

# Set the axes
ax0 = fig.add_axes([.86, .24, .05, .56])
ax1 = fig.add_axes([.12, .16, .73, .72])

num_dates = len(anl_dts)
num_levs = len(fcst_levs)

# create array storage for stats
plt_vals = np.full([num_levs, num_dates], np.nan)
scl_vals = np.full([num_levs, num_dates], np.nan)
fcst_dates = []

ref_array = np.zeros((num_levs, num_dates))

for i_nv in range(num_levs):
    for i_nd in range(num_dates):
        if i_nv == 0:
            # on the first lead-loop of each date pack the date tick labels
            if ( i_nd % 2 ) == 0 or num_dates < 10:
              # if 10 or more dates, only use every other as a label
              fcst_dates.append(anl_dts[i_nd].strftime('%Y%m%d'))
            else:
                fcst_dates.append('')

        try:
            # try to load data for the date / level combination
            anl_val = plt_data[ANL_key]['data'].loc[(plt_data[ANL_key]['data']['FCST_THRESH'] ==\
                    fcst_levs[i_nv]) & (plt_data[ANL_key]['data']['FCST_VALID_END'] ==\
                    anl_dts[i_nd].strftime('%Y%m%d_%H%M%S'))]
            
            ref_val = plt_data[REF_key]['data'].loc[(plt_data[REF_key]['data']['FCST_THRESH'] ==\
                    fcst_levs[i_nv]) & (plt_data[REF_key]['data']['FCST_VALID_END'] ==\
                    anl_dts[i_nd].strftime('%Y%m%d_%H%M%S'))]
            
            if not anl_val.empty and not ref_val.empty:
                anl_val = float(anl_val[STAT].values[0])
                ref_val = float(ref_val[STAT].values[0])
                ref_array[i_nv, i_nd] = ref_val

                if np.abs(ref_val) <= 0.1 or np.abs(anl_val) <= 0.1:
                    pass

                else:
                    plt_vals[i_nv, i_nd] = 100 * (anl_val - ref_val) / ref_val
                    scl_vals[i_nv, i_nd] = 100 * (anl_val - ref_val) / ref_val

        except:
            continue

if DYN_SCL:
    # find the max / min value over the inner 100 - ALPHA range of the data
    scale = scl_vals[~np.isnan(scl_vals)]
    max_scale, min_scale = np.percentile(scale, [100 - ALPHA / 2, ALPHA / 2])
    max_scale = max(np.abs(min_scale), np.abs(max_scale))
    min_scale = -max_scale

else:
    # min scale and max scale are set in the above
    min_scale = MIN_SCALE
    max_scale = MAX_SCALE

if max_scale < 100 and min_scale > -100:
    THRESHOLDS = [-100, -50, -25, -15, -0.1, 0.1, 15, 25, 50, 100]
    COLORS = ['#762a83', # -50 to -100%
              '#9970ab', # -25 to -50%
              '#c2a5cf', # -15 to -25%
              '#e7d4e8', # -0.1 to -15%
              '#f7f7f7', # for zero values
              '#d9f0d3', # 0.1 to 15%
              '#a6dba0', # 15 to 25%
              '#5aae61', # 25 to 50%
              '#1b7837', # 50 to 100%
              ]
    labels = ['-100%', '-50%', '-25%', '-15%',
              '-0.1%', '0.1%', '15%', '25%', '50%', '100%']
else:
    THRESHOLDS = [min_scale, -100, -50, -25, -15, -0.1, 0.1, 15, 25, 50, 100, max_scale]
    COLORS = ['#40004b', # < -100%
              '#762a83', # -50 to -100%
              '#9970ab', # -25 to -50%
              '#c2a5cf', # -15 to -25%
              '#e7d4e8', # -0.1 to -15%
              '#f7f7f7', # for zero values
              '#d9f0d3', # 0.1 to 15%
              '#a6dba0', # 15 to 25%
              '#5aae61', # 25 to 50%
              '#1b7837', # 50 to 100%
              '#00441b'  # >100%
              ]
    labels = ['<-100%', '-100%', '-50%', '-25%', '-15%',
              '-0.1%', '0.1%', '15%', '25%', '50%', '100%', '>100%']

COLOR_MAP = ListedColormap(COLORS)

COLOR_MAP.set_bad('darkgrey')

norm = BoundaryNorm(THRESHOLDS, ncolors=len(COLORS))

sns.heatmap(plt_vals, linewidth=0.5, norm=norm, ax=ax1, cbar_ax=ax0, vmin=min_scale,
            vmax=max_scale, cmap=COLOR_MAP, annot=ref_array, annot_kws={"size": 11})

##################################################################################
# define display parameters

# generate tic labels based on hour values
pct_ticks = np.around(np.linspace(min_scale, max_scale, 9), 0)
pct_labs = [str(int(tick)) + '%' for tick in pct_ticks]

ax0.set_yticks(THRESHOLDS)
ax0.set_yticklabels(labels, va='center')
ax1.set_yticklabels(fcst_levs, rotation=45, ha='right')
ax1.set_xticklabels(fcst_dates, rotation=45, ha='right')

# tick parameters
ax0.tick_params(
        labelsize=16
        )

ax1.tick_params(
        labelsize=16
        )

lab1='Verification Valid Date'
lab2='Accumulation threshold (mm)'
plt.figtext(.5, .02, lab1, horizontalalignment='center',
            verticalalignment='center', fontsize=20)

plt.figtext(.02, .5, lab2, horizontalalignment='center',
            verticalalignment='center', fontsize=20, rotation=90)

plt.title(TITLE, x = 0.5, y = 1.05, fontsize = 20)
plt.title(FLD_SUBTITLE, fontsize = 16, loc = 'left')
plt.suptitle(DMN_SUBTITLE, x = 0.5, y = .9075, fontsize = 16)
plt.title(QPE_SUBTITLE, fontsize = 16, loc = 'right')

plt.figtext(.86, .94, '* Reference \n   Score in Cell', horizontalalignment='left',
            verticalalignment='bottom', fontsize=14)

plt.figtext(.86, .1625, 'Skill\nLoss', horizontalalignment='left',
            verticalalignment='bottom', fontsize=20)

plt.figtext(.86, .87, 'Skill\nGain', horizontalalignment='left',
            verticalalignment='top', fontsize=20)

# save figure and display
plt.savefig(OUT_PATH)
plt.show()

##################################################################################
# end