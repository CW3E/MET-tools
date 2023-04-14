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
import pickle
import os
from proc_gridstat import OUT_ROOT

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flows to analyze 
CTR_FLWS = [
            'NRT_gfs',
            'NRT_ecmwf',
            'GFS',
            'ECMWF',
           ]

# Define the max number of underscore components of control flow names to include in
# fig legend. This includes components of the strings above from last to first. Set to
# number of underscore separated compenents in the string to obtain the full
# name as the legend label. Note: a non-empty prefix value below will always be
# included in the legend label
LAB_LEN = 2

# define if legend label includes grid
GRD_LAB = True

# define optional list of stats files prefixes, include empty string to ignore
PRFXS = [
        '',
        ]

# fig label for output file organization, included in figure file name
FIG_LAB = ''

# fig case directory, includes leading '/', leave as empty string if not needed
FIG_CSE = ''

# verification domains for the forecast data
GRDS = [
        'd01',
        'd02',
        'd03',
        '0.25',
       ]

# starting date and zero hour of forecast cycles
STRT_DT = '2022121400'

# final date and zero hour of data of forecast cycles
END_DT = '2023011800'

# valid date for the verification
VALID_DT = '2023010100'

# MET stat file type - should be non-leveled data
TYPE = 'cnt'

# MET stat column names to be made to heat plots / labels
STATS = ['RMSE', 'PR_CORR']

# landmask for verification region
LND_MSK = 'CALatLonPoints'

# plot title
TITLE='24hr accumulated precip at ' + VALID_DT[:4] + '-' + VALID_DT[4:6] + '-' +\
        VALID_DT[6:8] + '_' + VALID_DT[8:]

# plot sub-title title
SUBTITLE='Verification region - ' + LND_MSK

# fig saved automatically to OUT_PATH
OUT_DIR = OUT_ROOT + '/figures' + FIG_CSE
OUT_PATH = OUT_DIR + '/' + VALID_DT + '_' + LND_MSK + '_' + STATS[0] + '_' +\
           STATS[1] + '_' + FIG_LAB + '_lineplot.png'

##################################################################################
# Make data checks and determine all lead times over all files
##################################################################################
if len(STRT_DT) != 10:
    print('ERROR: STRT_DT, ' + STRT_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)

if len(END_DT) != 10:
    print('ERROR: END_DT, ' + END_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)

if len(VALID_DT) != 10:
    print('ERROR: VALID_DT, ' + VALID_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    v_iso = VALID_DT[:4] + '-' + VALID_DT[4:6] + '-' + VALID_DT[6:8] +\
            '_' + VALID_DT[8:]
    valid_dt = dt.fromisoformat(v_iso)

fcst_leads = []
for ctr_flw in CTR_FLWS:
    for prfx in PRFXS:
        if len(prfx) > 0:
            pfx = prfx + '_'
        else:
            pfx = ''
        
        # define derived data paths 
        data_root = OUT_ROOT + '/' + ctr_flw
        stat0 = STATS[0]
        stat1 = STATS[1]
        
        for grd in GRDS:
            # define the input name
            in_path = data_root + '/grid_stats_' + pfx + grd + '_' + STRT_DT +\
                      '_to_' + END_DT + '.bin'
            
            try:
                with open(in_path, 'rb') as f:
                    data = pickle.load(f)

            except:
                print('WARNING: input data ' + in_path +\
                        ' does not exist, skipping this configuration.')
                continue

            # load the values to be plotted along with landmask and lead
            vals = [
                    'VX_MASK',
                    'FCST_LEAD',
                    'FCST_VALID_END',
                   ]
            vals += STATS
            
            # cut down df to specified valid date / region and obtain leads of data 
            stat_data = data[TYPE][vals]
            stat_data = stat_data.loc[(stat_data['VX_MASK'] == LND_MSK)]
            stat_data = stat_data.loc[(stat_data['FCST_VALID_END'] ==
                                       valid_dt.strftime('%Y%m%d_%H%M%S'))]
            leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                           key=lambda x:(len(x), x))

            fcst_leads += leads

# find all unique values for forecast leads, sorted for plotting
fcst_leads = sorted(list(set(fcst_leads)), key=lambda x:(len(x), x))
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

# increment line count whenever a configuration is plotted
line_count = 0

for ctr_flw in CTR_FLWS:
    for prfx in PRFXS:
        if len(prfx) > 0:
            pfx = prfx + '_'
        else:
            pfx = ''
        
        # define derived data paths 
        data_root = OUT_ROOT + '/' + ctr_flw
        stat0 = STATS[0]
        stat1 = STATS[1]
        
        for grd in GRDS:
            # define the input name
            in_path = data_root + '/grid_stats_' + pfx + grd + '_' + STRT_DT +\
                      '_to_' + END_DT + '.bin'
            
            try:
                with open(in_path, 'rb') as f:
                    data = pickle.load(f)

            except:
                continue

            split_string = ctr_flw.split('_')
            split_len = len(split_string)
            line_lab = pfx 
            lab_len = min(LAB_LEN, split_len)
            if lab_len > 1:
                for i_ll in range(split_len - lab_len, -1, -1):
                    line_lab += split_string[-i_ll] + '_'

            line_lab += split_string[-1] 
            if GRD_LAB:
                line_lab += '_' + grd

            line_labs.append(line_lab)
            line_count += 1
            
            # load the values to be plotted along with landmask and lead
            vals = [
                    'VX_MASK',
                    'FCST_LEAD',
                    'FCST_VALID_END',
                   ]
            vals += STATS
            
            # infer existence of confidence intervals with precedence for bootstrap
            cnf_lvs = []
            for i_ns in range(2):
                stat = STATS[i_ns]
                if stat + '_BCL' in data[TYPE] and\
                    not (data[TYPE][stat + '_BCL'].isnull().values.any()):
                        vals.append(stat + '_BCL')
                        vals.append(stat + '_BCU')
                        cnf_lvs.append('_BC')

                elif stat + '_NCL' in data[TYPE] and\
                    not (data[TYPE][stat + '_NCL'].isnull().values.any()):
                        vals.append(stat + '_NCL')
                        vals.append(stat + '_NCU')
                        cnf_lvs.append('_NC')

                else:
                    cnf_lvs.append(False)

            # cut down df to specified valid date / region and obtain leads of data 
            stat_data = data[TYPE][vals]
            stat_data = stat_data.loc[(stat_data['VX_MASK'] == LND_MSK)]
            stat_data = stat_data.loc[(stat_data['FCST_VALID_END'] ==
                                       valid_dt.strftime('%Y%m%d_%H%M%S'))]
            
            # create array storage for stats and plot
            for i_ns in range(2):
                exec('ax = ax%s'%i_ns)
                if cnf_lvs[i_ns]:
                    tmp = np.empty([num_leads, 3])
                    tmp[:] = np.nan
            
                    for i_nl in range(num_leads):
                        val = stat_data.loc[(stat_data['FCST_LEAD'] == fcst_leads[i_nl])]
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
                        val = stat_data.loc[(stat_data['FCST_LEAD'] == fcst_leads[i_nl])]
                        if not val.empty:
                            tmp[i_nl] = val[STATS[i_ns]]
                    
                    l, = ax.plot(range(num_leads), tmp[:], linewidth=2)
                    exec('ax%s_l.append([l])'%i_ns)

            # add the line type to the legend
            line_list.append(l)

# set colors and markers
line_colors = sns.color_palette("husl", line_count)
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
