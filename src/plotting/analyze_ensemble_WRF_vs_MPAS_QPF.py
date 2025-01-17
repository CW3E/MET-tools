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

##################################################################################
# Define script definitions to be used later
##################################################################################
# Define experiment control flows as class instances
MPAS_60_3_WestCoast = control_flow(
    NAME='MPAS_60-3_WestCoast',
    PLT_LAB='MPAS 60-3km',
    GRDS=None,
    MEM_IDS=['mean']
    )

MPAS_60_10_CONUS = control_flow(
    NAME='MPAS_60-10_CONUS',
    PLT_LAB='MPAS 60-10km',
    GRDS=None,
    MEM_IDS=['mean']
    )

WRF_9_3_WestCoast = control_flow(
    NAME='WRF_9-3_WestCoast',
    PLT_LAB='WRF 9-3km',
    GRDS=['d01', 'd02'],
    MEM_IDS=['mean']
    )

ECMWF = control_flow(
    NAME='ECMWF',
    PLT_LAB='ECMWF',
    GRDS=None,
    MEM_IDS=None,
    )

GFS = control_flow(
    NAME='GFS',
    PLT_LAB='GFS',
    GRDS=None,
    MEM_IDS=None,
    )

GEFS = control_flow(
    NAME='GEFS',
    PLT_LAB='GEFS',
    GRDS=None,
    MEM_IDS=None,
    )

# Create a list of control flows for looping line plots
CTR_FLWS = [
             MPAS_60_3_WestCoast,
             MPAS_60_10_CONUS,
             WRF_9_3_WestCoast,
             ECMWF,
             GFS,
             GEFS,
           ]

# Define forecast accumulation thresholds
LEVS = ['>=1.0', '>=10.0', '>=25.0', '>=50.0', '>=100.0']

# Define land masks to produce verification diagnostics over
MSKS = [
        #'OR_All',
        #'WA_All',
        #'WA_OR',
        'OR_CA',
        #'PNW_NorCal',
        #'CA_All',
       ]

# Define event forecast start dates range / valid date triplets
DTS = [
       #['2021012300', '2021012700', '2021012800'],
       #['2021012400', '2021012800', '2021012900'],
       #['2022022300', '2022022700', '2022022800'],
       #['2022022400', '2022022800', '2022030100'],
       #['2022022500', '2022030100', '2022030200'],
       #['2022122300', '2022122700', '2022122800'],
       ['2022122600', '2022123000', '2022123100'],
       ['2022122700', '2022123100', '2023010100'],
       #['2023010600', '2023011000', '2023011100'],
       #['2023031000', '2023031400', '2023031500'],
      ]

# Define relative differene plots analysis / reference control flow pairs
DIFFS = [
         [MPAS_60_10_CONUS, WRF_9_3_WestCoast], # MPAS 10km versus WWRF
         [MPAS_60_3_WestCoast, WRF_9_3_WestCoast], # MPAS 3km versus WWRF
        ]

##################################################################################
# Define colorbars from template classes
##################################################################################
relative_diff_cb = explicit_discrete(**EXPLICIT_DISCRETE_MAPS['relative_diff'])
normalized_cb = explicit_discrete(**EXPLICIT_DISCRETE_MAPS['normalized_skillful'])

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
        'CSE': 'valid_date_2023-01-01T00',
        'FIG_CSE': 'lineplots',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'LEV': None,
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': True,
        'FIG_LAB': None,
        'IF_SHOW': False,
       }

##################################################################################
# Relative diff stat heatplot templates
##################################################################################
heatplot_multilevel_multilead_fss_relative_diff = {
        'DT_INC': '24',
        'STAT_KEY': 'FSS',
        'ANL_GRD_KEY': None,
        'ANL_MEM_KEY': 'mean',
        'REF_MEM_KEY': 'mean',
        'COLORBAR': relative_diff_cb,
        'MET_TOOL': 'GridStat',
        'CSE': 'valid_date_2023-01-01T00',
        'FIG_CSE': 'relative_diff_multilevel_multilead',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': True,
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
            dual_lineplot(**lineplot_rmse_corr).gen_fig()

        # loop WRF reference domain
        for GRD in ['d01', 'd02']:
            # relative diff heat plots
            for DIFF in DIFFS:
                ANL = DIFF[0]
                REF = DIFF[1]

                heatplot_multilevel_multilead_fss_relative_diff['ANL_CTR_FLW'] = ANL
                heatplot_multilevel_multilead_fss_relative_diff['REF_CTR_FLW'] = REF
                heatplot_multilevel_multilead_fss_relative_diff['MSK'] = MSK 
                heatplot_multilevel_multilead_fss_relative_diff['REF_GRD_KEY'] = GRD 

                for DT in DTS:
                    STRT_DT = DT[0]
                    STOP_DT = DT[1]
                    VALID_DT = DT[2]

                    heatplot_multilevel_multilead_fss_relative_diff['STRT_DT'] = STRT_DT
                    heatplot_multilevel_multilead_fss_relative_diff['STOP_DT'] = STOP_DT
                    heatplot_multilevel_multilead_fss_relative_diff['VALID_DT'] = VALID_DT
                    
                    multilevel_multilead_relative_diff(**heatplot_multilevel_multilead_fss_relative_diff).gen_fig()
