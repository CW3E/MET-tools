##################################################################################
# Description
##################################################################################
# This script is designed to generate heat plots in Matplotlib from MET grid_stat
# output files, preprocessed with the companion script proc_24hr_QPF.py. This
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
from proc_gridstat import OUT_ROOT

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flow to analyze 
CTR_FLW = 'ECMWF'

# define optional gridstat prefix 
PRFX = 'DW_MEAN_3'

# define case-wise sub-directory
CSE = 'DD'

# verification domain for the forecast data
GRD='0.25'

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2022121600'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
END_DT = '2023011800'

# number of hours between zero hours for forecast data (string HH)
CYC_INT = '24'

# first valid time for verification (string YYYYMMDDHH)
ANL_STRT = '2022122600'

# final valid time (string YYYYMMDDHH)
ANL_END = '2023011900'

# cycle interval verification valid times (string HH)
ANL_INT = '24'

# threshold level to plot
#LEV = '>0.0'
#LEV = '>=10.0'
LEV = '>=25.4'
#LEV = '>=50.8'
#LEV = '>=101.6'

# MET stat file type -- should be leveled data
#TYPE = 'nbrcts'
TYPE = 'nbrcnt'

# MET stat column names to be made to heat plots / labels
#STAT = 'FBIAS'
STAT = 'FSS'

# landmask for verification region -- need to be set in earlier preprocessing
LND_MSK = 'CA_Climate_Zone_16_Sierra'
#LND_MSK = 'CALatLonPoints'
#LND_MSK = 'FULL'

# define control flow plotting name
TITLE = STAT + ' - Precip Thresh ' + LEV + ' mm - ' + LND_MSK + ' - ' +\
        CTR_FLW + ' ' + PRFX

##################################################################################
# Begin plotting
##################################################################################
# convert to date times
if len(STRT_DT) != 10:
    print('ERROR: STRT_DT, ' + STRT_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)

if len(END_DT) != 10:
    print('ERROR: END_DT, ' + END_DT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)

if len(CYC_INT) != 2:
    print('ERROR: CYC_INT, ' + CYC_INT + ', is not in HH format.')
    sys.exit(1)
    
if len(ANL_STRT) != 10:
    print('ERROR: ANL_STRT, ' + ANL_STRT + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    s_iso = ANL_STRT[:4] + '-' + ANL_STRT[4:6] + '-' + ANL_STRT[6:8] +\
            '_' + ANL_STRT[8:]
    anl_strt = dt.fromisoformat(s_iso)

if len(ANL_END) != 10:
    print('ERROR: ANL_END, ' + ANL_END + ', is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    e_iso = ANL_END[:4] + '-' + ANL_END[4:6] + '-' + ANL_END[6:8] +\
            '_' + ANL_END[8:]
    anl_end = dt.fromisoformat(e_iso)

if len(ANL_INT) != 2:
    print('ERROR: ANL_INT, ' + ANL_INT + ', is not in HH format.')
    sys.exit(1)
else:
    anl_int = ANL_INT + 'H'
    
# generate the date range for the analyses
anl_dates = pd.date_range(start=anl_strt, end=anl_end,
                          freq=anl_int).to_pydatetime()

# Create a figure
fig = plt.figure(figsize=(11.25,8.63))

# Set the axes
ax0 = fig.add_axes([.92, .18, .03, .77])
ax1 = fig.add_axes([.07, .18, .84, .77])

# define derived data paths 
cse = CSE + '/' + CTR_FLW
data_root = OUT_ROOT + '/' + cse + '/MET_analysis'

# define the output name
in_path = data_root + '/grid_stats_' + PRFX + '_' + GRD + '_' + STRT_DT +\
          '_to_' + END_DT + '.bin'

out_path = data_root + '/' + STRT_DT + '_' + END_DT + '_lev_' + LEV +\
           '_' + LND_MSK + '_' + STAT + '_heatplot.png'

f = open(in_path, 'rb')
data = pickle.load(f)
f.close()

# load the values to be plotted along with landmask, lead and threshold
vals = [
        'VX_MASK',
        'FCST_LEAD',
        'FCST_THRESH',
        'FCST_VALID_END',
       ]
vals += [STAT]

# cut down df to specified region and level of data 
stat_data = data[TYPE][vals]
stat_data = stat_data.loc[(stat_data['FCST_THRESH'] == LEV)]
stat_data = stat_data.loc[(stat_data['VX_MASK'] == LND_MSK)]

# NOTE: sorting below is designed to handle the issue of string sorting with
# symbols and non-left-padded decimals
# sorts first on length of integer expansion for hours, secondly on char
data_leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                    key=lambda x:(len(x), x), reverse=True)
data_dates = []
num_leads = len(data_leads)
num_dates = len(anl_dates)

# create array storage for probs
tmp = np.zeros([num_leads, num_dates])

for i in range(num_leads):
    for j in range(num_dates):
        if i == 0:
            if ( j % 2 ) == 0 or num_dates < 10:
              # on the first loop pack the tick labels
              data_dates.append(anl_dates[j].strftime('%Y%m%d'))
            else:
                data_dates.append('')

        try:
            val = stat_data.loc[(stat_data['FCST_LEAD'] == data_leads[i]) &
                                 (stat_data['FCST_VALID_END'] == anl_dates[j].strftime('%Y%m%d_%H%M%S'))]
            
            tmp[i, j] = val[STAT]
        except:
            tmp[i, j] = np.nan

# define the color bar scale depending on the stat
color_map = sns.cubehelix_palette(20, start=.75, rot=1.50, as_cmap=True,
                                  reverse=True, dark=0.25)

if (STAT == 'GSS') or\
   (STAT == 'BAGSS') or\
   (STAT == 'HK'):
    min_scale = -0.25
    max_scale = 1.0
    sns.heatmap(tmp[:,:], linewidth=0.5, ax=ax1, cbar_ax=ax0, vmin=min_scale,
                vmax=max_scale, cmap=color_map)

elif (STAT == 'FBIAS'):
    scale = tmp[~np.isnan(tmp)]
    alpha = 1
    max_scale, min_scale = np.percentile(scale, [100 - alpha / 2, alpha / 2])
    sns.heatmap(tmp[:,:], linewidth=0.5, ax=ax1, cbar_ax=ax0, vmin=min_scale,
                vmax=max_scale, cmap=color_map, norm=LogNorm())

else:
    max_scale = 1.0
    min_scale = 0.0
    sns.heatmap(tmp[:,:], linewidth=0.5, ax=ax1, cbar_ax=ax0, vmin=min_scale,
                vmax=max_scale, cmap=color_map)

##################################################################################
# define display parameters

# generate tic labels based on hour values
for i in range(num_leads):
    data_leads[i] = data_leads[i][:-4]

ax0.set_yticklabels(ax0.get_yticklabels(), rotation=270, va='top')
ax1.set_xticklabels(data_dates, rotation=45, ha='right')
ax1.set_yticklabels(data_leads)

# tick parameters
ax0.tick_params(
        labelsize=16
        )

ax1.tick_params(
        labelsize=16
        )

lab1='Verification Valid Date'
lab2='Forecast Lead Hrs From Valid Date'
plt.figtext(.5, .02, lab1, horizontalalignment='center',
            verticalalignment='center', fontsize=20)

plt.figtext(.02, .565, lab2, horizontalalignment='center',
            verticalalignment='center', fontsize=20, rotation=90)

plt.figtext(.5, .98, TITLE, horizontalalignment='center',
            verticalalignment='center', fontsize=20)

# save figure and display
plt.savefig(out_path)
plt.show()

##################################################################################
# end
