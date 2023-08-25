##################################################################################
# Description
##################################################################################
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
import sys
import os
import numpy as np
import pandas as pd
import pickle
import copy
import matplotlib
# use this setting on COMET / Skyriver for x forwarding
import matplotlib.pyplot as plt

##################################################################################
# Set Parameters
##################################################################################
STR_INDT = '    '

CTR = 'RS'
TRT = 'S'

# case studies
CSES = [
        'VD',
        'CL',
        'CC',
        'PNW22',
       ]

# land masks for verification in 1-1 order with case studies above
MSKS = [
        'CA_All',
        'WA_OR',
        'CA_All',
        'WA_OR',
       ]

FLWS = [
        'NAM',
        'RAP',
       ]

# define the file name based on the verification settings
FNAME = 'concat_df_'
for cse in CSES:
    FNAME += cse + '_'


for flw in FLWS:
    FNAME += flw + '_' + CTR + '_' + flw + '_' + TRT + '_'
    
FNAME = FNAME[:-1] + '.bin'

TYPES = [
         'cnt',
         'nbrcnt',
        ]

STATS_0 = [
           'RMSE',
           'PR_CORR',
          ]

STATS_1 = [
           'FSS',
           'AFSS',
          ]

FCST_LEADS = [
              '240000',
              '480000',
              '720000',
              '960000',
             ]

FCST_THRESH = '>=25.0'


##################################################################################
# Process data
##################################################################################

with open(FNAME, 'rb') as f:
    tmp = pickle.load(f)

# extract the stats from the saved dictionary
types = []
for typ in TYPES:
    types.append(tmp[typ])

# find lengths for looping
N_cses = len(CSES)
N_flws = len(FLWS)
N_leds = len(FCST_LEADS)
N_types = len(TYPES)

all_deltas = []

for i_ty in range(N_types):
    # loop gridstat types
    typ = types[i_ty]
    exec('stats = STATS_%s'%i_ty)
    N_stats = len(stats)

    for i_st in range(N_stats):
        # process statistics within gridstat type
        STAT = stats[i_st]
        print('Processing statistic: ' + STAT)

        # create storage for deltas versus leads
        deltas = []

        for i_ld in range(N_leds):
            # loop on forecast leads
            lead = FCST_LEADS[i_ld]
            print(STR_INDT + 'Processing lead time: ' + lead)

            lead_idx = np.array(typ['FCST_LEAD'] == lead)

            # create storage for the stat differences for given lead
            stat_delta = np.empty([N_cses, N_flws])

            for i_cs in range(N_cses):
                # loop on case studies
                cse = CSES[i_cs]
                msk = MSKS[i_cs]
                print(STR_INDT * 2 + 'Processing case study: ' + cse)
                print(STR_INDT * 2 + 'Case study landmask is defined: ' +  msk)

                cse_idx = np.array(typ['CASE'] == cse)
                for i_fl in range(N_flws):
                    # loop on control flows
                    flw = FLWS[i_fl]
                    print(STR_INDT * 3 + 'Processing control flow: ' + flw)
                    msk_idx = np.array(typ['VX_MASK'] == msk)

                    # create a flow index for the treatment
                    flw_idx = np.array(typ['CTR_FLW'] == flw + '_' + TRT)
                    TREAT = typ.loc[cse_idx * flw_idx * msk_idx * lead_idx]
                    TREAT = TREAT[STAT].values[0]
    
                    # create a flow index for the control
                    flw_idx = np.array(typ['CTR_FLW'] == flw + '_' + CTR)
                    CNTRL = typ.loc[cse_idx * flw_idx * msk_idx * lead_idx]
                    CNTRL = CNTRL[STAT].values[0]
    
                    stat_delta[i_cs, i_fl] = TREAT - CNTRL

            # flatten all statistics for box plots versus lead hour
            deltas.append(stat_delta[:, :].flatten())

        # reshape for plotting
        all_deltas.append(np.array(deltas).transpose())

fcst_leads = []
for i_ld in range(N_leds):
    fcst_leads.append(FCST_LEADS[i_ld][:-4])

# create a figure
fig = plt.figure(figsize=(12,9.6))

# Set the axes
ax0 = fig.add_axes([.110, .750, .85, .23])
ax1 = fig.add_axes([.110, .520, .85, .23])
ax2 = fig.add_axes([.110, .290, .85, .23])
ax3 = fig.add_axes([.110, .060, .85, .23])
for i_d in range(len(all_deltas)):
    exec('ax%s.boxplot(all_deltas[%s], showmeans=True)'%(i_d,i_d))
    exec('ax%s.axhline(0.0, color=\'#808080\', linestyle=\'--\')'%i_d)


ax3.set_xticks(range(1,N_leds+1))
ax3.set_xticklabels(fcst_leads)

# tick parameters
ax3.tick_params(
        labelsize=18
        )

ax0.tick_params(
        labelsize=18,
        bottom=False,
        labelbottom=False,
        right=False,
        labelright=False,
        )

ax1.tick_params(
        labelsize=18,
        bottom=False,
        labelbottom=False,
        right=False,
        labelright=False,
        )

ax2.tick_params(
        labelsize=18,
        bottom=False,
        labelbottom=False,
        right=False,
        labelright=False,
        )

lab0='Forecast lead hrs'
lab1='RMSE'
lab2='PR_CORR'
lab3='FSS'
lab4='AFSS'

plt.figtext(.03, .865, lab1, horizontalalignment='center', rotation=90,
            verticalalignment='center', fontsize=22)

plt.figtext(.03, .635, lab2, horizontalalignment='center', rotation=90,
            verticalalignment='center', fontsize=22)

plt.figtext(.03, .405, lab3, horizontalalignment='right', rotation=90,
            verticalalignment='center', fontsize=22)

plt.figtext(.03, .175, lab4, horizontalalignment='right', rotation=90,
            verticalalignment='center', fontsize=22)

plt.figtext(.5, .01, lab0, horizontalalignment='center',
            verticalalignment='center', fontsize=22)

plt.show()
