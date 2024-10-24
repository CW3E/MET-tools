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

# Supported MET tools and their stat information
MET_TOOLS = {
             'GridStat':
             {
                 'RMSE': {
                     'label': 'Root-Mean\nSquared Error (mm)',
                     'type': 'cnt',
                     },
                 'PR_CORR': {
                     'label': 'Pearson\nCorrelation',
                     'type': 'cnt',
                     },
                 'FSS': {
                     'label': 'Fractional\nSkill Score',
                     'type': 'nbrcnt',
                     },
                 'AFSS': {
                     'label': 'Asymptotic Fractional\nSkill Score',
                     'type': 'nbrcnt',
                     },
                 'GSS': {
                     'label': 'Gilbert\nSkill Score',
                     'type': 'nbrcts',
                     },
                 'CSI': {
                     'label': 'Critical\nSuccess Index',
                     'type': 'nbrcts',
                     },
                 }
             }

# Verfification reference data sets for ground truth
VRF_REFS = {
            'StageIV': {
                'label': 'StageIV',
                'fields': {
                    'QPF_24hr': {
                        'label': '24hr Accumulated Precipitation',
                        }
                    }
                }
            }

def convert_dt(iso_str):
    return dt.strptime(iso_str, '%Y%m%d%H')

def check_vrf_ref(instance, attribute, value):
    if not value in VRF_REFS:
        raise ValueError('ERROR: ' + value + ' is not a supported' +\
                ' ground truth for verfication reference ' + instance.VRF_REF)

def check_vrf_fld(instance, attribute, value):
    if not value in VRF_REFS[instance.VRF_REF]['fields']:
        raise ValueError('ERROR: ' + value + ' is not a supported' +\
                ' field for verfication reference ' + instance.VRF_REF)

def check_stat_key(instance, attribute, value):
    if not value in MET_TOOLS[instance.MET_TOOL]:
        raise ValueError('ERROR: ' + value + ' is not a supported' +\
                ' statistic for verfication reference ' + instance.MET_TOOL)

def check_path(instance, attribute, value):
    if not os.path.isdir(value):
        raise OSError('ERROR: ' + value + 'directory does not exist.')

def check_io(instance, attribute, value):
    in_root, out_root = instance.gen_io_paths()
    os.system('mkdir -p ' + out_root)
    check_path(instance, attribute, in_root)
    check_path(instance, attribute, out_root)

##################################################################################
# Define parent classes
##################################################################################

@define
class plot:
    STRT_DT:str = field(
            converter=convert_dt,
            )
    STOP_DT:str = field(
            converter=convert_dt,
            )
    DT_INC:str = field(
            validator=validators.matches_re('^[0-9]+h$'),
            converter=lambda x : x + 'h',
            )
    MET_TOOL:str = field(
            validator=validators.in_(MET_TOOLS),
            )
    MSK:str = field(
            validator=[validators.instance_of(str),
                validators.min_len(1)],
            )
    CSE:str = field(
            validator=[validators.instance_of(str),
                validators.min_len(1)],
            )
    FIG_CSE:str = field(
            validator=validators.optional([validators.instance_of(str),
                validators.min_len(1)]),
            )
    VRF_REF:str = field(
            validator=validators.in_(VRF_REFS),
            )
    VRF_FLD:str = field(
            validator=[validators.instance_of(str),
                check_vrf_fld]
            )
    LEV:str = field(
            validator=validators.optional(validators.instance_of(str)),
            )
    IF_CNTR_PLT:str = field(
            validator=[validators.instance_of(bool),
                check_io],
            converter=lambda x: eval(x.lower().capitalize()),
            )
    FIG_LAB:str = field(
            validator=validators.optional(validators.instance_of(str)),
            )
    ENS_LAB:bool = field(
            validator=validators.instance_of(bool),
            )
    GRD_LAB:bool = field(
            validator=validators.instance_of(bool),
            )

    def gen_cycs(self):
        return pd.date_range(start=self.STRT_DT, end=self.STOP_DT, 
                             freq=self.DT_INC).to_pydatetime()
                
    def gen_io_paths(self):
        if self.IF_CNTR_PLT:
            in_root = '/in_root/' + self.CSE
            out_root = '/out_root/' + self.CSE + '/figures/' +\
                    self.CSE
        else:
            in_root = VRF_ROOT + '/' + self.CSE
            out_root = VRF_ROOT + '/' + self.CSE + '/figures/' +\
                    self.CSE
    
        if self.FIG_CSE:
                out_root += '/' + self.FIG_CSE

        return in_root, out_root

@define
class control_flow:
    NAME:str = field(
        validator=[validators.instance_of(str),
        validators.min_len(1)]
        )
    PLT_LAB:str = field(
            validator=[validators.instance_of(str),
                validators.min_len(1)]
            )

    GRDS:list = field(
        validator=validators.optional(
            validators.deep_iterable(
                member_validator=validators.instance_of(str),
                iterable_validator=validators.instance_of(list))
            )
        )
    MEM_IDS:list = field(
        validator=validators.optional(
            validators.deep_iterable(
                member_validator=validators.instance_of(str),
                iterable_validator=validators.instance_of(list))
            )
        )

##################################################################################
# Templated configurations
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

ens_v_bkg = {
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
             'ENS_LAB': False,
             'GRD_LAB': True,
             'FIG_LAB': None,
            }
