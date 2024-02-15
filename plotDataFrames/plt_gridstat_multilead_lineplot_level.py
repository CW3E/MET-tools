##################################################################################
# Description
##################################################################################
# This script is designed to generate line plots in Matplotlib from MET ASCII
# output files, converted to dataframes with the companion postprocessing routines.
# This plotting scheme is designed to plot thresholded data as lines in the
# vertical axis and the number of lead hours to the valid time for verification
# from the forecast initialization in the horizontal axis.
#
# Parameters for the script are to be supplied from a configuration file, with
# name supplied as a command line argument.
#
##################################################################################
# License Statement
##################################################################################
#
# Copyright 2024 CW3E, Contact Colin Grudzien cgrudzien@ucsd.edu
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

if not VALID_DT.isdigit() or len(VALID_DT) != 10:
    print('ERROR: VALID_DT, ' + VALID_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    iso = VALID_DT[:4] + '-' + VALID_DT[4:6] + '-' + VALID_DT[6:8] +\
            '_' + VALID_DT[8:]
    valid_dt = dt.fromisoformat(iso)

if not MSK:
    print('ERROR: Landmask variable MSK is not defined.')
    sys.exit(1)

if not LEV:
    print('ERROR: threshold value for leveled data "LEV" is not defined.')
    sys.exit(1)
            
# generate the date range and forecast leads for the analysis, parse binary files
# for relevant fields
plt_data = {}
fcst_zhs = pd.date_range(start=strt_dt, end=stop_dt, freq=cyc_inc).to_pydatetime()

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

            # create label based on configuration
            split_string = ctr_flw.split('_')
            split_len = len(split_string)
            idx_len = len(LAB_IDX)
            line_lab = ''
            lab_len = min(idx_len, split_len)
            if lab_len > 1:
                for i_ll in range(lab_len, 1, -1):
                    i_li = LAB_IDX[-i_ll]
                    line_lab += split_string[i_li] + '_'
    
                i_li = LAB_IDX[-1]
                line_lab += split_string[i_li]
    
            else:
                line_lab += split_string[0]

            if ENS_LAB:
                line_lab += ens
    
            if GRD_LAB:
                    line_lab += grd

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
                        'FCST_THRESH',
                       ]

                # include the statistics and their confidence intervals
                vals += STATS
                for i_ns in range(2):
                    stat = STATS[i_ns]
                    if stat + '_BCL' in data:
                        vals.append(stat + '_BCL')
                        vals.append(stat + '_BCU')
    
                    if stat + '_NCL' in data:
                        vals.append(stat + '_NCL')
                        vals.append(stat + '_NCU')
                
                # cut down df to specified valid date / region / relevant stats
                stat_data = data[vals]
                stat_data = stat_data.loc[(stat_data['VX_MASK'] == MSK)]
                stat_data = stat_data.loc[(stat_data['FCST_THRESH'] == LEV)]
                stat_data = stat_data.loc[(stat_data['FCST_VALID_END'] ==
                                           valid_dt.strftime('%Y%m%d_%H%M%S'))]

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

##################################################################################
# Begin plotting
##################################################################################
# create a figure
fig = plt.figure(figsize=(12,9.6))

# Set the axes
ax0 = fig.add_axes([.110, .395, .85, .33])
ax1 = fig.add_axes([.110, .065, .85, .33])

num_leads = len(fcst_leads)
line_list = []
line_labs = []
ax0_l = []
ax1_l = []

stat0 = STATS[0]
stat1 = STATS[1]

# loop configurations, load trimmed data from plt_data dictionary
for key in plt_data.keys():
    data = plt_data[key]['data']
    line_lab = plt_data[key]['label']
    
    # infer existence of confidence interval data with precedence for bootstrap
    cnf_lvs = []
    for i_ns in range(2):
        stat = STATS[i_ns]
        if stat + '_BCL' in data and\
            not (data[stat + '_BCL'].isnull().values.any()):
                cnf_lvs.append('_BC')
    
        elif stat + '_NCL' in data and\
            not (data[stat + '_NCL'].isnull().values.any()):
                cnf_lvs.append('_NC')
    
        else:
            cnf_lvs.append(False)
    
        exec('ax = ax%s'%i_ns)
        if cnf_lvs[i_ns]:
            tmp = np.empty([num_leads, 3])
            tmp[:] = np.nan
    
            for i_nl in range(num_leads):
                val = data.loc[(data['FCST_LEAD'] == fcst_leads[i_nl])]
                if not val.empty:
                    tmp[i_nl, 0] = val[STATS[i_ns]]
                    tmp[i_nl, 1] = val[STATS[i_ns] + cnf_lvs[i_ns] + 'L']
                    tmp[i_nl, 2] = val[STATS[i_ns] + cnf_lvs[i_ns] + 'U']
            
            l0 = ax.fill_between(range(num_leads), tmp[:, 1], tmp[:, 2], alpha=0.5)
            l1, = ax.plot(range(num_leads), tmp[:, 0], linewidth=2)
            exec('ax%s_l.append([l1,l0])'%i_ns)
            l = l1
    
        else:
            tmp = np.empty([num_leads])
            tmp[:] = np.nan
        
            for i_nl in range(num_leads):
                val = data.loc[(data['FCST_LEAD'] == fcst_leads[i_nl])]
                if not val.empty:
                    tmp[i_nl] = val[STATS[i_ns]]
            
            l, = ax.plot(range(num_leads), tmp[:], linewidth=2)
            exec('ax%s_l.append([l])'%i_ns)
    
    # add the line type to the legend
    line_list.append(l)
    line_labs.append(line_lab)

# set colors and markers
line_count = len(line_list)
line_colors = sns.color_palette('husl', line_count)
for i_lc in range(line_count):
    for i_ns in range(2):
        exec('axl = ax%s_l[i_lc]'%i_ns)
        for i_na in range(len(axl)):
            l = axl[i_na]
            l.set_color(line_colors[i_lc])
            if i_na == 0:
              l.set_marker((i_lc + 2, 0, 0))
              l.set_markersize(18)

##################################################################################
# define display parameters

# generate tic labels based on hour values
for i_nl in range(num_leads):
    fcst_leads[i_nl] = fcst_leads[i_nl][:-4]

ax1.set_xticks(range(num_leads))
ax1.set_xticklabels(fcst_leads)

# tick parameters
ax1.tick_params(
        labelsize=18
        )

ax0.tick_params(
        labelsize=18
        )

ax0.tick_params(
        labelsize=18,
        bottom=False,
        labelbottom=False,
        right=False,
        labelright=False,
        )

ax0.set_yticks(ax0.get_yticks(), ax0.get_yticklabels(), va='bottom')
ax1.set_yticks(ax1.get_yticks(), ax1.get_yticklabels(), va='top')

lab0=STATS[0]
lab1=STATS[1]
lab2='Forecast lead hrs'
plt.figtext(.5, .98, TITLE, horizontalalignment='center',
            verticalalignment='center', fontsize=22)

plt.figtext(.5, .93, SUBTITLE, horizontalalignment='center',
            verticalalignment='center', fontsize=22)

plt.figtext(.03, .595, lab0, horizontalalignment='right', rotation=90,
            verticalalignment='center', fontsize=22)

plt.figtext(.03, .265, lab1, horizontalalignment='right', rotation=90,
            verticalalignment='center', fontsize=22)

plt.figtext(.5, .01, lab2, horizontalalignment='center',
            verticalalignment='center', fontsize=22)

if line_count <= 3:
    ncols = line_count
else:
    rmdr_3 = line_count % 3
    rmdr_4 = line_count % 4
    if rmdr_3 < rmdr_4:
        ncols = 3
    else:
        ncols = 4

fig.legend(line_list, line_labs, fontsize=18, ncol=ncols, loc='center',
           bbox_to_anchor=[0.5, 0.83])

# save figure and display
os.system('mkdir -p ' + OUT_ROOT)
plt.savefig(OUT_PATH)
plt.show()

##################################################################################
# end
