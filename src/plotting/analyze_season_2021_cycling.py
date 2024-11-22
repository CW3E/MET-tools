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
MPAS_JEDI_60km_ARO_MHS = control_flow(
    NAME='MPAS-JEDI_60km_ARO_MHS',
    PLT_LAB='MPAS 60km ARO MHS',
    GRDS=None,
    MEM_IDS=['ens_00']
    )

MPAS_JEDI_60km_noARO_MHS = control_flow(
    NAME='MPAS-JEDI_60km_noARO_MHS',
    PLT_LAB='MPAS 60km MHS',
    GRDS=None,
    MEM_IDS=['ens_00']
    )

MPAS_JEDI_60km_ARO_noMHS = control_flow(
    NAME='MPAS-JEDI_60km_ARO_noMHS',
    PLT_LAB='MPAS 60km ARO',
    GRDS=None,
    MEM_IDS=['ens_00']
    )

MPAS_JEDI_60km_noARO_noMHS = control_flow(
    NAME='MPAS-JEDI_60km_noARO_noMHS',
    PLT_LAB='MPAS 60km',
    GRDS=None,
    MEM_IDS=['ens_00']
    )

# Create a list of control flows for looping line plots
CTR_FLWS = [
            MPAS_JEDI_60km_noARO_noMHS,
            MPAS_JEDI_60km_ARO_noMHS,
            MPAS_JEDI_60km_noARO_MHS,
            MPAS_JEDI_60km_ARO_MHS,
           ]

# Define forecast accumulation thresholds
LEVS = ['>=1.0', '>=10.0', '>=25.0', '>=50.0', '>=100.0']

# Define event forecast start dates range / valid date triplets
DTS = [
       ['2021011900', '2021012000', '2021012100'],
       ['2021012300', '2021012700', '2021012800'],
       ['2021012400', '2021012800', '2021012900'],
       ['2021012700', '2021013100', '2021020100'],
       ['2021012800', '2021020100', '2021020200'],
       ['2021012900', '2021020200', '2021020300'],
      ]

# Define relative differene plots analysis / reference control flow pairs
DIFFS = [
         [MPAS_JEDI_60km_ARO_noMHS, MPAS_JEDI_60km_noARO_noMHS], # no MHS +/- ARO
         [MPAS_JEDI_60km_ARO_MHS, MPAS_JEDI_60km_noARO_MHS],     # MHS +/- ARO
         [MPAS_JEDI_60km_noARO_MHS, MPAS_JEDI_60km_noARO_noMHS], # no ARO +/- MHS
         [MPAS_JEDI_60km_ARO_MHS, MPAS_JEDI_60km_ARO_noMHS],     # ARO +/- MHS
        ]

##################################################################################
# Define colorbars from template classes
##################################################################################
relative_diff_cb = explicit_discrete(**EXPLICIT_DISCRETE_MAPS['relative_diff'])
normalized_cb = explicit_discrete(**EXPLICIT_DISCRETE_MAPS['normalized_skillful'])
high_rmse_cb = explicit_discrete(**EXPLICIT_DISCRETE_MAPS['high_rmse'])

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
        'MSK': 'CA_All',
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
        'MSK': 'CA_All',
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
# Raw stat heatplot templates
##################################################################################

heatplot_multidate_rmse = {
        'VRF_STRT': '2021012100',
        'VRF_STOP': '2021020300',
        'DT_INC': '24',
        'STAT_KEY': 'RMSE',
        'GRD_KEY': None,
        'MEM_KEY': 'ens_00',
        'MIN_LD': 24,
        'MAX_LD': 120,
        'LD_INC': 24,
        'DT_FMT': '%Y-%m-%d',
        'COLORBAR': high_rmse_cb,
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'multidate_multilead_heatplots',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'LEV': None,
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': False,
        'FIG_LAB': None,
        'IF_SHOW': False,
        }

heatplot_multidate_fss = {
        'VRF_STRT': '2021012100',
        'VRF_STOP': '2021020300',
        'DT_INC': '24',
        'STAT_KEY': 'FSS',
        'GRD_KEY': None,
        'MEM_KEY': 'ens_00',
        'MIN_LD': 24,
        'MAX_LD': 120,
        'LD_INC': 24,
        'DT_FMT': '%Y-%m-%d',
        'COLORBAR': normalized_cb,
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'multidate_multilead_heatplots',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': False,
        'FIG_LAB': None,
        'IF_SHOW': False,
        }

heatplot_multilevel_multilead_fss = {
        'DT_INC': '24',
        'STAT_KEY': 'FSS',
        'GRD_KEY': None,
        'MEM_KEY': 'ens_00',
        'COLORBAR': normalized_cb,
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'all_level_multilead_heatplots',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': False,
        'FIG_LAB': None,
        'IF_SHOW': False,
        }

##################################################################################
# Relative diff stat heatplot templates
##################################################################################
heatplot_multidate_rmse_relative_diff = {
        'VRF_STRT': '2021012100',
        'VRF_STOP': '2021020300',
        'DT_INC': '24',
        'STAT_KEY': 'RMSE',
        'ANL_GRD_KEY': None,
        'ANL_MEM_KEY': 'ens_00',
        'REF_GRD_KEY': None,
        'REF_MEM_KEY': 'ens_00',
        'MIN_LD': 24,
        'MAX_LD': 120,
        'LD_INC': 24,
        'DT_FMT': '%Y-%m-%d',
        'COLORBAR': relative_diff_cb,
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'relative_diff_multidate_multilead_plots',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'LEV': None,
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': False,
        'FIG_LAB': None,
        'IF_SHOW': False,
        }

heatplot_multidate_fss_relative_diff = {
        'VRF_STRT': '2021012100',
        'VRF_STOP': '2021020300',
        'DT_INC': '24',
        'STAT_KEY': 'FSS',
        'ANL_GRD_KEY': None,
        'ANL_MEM_KEY': 'ens_00',
        'REF_GRD_KEY': None,
        'REF_MEM_KEY': 'ens_00',
        'MIN_LD': 24,
        'MAX_LD': 120,
        'LD_INC': 24,
        'DT_FMT': '%Y-%m-%d',
        'COLORBAR': relative_diff_cb,
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'relative_diff_multidate_multilead_plots',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': False,
        'FIG_LAB': None,
        'IF_SHOW': False,
        }

heatplot_fixedlead_fss_relative_diff = {
        'VRF_STRT': '2021012100',
        'VRF_STOP': '2021020300',
        'DT_INC': '24',
        'STAT_KEY': 'FSS',
        'ANL_GRD_KEY': None,
        'ANL_MEM_KEY': 'ens_00',
        'REF_GRD_KEY': None,
        'REF_MEM_KEY': 'ens_00',
        'FCST_LD': 24,
        'DT_FMT': '%Y-%m-%d',
        'COLORBAR': relative_diff_cb,
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'relative_diff_multidate_fixedlead',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': False,
        'FIG_LAB': None,
        'IF_SHOW': False,
        }

heatplot_multilevel_multilead_fss_relative_diff = {
        'DT_INC': '24',
        'STAT_KEY': 'FSS',
        'ANL_GRD_KEY': None,
        'ANL_MEM_KEY': 'ens_00',
        'REF_GRD_KEY': None,
        'REF_MEM_KEY': 'ens_00',
        'COLORBAR': relative_diff_cb,
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'season_2021_cycling',
        'FIG_CSE': 'relative_diff_multilevel_multilead',
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
    # lineplots
    for DT in DTS:
        STRT_DT = DT[0]
        STOP_DT = DT[1]
        VALID_DT = DT[2]

        lineplot_rmse_corr['STRT_DT'] = STRT_DT
        lineplot_rmse_corr['STOP_DT'] = STOP_DT
        lineplot_rmse_corr['VALID_DT'] = VALID_DT

        lineplot_fss_afss['STRT_DT'] = STRT_DT
        lineplot_fss_afss['STOP_DT'] = STOP_DT
        lineplot_fss_afss['VALID_DT'] = VALID_DT

        dual_lineplot(**lineplot_rmse_corr).gen_fig()
        for LEV in LEVS:
            lineplot_fss_afss['LEV'] = LEV
            dual_lineplot(**lineplot_fss_afss).gen_fig()

    # raw stat heat plots
    for CTR_FLW in CTR_FLWS:
        heatplot_multidate_rmse['CTR_FLW'] = CTR_FLW
        heatplot_multidate_fss['CTR_FLW'] = CTR_FLW
        multidate_multilead(**heatplot_multidate_rmse).gen_fig()
        for LEV in LEVS:
            heatplot_multidate_fss['LEV'] = LEV
            multidate_multilead(**heatplot_multidate_fss).gen_fig()

        for DT in DTS:
            STRT_DT = DT[0]
            STOP_DT = DT[1]
            VALID_DT = DT[2]

            heatplot_multilevel_multilead_fss['CTR_FLW'] = CTR_FLW
            heatplot_multilevel_multilead_fss['STRT_DT'] = STRT_DT
            heatplot_multilevel_multilead_fss['STOP_DT'] = STOP_DT
            heatplot_multilevel_multilead_fss['VALID_DT'] = VALID_DT
            multilevel_multilead(**heatplot_multilevel_multilead_fss).gen_fig()

    # relative diff heat plots
    for DIFF in DIFFS:
        ANL = DIFF[0]
        REF = DIFF[1]

        heatplot_multidate_rmse_relative_diff['ANL_CTR_FLW'] = ANL
        heatplot_multidate_rmse_relative_diff['REF_CTR_FLW'] = REF
        multidate_multilead_relative_diff(**heatplot_multidate_rmse_relative_diff).gen_fig()

        heatplot_fixedlead_fss_relative_diff['ANL_CTR_FLW'] = ANL
        heatplot_fixedlead_fss_relative_diff['REF_CTR_FLW'] = REF
        multidate_fixedlead_relative_diff(**heatplot_fixedlead_fss_relative_diff).gen_fig()

        heatplot_multidate_fss_relative_diff['ANL_CTR_FLW'] = ANL
        heatplot_multidate_fss_relative_diff['REF_CTR_FLW'] = REF
        for LEV in LEVS:
            heatplot_multidate_fss_relative_diff['LEV'] = LEV
            multidate_multilead_relative_diff(**heatplot_multidate_fss_relative_diff).gen_fig()

        heatplot_multilevel_multilead_fss_relative_diff['ANL_CTR_FLW'] = ANL
        heatplot_multilevel_multilead_fss_relative_diff['REF_CTR_FLW'] = REF

        for DT in DTS:
            STRT_DT = DT[0]
            STOP_DT = DT[1]
            VALID_DT = DT[2]

            heatplot_multilevel_multilead_fss_relative_diff['STRT_DT'] = STRT_DT
            heatplot_multilevel_multilead_fss_relative_diff['STOP_DT'] = STOP_DT
            heatplot_multilevel_multilead_fss_relative_diff['VALID_DT'] = VALID_DT
            
            multilevel_multilead_relative_diff(**heatplot_multilevel_multilead_fss_relative_diff).gen_fig()
