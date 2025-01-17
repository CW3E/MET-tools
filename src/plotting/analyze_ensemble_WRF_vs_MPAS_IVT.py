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
    GRDS=['d01'],
    MEM_IDS=['mean']
    )

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
# Relative diff stat heatplot templates
##################################################################################
heatplot_multidate_corr_relative_diff = {
        'VRF_STRT': '2022022400',
        'VRF_STOP': '2022030200',
        'MSK': 'Northeast_Pacific',
        'DT_INC': '24',
        'STAT_KEY': 'PR_CORR',
        'ANL_GRD_KEY': None,
        'ANL_MEM_KEY': 'mean',
        'REF_GRD_KEY': 'd01',
        'REF_MEM_KEY': 'mean',
        'MIN_LD': 24,
        'MAX_LD': 120,
        'LD_INC': 24,
        'DT_FMT': '%Y-%m-%d',
        'COLORBAR': relative_diff_cb,
        'MET_TOOL': 'GridStat',
        'CSE': 'valid_date_2022-03-02T00',
        'FIG_CSE': 'relative_diff_multidate_multilead_plots',
        'VRF_REF': 'ERA5',
        'VRF_FLD': 'IVT_00hr',
        'LEV': None,
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

    # relative diff heat plots
    for DIFF in DIFFS:
        ANL = DIFF[0]
        REF = DIFF[1]

        heatplot_multidate_corr_relative_diff['ANL_CTR_FLW'] = ANL
        heatplot_multidate_corr_relative_diff['REF_CTR_FLW'] = REF
        multidate_multilead_relative_diff(**heatplot_multidate_corr_relative_diff).gen_fig()
