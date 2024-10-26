##################################################################################
# Description
##################################################################################
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

##################################################################################
# Templated Experiment Configurations
##################################################################################
MPAS_240_U = control_flow(NAME='MPAS_240-U', PLT_LAB='MPAS 240-U',
        GRDS=None, MEM_IDS=['mean'])
MPAS_240_U_LwrBnd = control_flow(NAME='MPAS_240-U_LwrBnd',
        PLT_LAB='MPAS 240-U LwrBnd', GRDS=None, MEM_IDS=['mean'])
WRF_9_WestCoast = control_flow(NAME='WRF_9_WestCoast',
        PLT_LAB='WRF 9km', GRDS=['d01'], MEM_IDS=['mean'])
WRF_9_3_WestCoast = control_flow(NAME='WRF_9-3_WestCoast',
        PLT_LAB='WRF 9km/3km', GRDS=['d01', 'd02'], MEM_IDS=['mean'])
ECMWF = control_flow(NAME='ECMWF', PLT_LAB='ECMWF Deterministic',
        GRDS=None, MEM_IDS=None)
GFS = control_flow(NAME='GFS', PLT_LAB='GFS Determinisitc',
        GRDS=None, MEM_IDS=None)
GEFS = control_flow(NAME='GEFS', PLT_LAB='GEFS mean',
        GRDS=None, MEM_IDS=None)

##################################################################################
# Templated Plot Configurations
##################################################################################
lineplot_rmse_corr = {
        'MET_TOOL': 'GridStat',
        'CSE': 'valid_date_2022-12-28T00',
        'FIG_CSE': 'testing',
        'CTR_FLWS': [
                     MPAS_240_U,
                     MPAS_240_U_LwrBnd,
                     WRF_9_WestCoast,
                     WRF_9_3_WestCoast,
                     ECMWF,
                     GFS,
                     GEFS
                    ],
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'LEV': None,
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'STAT_KEYS': ['RMSE', 'PR_CORR'],
        'CI': 'NC',
        'STRT_DT': '2022122300',
        'STOP_DT': '2022122700',
        'DT_INC': '24',
        'VALID_DT': '2022122800',
        'MSK': 'CA_All',
        'MEM_LAB': False,
        'GRD_LAB': True,
        'FIG_LAB': None,
        'IF_SHOW': True,
       }

lineplot_fss_afss = {
        'CTR_FLWS': [
                     MPAS_240_U,
                     MPAS_240_U_LwrBnd,
                     WRF_9_WestCoast,
                     WRF_9_3_WestCoast,
                     ECMWF,
                     GFS,
                     GEFS
                    ],
        'VALID_DT': '2022122800',
        'STAT_KEYS': ['FSS', 'AFSS'],
        'CI': 'NC',
        'STRT_DT': '2022122300',
        'STOP_DT': '2022122700',
        'DT_INC': '24',
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'valid_date_2022-12-28T00',
        'FIG_CSE': 'testing',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'LEV': '>=50.0',
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': True,
        'FIG_LAB': None,
        'IF_SHOW': True,
       }

heat_plot_multidate_rmse = {
        'CTR_FLW': WRF_9_3_WestCoast,
        'STAT_KEY': 'RMSE',
        'GRD_KEY': 'd02',
        'MEM_KEY': 'mean',
        'MIN_LD': 24,
        'MAX_LD': 120,
        'LD_INC': 24,
        'DT_FMT': '%Y%m%d%H',
        'ALPHA': 5.0,
        'PLT_SCL': None,
        'STRT_DT': '2022122300',
        'STOP_DT': '2022122700',
        'DT_INC': '24',
        'MET_TOOL': 'GridStat',
        'MSK': 'CA_All',
        'CSE': 'valid_date_2022-12-28T00',
        'FIG_CSE': 'testing',
        'VRF_REF': 'StageIV',
        'VRF_FLD': 'QPF_24hr',
        'LEV': '>=50.0',
        'IF_CNTR_PLT': IF_CNTR_PLT,
        'MEM_LAB': False,
        'GRD_LAB': True,
        'FIG_LAB': None,
        'IF_SHOW': True,
        }

##################################################################################
