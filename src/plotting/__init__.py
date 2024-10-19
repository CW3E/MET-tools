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
from attrs import define, field, validators

##################################################################################
# Load workflow constants and Utility Methods 
##################################################################################
INDT = '    '
VRF_ROOT = os.environ['VRF_ROOT']
IF_CNTR_PLT = os.environ['IF_CNTR_PLT']

def convert_dt(iso_str):
    return dt.strptime(iso_str, '%Y%m%d%H')

# Define pre-set plotting parameters for specific stats
stat_labs = {
             'RMSE': 'Root-Mean\nSquared Error (mm)',
             'PR_CORR': 'Pearson\nCorrelation',
             'FSS': 'Fractional\nSkill Score',
             'AFSS': 'Asymptotic Fractional\nSkill Score',
             'GSS': 'Gilbert\nSkill Score',
             'CSI': 'Critical\nSuccess Index',
            }

stat_types = [
              'cnt',
              'cts',
              'nbrcnt',
              'nbrcts',
             ]

# Define the currently supported attributes for line plots
MET_TOOLS = [
             'GridStat',
            ]
PRFXS = [
         'grid_stat_QPF_24hr',
        ]

##################################################################################
# Define parent classes
##################################################################################

@define
class plot:
    STRT_DT:str = field(
                        validator=validators.matches_re('^[0-9]{10}$'),
                        converter=plotting.convert_dt,
                       )
    STOP_DT:str = field(
                        validator=validators.matches_re('^[0-9]{10}$'),
                        converter=plotting.convert_dt,
                       )
    CYC_INC:str = field(
                        validator=validators.matches_re('^[0-9]+$'),
                        converter=lambda x : x + 'h'
                       )
    # NOTE: NEED TO START CONVERTING THESE INTO ATTRIBUTES OF PLOTTING CLASS
    # USING ATTRS TO HANDLE INTANTIATION VALIDATION
    if not self.MET_TOOL in line_plot.MET_TOOLS:
        print('ERROR: ' + self.MET_TOOL + ' is not a supported tool' +\
              ' currently.')
        print('Supported tools include:')
        for tool in line_plot.MET_TOOLS:
            print(INDT + tool)
        raise ValueError
    else:
        met_tool = self.MET_TOOL

    if not self.PRFX in line_plot.PRFXS:
        print('ERROR: ' + line_plot.PRFX + ' is not a supported' +\
              ' analysis currently.')
        print('Supported analyses include:')
        for prfx in line_plot.PRFXS:
            print(INDT + prfx)
        raise ValueError
    else:
        prfx = self.PRFX

    if not type(self.MSK) == str:
        raise TypeError(1,
              'ERROR: verification region name attribute "MSK" is not' +\
              ' a string.')
    elif len(self.MSK) == 0:
        raise ValueError(1,
              'ERROR: verification region name attribute "CSE" is length' +\
              ' zero.')
    else:
        msk = self.MSK

    if not type(self.CSE) == str:
        raise TypeError(1,
              'ERROR: case study name attribute "CSE" is not a string.')
    elif len(self.CSE) == 0:
        raise ValueError(1,
              'ERROR: case study name attribute "CSE" is length zero.' +\
              ' This must be defined as the root of the case study ' +\
              ' / configuration directory structure for verification IO.')
    else:
        cse = self.CSE

    if not type(self.FIG_CSE) == str:
        raise TypeError('ERROR: figure output sub-directory name' +\
              ' FIG_CSE is not a string. Define equal to an empty' +\
              ' string if not used.')
    else:
        fig_cse = self.FIG_CSE


@define
class ctr_flw:
    name:str = field(validator=[validators.instance_of(str),
                                validators.min_len(1)])

    grds:list = field(validator=validators.optional(
          validators.deep_iterable(
          member_validator=validators.instance_of(str),
          iterable_validator=validators.instance_of(list))
         )
        )

    mem_ids:list = field(validator=validators.optional(
             validators.deep_iterable(
              member_validator=validators.instance_of(str),
              iterable_validator=validators.instance_of(list))
            )
           )

##################################################################################
# Templated configurations
##################################################################################
MPAS_240_U = ctr_flw(name='MPAS_240-U', grds=None, mem_ids=['mean'])
MPAS_240_U_LwrBnd = ctr_flw(name='MPAS_240-U_LwrBnd', grds=None, mem_ids=['mean'])
WRF_9_WestCoast = ctr_flw(name='WRF_9_WestCoast', grds=['d01'], mem_ids=['mean'])
WRF_9_3_WestCoast = ctr_flw(name='WRF_9-3_WestCoast', grds=['d01', 'd02'],
        mem_ids=['mean'])
ECMWF = ctr_flw(name='ECMWF', grds=None, mem_ids=None)
GFS = ctr_flw(name='GFS', grds=None, mem_ids=None)
GEFS = ctr_flw(name='GEFS', grds=None, mem_ids=None)

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
