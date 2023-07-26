##################################################################################
# Description
##################################################################################
# This script reads in arbitrary grid_stats_*.bin output files from
# proc_gridstat.py and concatenates Pandas dataframes of a specified statistics
# type writing workflow parameters as categorical variables for statistical
# encoding. The dataframes are saved into a Pickled binary file.
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
import glob
#import statsmodels.api as sm
#from statsmodels.formula.api import ols
import ipdb

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flow to analyze 
CTR_FLWS = [
            'NAM_lag06_b0.00_v03_h0300',
            'RAP_lag06_b0.00_v06_h0300'
           ]

# define the case-wise sub-directory
CSES = [
        'CC',
        'VD',
        'PNW22',
       ]

# optionally define verification domain label, set as empty string if not needed
GRDS = [
        '',
       ]

# optionally define output prefix, set as empty string if not needed
PRFXS = [
         '',
        ]

# Grid-Stat statistics file type extensions / dictionary keys to access
TYPES = [
         'cnt',
         'nbrcnt',
        ]
             
# statistics to combine into processed dataframe included in the above file types
STATS = [
         'RMSE',
         'PR_CORR',
         'FSS',
         'AFSS',
        ]

# verification fields to be extracted across stats / analyses
FLDS = [
        'FCST_LEAD',
        'VX_MASK',
        'FCST_VALID_END',
       ]

# root directory for gridstat outputs
IN_ROOT = '/cw3e/mead/projects/cwp106/scratch/cgrudzien/tuning_regression_analysis'

# root directory for processed pandas outputs
OUT_ROOT = '/cw3e/mead/projects/cwp106/scratch/cgrudzien/tuning_regression_analysis'

##################################################################################
# Data processing routines
##################################################################################
# standard string indentation
STR_INDT = '    '

log_dir = OUT_ROOT + '/batch_logs'
os.system('mkdir -p ' + log_dir)

log_name = log_dir + '/cat_df'
for cse in CSES:
    log_name += '_' + cse
for ctr_flw in CTR_FLWS:
    log_name += '_' + ctr_flw

for grid in GRDS:
    # include underscore if grid is of nonzero length
    if len(grid) > 0:
        grd = '_' + grid
    else:
        grd = ''
    log_name += grd

for prfx in PRFXS:
    # include underscore if prefix is of nonzero length
    if len(prfx) > 0:
        pfx = '_' + prfx
    else:
        pfx = ''
    log_name += prfx
                     
log_name += '.log'

# create empty data frame with columns according to parameters
out_df = {'CASES': [], 'CTR_FLW': [], 'GRID': [], 'PRFX': []}
for FLD in FLDS:
    out_df[FLD] = []

for STAT in STATS:
    out_df[STAT] = []

out_df = pd.DataFrame.from_dict(out_df, orient='columns')

with open(log_name, 'w') as log_f:
    for cse in CSES:
        for ctr_flw in CTR_FLWS:
            for grid in GRDS:
                # include underscore if grid is of nonzero length
                if len(grid) > 0:
                    grd = '_' + grid
                else:
                    grd = ''
                    
                for prfx in PRFXS:
                    # include underscore if prefix is of nonzero length
                    if len(prfx) > 0:
                        pfx = '_' + prfx
                    else:
                        pfx = ''
                    
                    # check for input / output root directory
                    if not os.path.isdir(IN_ROOT):
                        print('ERROR: input data root directory ' + IN_ROOT +\
                                ' does not exist.', file=log_f)
                        sys.exit(1)
                    
                    # check for input / output root directory
                    elif not os.path.isdir(OUT_ROOT):
                        print('ERROR: output data root directory ' +\
                                OUT_ROOT + ' does not exist.', file=log_f)
                        sys.exit(1)
                   
                    # define the gridstat files to open based on the analysis date
                    in_paths = IN_ROOT + '/' + cse + '/' + ctr_flw + '/*' +\
                               '/grid_stat' + pfx + grd + '*.bin'

                    # loop sorted grid_stat_*.bin files
                    print('Searching in_paths for pickled data frames:', file=log_f)
                    print(STR_INDT + in_paths, file=log_f)
                    in_paths = sorted(glob.glob(in_paths))
                               
                    print('Processing date binaries at paths:', file=log_f)
                    print((STR_INDT + in_path + '\n' for in_path in in_paths),
                            file=log_f)

                    # dataframe corresponding to case / control flow / grid / prefix
                    tmp_df = {'CASE': [cse], 'CTR_FLW': [ctr_flw],
                              'GRID': [grid],  'PRFX': [prfx]}

                    tmp_df = pd.DataFrame.from_dict(tmp_df, orient='columns')

                    for in_path in in_paths:
                        with open(in_path, 'rb') as f:
                            tmp_data = pickle.load(f)

                        for s_type in TYPES:
                            ipdb.set_trace()
                            try:
                                s_data = tmp_data[s_type]
                                f_df = s_data[FLDS]

                                for stat in STATS:
                                    try:
                                        exec('f_df = f_df.assign(%s=s_data[\'%s\'])'%(stat,stat))

                                    except:
                                        print('WARNING: ' + stat +
                                                ' not found in value pair of:',
                                                file=log_f)
                                        print(STR_INDT + 'File: '  + in_path,
                                                file=log_f)
                                        print(STR_INDT + 'Key: ' + s_type,
                                                file=log_f)

                                f_df

                            except:
                                print('WARNING: ' + s_type + ' key not found in:',
                                        file=log_f)
                                print(STR_INDT + in_path, file=log_f)
                                        

                    stat_df = pd.concat([tmp_df, stat_df], axis=1)


