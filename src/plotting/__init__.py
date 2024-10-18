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
# 
##################################################################################
# Imports
##################################################################################
import matplotlib
from datetime import datetime as dt
from datetime import timedelta as td
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
from control_flows import ctr_flw
from lineplots import line_plot

##################################################################################
INDT = '    '
VRF_ROOT = os.environ['VRF_ROOT']
IF_CNTR_PLT = os.environ['IF_CNTR_PLT']

MPAS_240_U = ctr_flw('MPAS_240-U', mem_ids=['mean'])
MPAS_240_U_LwrBnd = ctr_flw('MPAS_240-U_LwrBnd', mem_ids=['mean'])
WRF_9_WestCoast = ctr_flw('WRF_9_WestCoast', ['d01'], ['mean'])
WRF_9_3_WestCoast = ctr_flw('WRF_9-3_WestCoast', ['d01', 'd02'], ['mean'])
ECMWF = ctr_flw('ECMWF')
GFS = ctr_flw('GFS')
GEFS = ctr_flw('GEFS')

ens_v_bkg = {
             'MET_TOOL': 'GridStat',
             'PRFX': 'grid_stat_QPF_24hr',
             'STAT_TYPE': 'cnt',
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
             'VRF_ROOT': VRF_ROOT,
             'IF_CNTR_PLT': IF_CNTR_PLT,
             'STAT_KEYS': ['RMSE', 'PR_CORR'],
             'STRT_DT': '2022122300',
             'STOP_DT': '2022122700',
             'CYC_INC': '24',
             'VALID_DT': '2022122800',
             'MSK': 'CA_All',
             'LAB_IDX': [0, 1],
             'ENS_LAB': False,
             'GRD_LAB': True,
             'DT_FRMT': '%Y%m%d%H'
            }

test_lineplot = line_plot(ens_v_bkg)

