##################################################################################
# Description
##################################################################################
# This script is designed to generate line plots in Matplotlib from MET grid_stat
# output files, preprocessed with the companion script proc_24hr_QPF.py.  This
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
# Copyright 2022 Colin Grudzien, cgrudzien@ucsd.edu
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
import ipdb

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flows to analyze 
CTR_FLWS = [
            'deterministic_forecast_b0.00',
            'deterministic_forecast_b0.10',
            'deterministic_forecast_b0.20',
            'deterministic_forecast_b0.30',
            'deterministic_forecast_b0.40',
            'deterministic_forecast_b0.50',
            'deterministic_forecast_b0.60',
            'deterministic_forecast_b0.70',
            'deterministic_forecast_b0.80',
            'deterministic_forecast_b0.90',
            'deterministic_forecast_b1.00',
            #'deterministic_forecast_lag00_b0.00_v03_h0300',
            #'deterministic_forecast_lag00_b0.00_v06_h0300',
            #'deterministic_forecast_lag06_b0.00_v03_h0300',
            #'deterministic_forecast_lag06_b0.00_v06_h0300',
            #'deterministic_forecast_lag00_b0.00_v06_h0150',
            #'deterministic_forecast_lag00_b0.00_v06_h0300',
            #'deterministic_forecast_lag00_b0.00_v06_h0450',
            #'deterministic_forecast_lag00_b0.00_v06_h0600',
            #'deterministic_forecast_lag00_b0.00_v06_h0900',
            #'deterministic_forecast_lag00_b0.00',
            #'deterministic_forecast_lag00_b0.10',
            #'deterministic_forecast_lag00_b0.20',
            #'deterministic_forecast_lag00_b0.30',
            #'deterministic_forecast_lag00_b0.40',
            #'deterministic_forecast_lag00_b0.50',
            #'deterministic_forecast_lag00_b0.60',
            #'deterministic_forecast_lag00_b0.70',
            #'deterministic_forecast_lag00_b0.80',
            #'deterministic_forecast_lag00_b0.90',
            #'deterministic_forecast_lag00_b1.00',
            'GFS',
            'ECMWF',
           ]

# define optional list of stats files prefixes, include empty string to ignore
PRFXS = [
        '',
        ]

# fig label for output file organization
FIG_LAB = 'lag00'

# fig case directory
FIG_CSE = 'beta'

# define case-wise sub-directory
CSE = 'CC'

# verification domain for the forecast data
GRD='d02'

# verification domain for the calibration data
REF='0.25'

# starting date and zero hour of forecast cycles
STRT_DT = '2021012400'

# final date and zero hour of data of forecast cycles
END_DT = '2021012700'

# valid date for the verification
VALID_DT = '2021012800'

# MET stat file type -- should be non-leveled data
TYPE = 'cnt'

# MET stat column names to be made to heat plots / labels
STATS = ['RMSE', 'PR_CORR']
#STATS = ['MAD', 'SP_CORR']

# landmask for verification region -- need to be set in earlier preprocessing
#LND_MSK = 'CA_Climate_Zone_16_Sierra'
LND_MSK = 'CALatLonPoints'
#LND_MSK = 'FULL'

# plot title
TITLE='24hr accumulated precip at ' + VALID_DT

# plot sub-title title
SUBTITLE='Verification region -- ' + LND_MSK

# fig root
FIG_ROOT = '/home/cgrudzien/cycle_analysis'

##################################################################################
# Begin plotting
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

# create a figure
fig = plt.figure(figsize=(11.25,8.63))
num_flws = len(CTR_FLWS)
num_pfxs = len(PRFXS)

# Set the axes
ax0 = fig.add_axes([.110, .395, .85, .33])
ax1 = fig.add_axes([.110, .065, .85, .33])

line_list = []
line_labs = []
ax0_l = []
ax1_l = []

# increment line count whenever a configuration is plotted
line_count = -1

for i in range(num_flws):
    # loop on control flows
    ctr_flw = CTR_FLWS[i]

    for m in range(num_pfxs):
        # loop on prefixes
        pfx = PRFXS[m]
        if len(pfx) > 0:
            pfx += '_'
        
        # define derived data paths 
        data_root = OUT_ROOT + '/' + CSE + '/' + ctr_flw + '/MET_analysis'
        stat0 = STATS[0]
        stat1 = STATS[1]
        
        # define the input name
        if ctr_flw == 'ECMWF' or ctr_flw == 'GFS':
            in_path = data_root + '/grid_stats_' + pfx + REF + '_' + STRT_DT +\
                      '_to_' + END_DT + '.bin'

        else:
            in_path = data_root + '/grid_stats_' + pfx + GRD + '_' + STRT_DT +\
                      '_to_' + END_DT + '.bin'
        
        try:
            f = open(in_path, 'rb')
            data = pickle.load(f)
            f.close()

        except:
            print('WARNING: input data ' + in_path +\
                    ' does not exist, skipping this configuration.')
            continue

        split_string = ctr_flw.split('_')
        line_lab = pfx 
        if len(split_string) > 1:
            for i in range(1,1,-1):
                line_lab += split_string[-i] + '_'
            line_lab += split_string[-1] 

        else:
            line_lab += ctr_flw

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
        for k in range(2):
            stat = STATS[k]
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
        data_leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                            key=lambda x:(len(x), x))
        num_leads = len(data_leads)
        
        # create array storage for stats and plot
        for k in range(2):
            exec('ax = ax%s'%k)
            if cnf_lvs[k]:
                tmp = np.zeros([num_leads, 3])
        
                for j in range(num_leads):
                    val = stat_data.loc[(stat_data['FCST_LEAD'] == data_leads[j])]
                    tmp[j, 0] = val[STATS[k]]
                    tmp[j, 1] = val[STATS[k] + cnf_lvs[k] + 'L']
                    tmp[j, 2] = val[STATS[k] + cnf_lvs[k] + 'U']
                
                l0 = ax.fill_between(range(num_leads), tmp[:, 1], tmp[:, 2], alpha=0.5)
                l1, = ax.plot(range(num_leads), tmp[:, 0], linewidth=2)
                exec('ax%s_l.append([l1,l0])'%k)
                l = l1

            else:
                tmp = np.zeros([num_leads])
            
                for j in range(num_leads):
                    val = stat_data.loc[(stat_data['FCST_LEAD'] == data_leads[j])]
                    tmp[j] = val[STATS[k]]
                
                l, = ax.plot(range(num_leads), tmp[:], linewidth=2)
                exec('ax%s_l.append([l])'%k)

        # add the line type to the legend
        line_list.append(l)


# set colors and markers
line_colors = sns.color_palette("husl", line_count + 1)
for i in range(len(ax0_l)):
    ax = ax0_l[i]
    for j in range(len(ax)):
        l = ax[j]
        l.set_color(line_colors[i])
        if j == 0:
          l.set_marker((i + 2, 0, 0))
          l.set_markersize(18)

for i in range(len(ax1_l)):
    ax = ax1_l[i]
    for j in range(len(ax)):
        l = ax[j]
        l.set_color(line_colors[i])
        if j == 0:
          l.set_marker((i + 2, 0, 0))
          l.set_markersize(18)

##################################################################################
# define display parameters

# generate tic labels based on hour values
for i in range(num_leads):
    data_leads[i] = data_leads[i][:-4]

ax1.set_xticks(range(num_leads))
ax1.set_xticklabels(data_leads)

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

#ax0.set_ylim([10, 30])
#ax1.set_ylim([.6,1.0])

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

fig.legend(line_list, line_labs, fontsize=18, ncol=min(num_flws * num_pfxs, 5),
           loc='center', bbox_to_anchor=[0.5, 0.83])

# save figure and display
out_dir = FIG_ROOT + '/' + CSE + '/' + FIG_CSE
os.system('mkdir -p ' + out_dir)
out_path = out_dir + '/' + VALID_DT + '_' +\
           LND_MSK + '_' + stat0 + '_' +\
           stat1 + '_' + FIG_LAB + '_lineplot.png'
    
plt.savefig(out_path)
plt.show()

##################################################################################
# end
