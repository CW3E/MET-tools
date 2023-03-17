##################################################################################
# Description
##################################################################################
# This script reads in arbitrary grid_stat_* output files from a MET analysis
# and creates Pandas dataframes containing a time series for each file type
# versus lead time to a verification period. The dataframes are saved into a
# Pickled dictionary organized by MET file extension as key names, taken
# agnostically from bash wildcard patterns.
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
from datetime import datetime as dt
from datetime import timedelta

##################################################################################
# SET GLOBAL PARAMETERS 
##################################################################################
# define control flow to analyze 
CTR_FLW = 'GFS'

# define the case-wise sub-directory
CSE = 'VD'

# verification domain for the forecast data                                                                           
GRD = '0.25'

# define the interpolation method and related parameters

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2019021100'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
END_DT = '2019021400'

# number of hours between zero hours for forecast data (string HH)
CYC_INT = '24'

# optionally define output prefix, set as empty string if not needed
PRFX = ''

# standard string indentation
STR_INDT = '    '

# root directory for gridstat outputs
IN_ROOT = '/cw3e/mead/projects/cwp106/scratch/cgrudzien/cycling_sensitivity_testing'

# root directory for processed pandas outputs
OUT_ROOT = '/cw3e/mead/projects/cwp106/scratch/cgrudzien/cycling_sensitivity_testing'

##################################################################################
# Process data
##################################################################################
# commands to be run if executed as a script
if __name__ == '__main__':
    # define derived data paths 
    cse = CSE + '/' + CTR_FLW
    in_data_root = IN_ROOT + '/' + cse + '/MET_analysis'

    # check for input root directory
    if not os.path.isdir(in_data_root):
        print('ERROR: input data root directory ' + in_data_root +\
                ' does not exist.')
        sys.exit(1)
    
    # convert to date times
    if len(STRT_DT) != 10:
        print('ERROR: STRT_DT, ' + STRT_DT + ', is not in YYYYMMDDHH format.')
        sys.exit(1)
    else:
        s_iso = STRT_DT[:4] + '-' + STRT_DT[4:6] + '-' + STRT_DT[6:8] +\
                '_' + STRT_DT[8:]
        strt_dt = dt.fromisoformat(s_iso)

    if len(END_DT) != 10:
        print('ERROR: END_DT, ' + END_DT + ', is not in YYYYMMDDHH format.')
        sys.exit(1)
    else:
        e_iso = END_DT[:4] + '-' + END_DT[4:6] + '-' + END_DT[6:8] +\
                '_' + END_DT[8:]
        end_dt = dt.fromisoformat(e_iso)

    if len(CYC_INT) != 2:
        print('ERROR: CYC_INT, ' + CYC_INT + ', is not in HH format.')
        sys.exit(1)
    else:
        cyc_int = CYC_INT + 'H'
    
    # define the output name
    out_data_root = OUT_ROOT + '/' + cse + '/MET_analysis'
    os.system('mkdir -p ' + out_data_root)
    out_path = out_data_root + '/grid_stats_' + PRFX + '_' + GRD + '_' + STRT_DT +\
               '_to_' + END_DT + '.bin'
    
    # generate the date range for the analyses
    analyses = pd.date_range(start=strt_dt, end=end_dt,
                             freq=cyc_int).to_pydatetime()
    
    # initiate empty dictionary for storage of dataframes by keyname
    data_dict = {}
    
    print('Processing dates ' + STRT_DT + ' to ' + END_DT)
    for anl_dt in analyses:
        # directory string format
        anl_strng = anl_dt.strftime('%Y%m%d%H')
        
        # define the gridstat files to open based on the analysis date
        in_paths = in_data_root + '/' + anl_strng + '/' + GRD +\
                   '/grid_stat_' + PRFX + '*.txt'
    
        # loop sorted grid_stat_PRFX* files, sorting compares first on the
        # length of lead time for non left-padded values
        in_paths = sorted(glob.glob(in_paths),
                          key=lambda x:(len(x.split('_')[-4]), x))
        for in_path in in_paths:
            print(STR_INDT + 'Opening file ' + in_path)
    
            # cut the diagnostic type from file name
            fname = in_path.split('/')[-1]
            split_name = fname.split('_')
            postfix = split_name[-1].split('.')
            postfix = postfix[0]
    
            # open file, load column names, then loop lines
            f = open(in_path)
            cols = f.readline()
            cols = cols.split()
            
            if len(cols) > 0:
                fname_df = {} 
                tmp_dict = {}
                df_indx = 1
    
                print(STR_INDT + 'Loading columns:')
                for col_name in cols:
                    print(STR_INDT * 2 + col_name)
                    fname_df[col_name] = [] 
    
                fname_df =  pd.DataFrame.from_dict(fname_df, orient='columns')
    
                # parse file by line, concatenating columns
                for line in f:
                    split_line = line.split()
    
                    for i in range(len(split_line)):
                        val = split_line[i]
    
                        # filter NA vals
                        if val == 'NA':
                            val = np.nan
                        tmp_dict[cols[i]] = val
    
                    tmp_dict['line'] = [df_indx]
                    tmp_dict = pd.DataFrame.from_dict(tmp_dict, orient='columns')
                    fname_df = pd.concat([fname_df, tmp_dict], axis=0)
                    df_indx += 1
    
                fname_df['line'] = fname_df['line'].astype(int)
                
                if postfix in data_dict.keys():
                    last_indx = data_dict[postfix].index[-1]
                    fname_df['line'] = fname_df['line'].add(last_indx)
                    fname_df = fname_df.set_index('line')
                    data_dict[postfix] = pd.concat([data_dict[postfix], fname_df], axis=0)
    
                else:
                    fname_df = fname_df.set_index('line')
                    data_dict[postfix] = fname_df
    
            else:
                print('WARNING: file ' + in_path + ' is empty, skipping this file.')
    
            print(STR_INDT + 'Closing file ' + in_path)
            f.close()
    
    print('Writing out data to ' + out_path)
    f = open(out_path, 'wb')
    pickle.dump(data_dict, f)
    f.close()

##################################################################################
# end
