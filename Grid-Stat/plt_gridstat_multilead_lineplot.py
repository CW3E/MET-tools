##################################################################################
# Description
##################################################################################
# This script is designed to generate line plots in Matplotlib from MET grid_stat
# output files, preprocessed with the companion script proc_gridstat.py.  This
# plotting scheme is designed to plot non-threshold data as lines in the vertical
# axis and the number of lead hours to the valid time for verification from the
# forecast initialization in the horizontal axis. The global parameters for the
# script below control the initial times for the forecast initializations, as
# well as the valid date of the verification. Stats to compare can be reset in
# the global parameters with heat map color bar changing scale dynamically.
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
import ipdb

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flows to analyze 
CTR_FLWS = [
            #'NAM_lag06_b0.00_v01_h0300', 
            #'NAM_lag06_b0.00_v02_h0300',
            'NAM_lag06_b0.00_v03_h0300',
            #'NAM_lag06_b0.00_v04_h0300',
            #'NAM_lag06_b0.00_v05_h0300',
            #'NAM_lag06_b0.00_v06_h0300',
            #'RAP_lag06_b0.00_v01_h0300',
            #'RAP_lag06_b0.00_v02_h0300',
            #'RAP_lag06_b0.00_v03_h0300',
            #'RAP_lag06_b0.00_v04_h0300',
            #'RAP_lag06_b0.00_v05_h0300',
            'RAP_lag06_b0.00_v06_h0300',
            'ECMWF',
            'GFS',
           ]

# Define a list of indices for underscore-separated components of control flow
# names to include in fig legend. Note: a non-empty prefix value below will
# always be included in the legend label, and control flows with fewer components
# than indices above will only include those label components that exist
LAB_IDX = [0, 3]

# define if legend label includes grid
GRD_LAB = False

# define optional list of stats files prefixes, include empty string to ignore
PRFXS = [
        '',
        ]

# fig label for output file organization, included in figure file name
FIG_LAB = ''

# fig case directory, includes leading '/', leave as empty string if not needed
FIG_CSE = '/Skillful'

# verification domains for the forecast data
GRDS = [
        '',
       ]

# Minimum starting date and zero hour of forecast cycles
FCST_STRT = '2020020200'

# Maximium starting date and zero hour of data of forecast cycles
FCST_END = '2020020600'

# number of hours between zero hours for forecast data (string HH)
CYC_INT = '24'

# valid date for the verification
ANL_DT = '2020020700'

# Max forecast lead to plot in hours
MAX_LD = '120'

# MET stat file type - should be non-leveled data
TYPE = 'cnt'

# MET stat column names to be made to heat plots / labels
STATS = ['RMSE', 'PR_CORR']

# landmask for verification region
LND_MSK = 'WA_OR'

# plot title
TITLE='24hr accumulated precip at ' + ANL_DT[:4] + '-' + ANL_DT[4:6] + '-' +\
        ANL_DT[6:8] + '_' + ANL_DT[8:]

# plot sub-title title
SUBTITLE='Verification region -'
lnd_msk_split = LND_MSK.split('_')
for split in lnd_msk_split:
    SUBTITLE += ' ' + split

# fig saved automatically to OUT_PATH
if len(FIG_LAB) > 0:
    fig_lab = '_' + FIG_LAB
else:
    fig_lab = ''

OUT_DIR = OUT_ROOT + '/figures' + FIG_CSE
OUT_PATH = OUT_DIR + '/' + ANL_DT + '_' + LND_MSK + '_' + STATS[0] + '_' +\
           STATS[1] + fig_lab + '_lineplot.png'

##################################################################################
# Make data checks and determine all lead times over all files
##################################################################################
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

if len(ANL_DT) != 10:
    print('ERROR: ANL_DT, ' + ANL_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    anl_dt = dt.fromisoformat(ANL_DT[:4] + '-' + ANL_DT[4:6] + '-' + ANL_DT[6:8] +
            '_' + ANL_DT[8:])

if len(CYC_INT) != 2:
    print('ERROR: CYC_INT, ' + CYC_INT + ', is not in HH format.')
    sys.exit(1)
else:
    cyc_int = CYC_INT + 'H'

# generate the date range and forecast leads for the analysis, parse binary files
# for relevant fields
plt_data = {}
fcst_zhs = pd.date_range(start=fcst_strt, end=fcst_end, freq=cyc_int).to_pydatetime()

fcst_leads = []
for ctr_flw in CTR_FLWS:
    # define derived data paths 
    data_root = OUT_ROOT + '/' + ctr_flw

    for prfx in PRFXS:
        if len(prfx) > 0:
            pfx = '_' + prfx
        else:
            pfx = ''
        
        for grid in GRDS:
            if len(grid) > 0:
                grd = '_' + grid
            else:
                grd = ''

            key = ctr_flw + pfx + grd
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
                stat_data = stat_data.loc[(stat_data['VX_MASK'] == LND_MSK)]
                stat_data = stat_data.loc[(stat_data['FCST_VALID_END'] ==
                                           anl_dt.strftime('%Y%m%d_%H%M%S'))]

                # check if there is data for this configuration and these fields
                if not stat_data.empty:
                    leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                                   key=lambda x:(len(x), x))
    
                    if key in plt_data.keys():
                        # if there is existing data, concatenate dataframes
                        plt_data[key] = pd.concat([plt_data[key], stat_data],
                                                   axis=0)
                    else:
                        # if this is a first instance, create fields
                        plt_data[key] = stat_data

                    # obtain leads of data 
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

num_leads = len(fcst_leads)

##################################################################################
# Begin plotting
##################################################################################
# create a figure
fig = plt.figure(figsize=(12,9.6))

# Set the axes
ax0 = fig.add_axes([.110, .395, .85, .33])
ax1 = fig.add_axes([.110, .065, .85, .33])

line_list = []
line_labs = []
ax0_l = []
ax1_l = []

stat0 = STATS[0]
stat1 = STATS[1]

# loop configurations, load trimmed data from plt_data dictionary
for ctr_flw in CTR_FLWS:
    for prfx in PRFXS:
        if len(prfx) > 0:
            pfx = '_' + prfx
        else:
            pfx = ''

        for grid in GRDS:
            if len(grid) > 0:
                grd = '_' + grid
            else:
                grd = ''
            
            key = ctr_flw + pfx + grd 
            try:
                data = plt_data[key]
    
            except:
                continue
            
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

            if pfx:
                line_lab += pfx
    
            if GRD_LAB:
                    line_lab += grd

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
os.system('mkdir -p ' + OUT_DIR)
plt.savefig(OUT_PATH)
plt.show()

##################################################################################
# end
