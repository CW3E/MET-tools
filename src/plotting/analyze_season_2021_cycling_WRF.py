##################################################################################
# Description
##################################################################################
# This is a quick template analysis to demonstrate the type of figures that
# can be put together with these classes.  Value substitution is utilized
# in dictionary definitions used to instantiate classes.
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
##################################################################################
# Imports
##################################################################################
from plotting import *
from heatplots import *
from lineplots import *
from colorbars import *
import ipdb

##################################################################################
# Define script definitions to be used later
##################################################################################
# Define experiment control flows as class instances
WRF_v03_noMHS_CP = control_flow(
    NAME='WRF_v03_noMHS_CP',
    PLT_LAB='WRF v3 noMHS CP',
    GRDS=['d01'],
    MEM_IDS=['ens_00']
    )

WRF_v06_noMHS_CP = control_flow(
    NAME='WRF_v06_noMHS_CP',
    PLT_LAB='WRF v6 noMHS CP',
    GRDS=['d01'],
    MEM_IDS=['ens_00']
    )

WRF_v03_MHS_CP = control_flow(
    NAME='WRF_v03_MHS_CP',
    PLT_LAB='WRF v3 MHS CP',
    GRDS=['d01'],
    MEM_IDS=['ens_00']
    )

WRF_v06_MHS_CP = control_flow(
    NAME='WRF_v06_MHS_CP',
    PLT_LAB='WRF v6 MHS CP',
    GRDS=['d01'],
    MEM_IDS=['ens_00']
    )

WRF_v03_noMHS_MR = control_flow(
    NAME='WRF_v03_noMHS_MR',
    PLT_LAB='WRF v3 noMHS MR',
    GRDS=['d01'],
    MEM_IDS=['ens_00']
    )

WRF_v06_noMHS_MR = control_flow(
    NAME='WRF_v06_noMHS_MR',
    PLT_LAB='WRF v6 noMHS MR',
    GRDS=['d01'],
    MEM_IDS=['ens_00']
    )

WRF_v03_MHS_MR = control_flow(
    NAME='WRF_v03_MHS_MR',
    PLT_LAB='WRF v3 MHS MR',
    GRDS=['d01'],
    MEM_IDS=['ens_00']
    )

WRF_v06_MHS_MR = control_flow(
    NAME='WRF_v06_MHS_MR',
    PLT_LAB='WRF v6 MHS MR',
    GRDS=['d01'],
    MEM_IDS=['ens_00']
    )

# Create a list of control flows for looping line plots
CTR_FLWS = [
            WRF_v03_noMHS_CP,
            WRF_v06_noMHS_CP,
            WRF_v03_MHS_CP,
            WRF_v06_MHS_CP,
            WRF_v03_noMHS_MR,
            WRF_v06_noMHS_MR,
            WRF_v03_MHS_MR,
            WRF_v06_MHS_MR,
           ]

# Define forecast accumulation thresholds
LEVS = ['>=1.0', '>=10.0', '>=25.0', '>=50.0', '>=100.0']

# Define land masks to produce verification diagnostics over
MSKS = ['PNW_NorCal', 'OR_CA']

# Define event forecast start dates range / valid date triplets
DTS = [
       ['2021012300', '2021012700', '2021012800'],
       ['2021012400', '2021012800', '2021012900'],
       ['2021012800', '2021020100', '2021020200'],
      ]

##################################################################################
# Line plot templates (not including substituted arguments)
##################################################################################
lineplot_rmse_corr = {
        'CTR_FLWS': CTR_FLWS,
        'DT_INC': '24',
        'STAT_KEYS': ['RMSE', 'PR_CORR'],
        'STAT0_LIM': None,
        'STAT1_LIM': None,
        'CI': 'NC',
        'MET_TOOL': 'GridStat',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'lineplots',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'LEV': None,
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': False,
        'FIG_LAB': None,
        'IF_SHOW': False,
       }

lineplot_fss_afss = {
        'CTR_FLWS': CTR_FLWS,
        'DT_INC': '24',
        'STAT_KEYS': ['FSS', 'AFSS'],
        'STAT0_LIM': None,
        'STAT1_LIM': None,
        'CI': 'NC',
        'MET_TOOL': 'GridStat',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'lineplots',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': False,
        'FIG_LAB': None,
        'IF_SHOW': False,
       }

##################################################################################
# Run plotting if called as script
##################################################################################
if __name__ == '__main__':
    for MSK in MSKS:
        # lineplots
        for DT in DTS:
            STRT_DT = DT[0]
            STOP_DT = DT[1]
            VALID_DT = DT[2]

            lineplot_rmse_corr['STRT_DT'] = STRT_DT
            lineplot_rmse_corr['STOP_DT'] = STOP_DT
            lineplot_rmse_corr['VALID_DT'] = VALID_DT
            lineplot_rmse_corr['MSK'] = MSK 

            lineplot_fss_afss['STRT_DT'] = STRT_DT
            lineplot_fss_afss['STOP_DT'] = STOP_DT
            lineplot_fss_afss['VALID_DT'] = VALID_DT
            lineplot_fss_afss['MSK'] = MSK 

            dual_lineplot(**lineplot_rmse_corr).gen_fig()
            for LEV in LEVS:
                lineplot_fss_afss['LEV'] = LEV
                dual_lineplot(**lineplot_fss_afss).gen_fig()

