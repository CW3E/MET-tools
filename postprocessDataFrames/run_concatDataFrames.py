##################################################################################
# Description
##################################################################################
# This script reads in arbitrary grid_stats_*.bin output files from
# makeDataFrames.py and concatenates Pandas dataframes of pecified statistics
# types writing workflow parameters as labels for later statistical encoding.
# The dataframes are saved into a dictionary with key names associated
# to the Grid-Stat statistics type, written to a Pickled binary file.
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
import sys
import os
import numpy as np
import pandas as pd
from pandas.api.types import CategoricalDtype
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
        'VX_MASK',
        'FCST_VALID_END',
        'FCST_LEAD',
        'FCST_THRESH',
       ]

# levels to be set as ordered categories within the data
LEVS = [
        '>0.0',
        '>=10.0',
        '>=25.4',
        '>=50.8',
        '>=101.6',
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

# generate output file names from the analyzed case studies and control flows
out_name = 'concat_df'
for cse in CSES:
    out_name += '_' + cse
for ctr_flw in CTR_FLWS:
    out_name += '_' + ctr_flw

# include non-empty grid parameters
for grid in GRDS:
    # include underscore if grid is of nonzero length
    if len(grid) > 0:
        grd = '_' + grid
    else:
        grd = ''
    out_name += grd

# include non-empty prefixes used in Grid-Stat configurations
for prfx in PRFXS:
    # include underscore if prefix is of nonzero length
    if len(prfx) > 0:
        pfx = '_' + prfx
    else:
        pfx = ''
    out_name += prfx
                     
log_f = log_dir + '/' + out_name + '.log'
out_path = OUT_ROOT + '/' + out_name + '.bin'

# creating empty dictionary for storage of merged dataframes
data_dict = {}

with open(log_f, 'w') as log_f:
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
                    for in_path in in_paths:
                        print(STR_INDT + in_path, file=log_f)

                    # dataframe corresponding to case / control flow / grid / prefix
                    param_df = {'CASE': [cse], 'CTR_FLW': [ctr_flw],
                                'GRID': [grid],  'PRFX': [prfx]}

                    param_df = pd.DataFrame.from_dict(param_df, orient='columns')

                    for in_path in in_paths:
                        try:
                            with open(in_path, 'rb') as f:
                                date_data = pickle.load(f)
    
                            for stat_type in TYPES:
                                # storage for merged dataframes of same stat type
                                merge_df = pd.DataFrame()

                                try:
                                    # extract parsed fields of stat_type
                                    stat_df = date_data[stat_type]
                                    
                                    # extract basic fields for output data
                                    field_df = stat_df[FLDS]

                                    for stat in STATS:
                                        try:
                                            # assign additional columns for specific statistics
                                            exec('field_df = field_df.assign(%s=stat_df[\'%s\'])'%(stat,stat))
    
                                        except:
                                            print('WARNING: ' + stat + ' not found in value pair of:', file=log_f)
                                            print(STR_INDT + 'File: '  + in_path, file=log_f)
                                            print(STR_INDT + 'Key: ' + stat_type, file=log_f)
    
                                    # merge worfklow parameters into columns
                                    tmp_df = param_df.merge(field_df, how='cross') 
    
                                    if stat_type in data_dict.keys():
                                        data_dict[stat_type] = pd.concat([data_dict[stat_type], tmp_df], axis=0)
    
                                    else:
                                        data_dict[stat_type] = tmp_df
    
                                except:
                                    print('WARNING: ' + stat_type + ' key not found in:',
                                            file=log_f)
                                    print(STR_INDT + in_path, file=log_f)
                                            
                        except:
                            print('WARNING: file:\n' + in_path, file=log_f)
                            print('is not readable, skipping this file.')
   
    for dict_key in data_dict.keys():
        # clean up concatenated dataframes
        tmp_df = data_dict[dict_key]

        # turn forecast thresholds into ordered categories
        tmp_df['FCST_THRESH'] = pd.Categorical(tmp_df['FCST_THRESH'].values,
                categories=LEVS, ordered=True)

        # sort data on the following order
        sort_order = ['CASE', 'CTR_FLW', 'GRID', 'PRFX'] + FLDS
        tmp_df = tmp_df.sort_values(by=sort_order)

        # clean NAs including non-matching categories
        tmp_df = tmp_df.dropna(axis=1, how='all')
        
        # drop columns of empty strings
        for df_key in tmp_df.keys():
            if (tmp_df[df_key].values == '').all():
                tmp_df = tmp_df.drop(labels = [df_key], axis = 1)

        for stat in STATS:
            # convert statistics to float values
            try:
                tmp_df[stat] = tmp_df[stat].astype('float')

            except:
                pass

        # re-index based on row values
        tmp_df = tmp_df.set_axis(range(1, len(tmp_df.index) +1 ), axis='index')

        # store back in the dictionry under dict_key
        data_dict[dict_key] = tmp_df

    print('Writing out data to ' + out_path, file=log_f)
    with open(out_path, 'wb') as f:
        pickle.dump(data_dict, f)

