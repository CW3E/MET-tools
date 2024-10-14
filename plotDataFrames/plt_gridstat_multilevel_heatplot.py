##################################################################################
# Description
##################################################################################
# This script is designed to generate heat plots in Matplotlib from MET ASCII
# output files, converted to dataframes with the companion postprocessing routines.
# This plotting scheme is designed to plot accumulation threshold in the vertical
# axis and the forecast lead from the verfication valid time in the horizontal
# axis.
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
import seaborn as sns
import numpy as np
import pandas as pd
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
if not VLD_DT.isdigit() or len(VLD_DT) != 10:
    print('ERROR: VLD_DT\n' + VLD_DT + '\n is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    iso = VLD_DT[:4] + '-' + VLD_DT[4:6] + '-' + VLD_DT[6:8] + '_' +\
            VLD_DT[8:]
    vld_dt = dt.fromisoformat(iso)

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

# generate the date range and forecast leads for the analysis, parse binary files
# for relevant fields
fcst_strt = vld_dt - td(hours=max_ld)
fcst_stop = vld_dt - td(hours=int(CYC_INC))
fcst_zhs = pd.date_range(start=fcst_strt, end=fcst_stop, freq=cyc_inc)
fcst_zhs = fcst_zhs.to_pydatetime()
plt_data = {}

fcst_leads = []
fcst_levs = []
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
            'FCST_THRESH',
            STAT,
           ]

    # cut down df to specified valid date / region / relevant stat
    stat_data = data[vals]
    stat_data = stat_data.loc[(stat_data['VX_MASK'] == MSK)]

    # check if there is data for this configuration and these fields
    if not stat_data.empty:
        leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                       key=lambda x:(len(x), x))

        levs = sorted(list(set(stat_data['FCST_THRESH'].values)),
                key=lambda x:(len(x.split('.')[0]), x), reverse=True)

        if key in plt_data.keys():
            # if there is existing data, concatenate dataframes
            plt_data[key]['data'] = pd.concat([plt_data[key]['data'],
                stat_data], axis=0)
        else:
            # if this is a first instance, create fields
            plt_data[key] = {'data': stat_data}

        # obtain leads of data 
        fcst_leads += leads
        fcst_levs += levs

# find all unique values for forecast leads, sorted for plotting, less than max lead
fcst_leads = sorted(list(set(fcst_leads)), key=lambda x:(len(x), x))
fcst_levs = sorted(list(set(fcst_levs)),
        key=lambda x:(len(x.split('.')[0]), x), reverse=True)
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
ax0 = fig.add_axes([.91, .10, .03, .80])
ax1 = fig.add_axes([.12, .10, .78, .80])

# create array storage for stats
num_leads = len(fcst_leads)
num_levs = len(fcst_levs)

tmp = np.empty([num_levs, num_leads])
tmp[:] = np.nan

# reverse order for plotting
lead_labs = []

for i_nv in range(num_levs):
    for i_nl in range(num_leads):
        if i_nv == 0:
            # on the first level-loop of each date pack the lead tick labels
            if ( i_nl % 2 ) == 0 or num_leads < 10:
              # if 10 or more dates, only use every other as a label
              lead_labs.append(fcst_leads[i_nl][:-4])
            else:
                fcst_dates.append('')

        try:
            # try to load data for the date / lead combination
            val = plt_data[key]['data'].loc[(plt_data[key]['data']['FCST_LEAD'] ==\
                    fcst_leads[i_nl]) & (plt_data[key]['data']['FCST_VALID_END'] ==\
                    vld_dt.strftime('%Y%m%d_%H%M%S')) &\
                    (plt_data[key]['data']['FCST_THRESH'] == fcst_levs[i_nv]) ]
            
            if not val.empty:
                tmp[i_nv, i_nl] = val[STAT]

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

ax0.set_xticklabels(ax0.get_xticklabels(), rotation=270, va='top')
ax1.set_yticklabels(fcst_levs, rotation=45, ha='right')
ax1.set_xticklabels(lead_labs)

# tick parameters
ax0.tick_params(
        labelsize=16
        )

ax1.tick_params(
        labelsize=16
        )

lab1='Forecast Lead Hrs'
lab2='Accumulation threshold - mm'
plt.figtext(.5, .02, lab1, horizontalalignment='center',
            verticalalignment='center', fontsize=20)

plt.figtext(.02, .5, lab2, horizontalalignment='center',
            verticalalignment='center', fontsize=20, rotation=90)

#plt.figtext(.5, .98, TITLE, horizontalalignment='center',
#            verticalalignment='center', fontsize=20)

#plt.figtext(.5, .94, SUBTITLE, horizontalalignment='center',
#            verticalalignment='center', fontsize=20)

plt.title(TITLE, x = 0.5, y = 1.06, fontsize = 20)
plt.title(VDT_SUBTITLE, fontsize = 16, loc = "left")
plt.suptitle(DMN_SUBTITLE, x = 0.5, y = .927, fontsize = 16)
plt.title(QPE_SUBTITLE, fontsize = 16, loc = "right")

# save figure and display
plt.savefig(OUT_PATH)
plt.show()

##################################################################################
# end

