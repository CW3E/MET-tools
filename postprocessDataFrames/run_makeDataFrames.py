##################################################################################
# Description
##################################################################################
# This script reads in arbitrary MET ASCII output files 
# and creates Pandas dataframes containing a time series for each file type
# versus lead time to a verification period. The dataframes are saved into a
# Pickled dictionary organized by MET file extension as key names, taken
# agnostically from bash wildcard patterns.
#
# Batches of hyper-parameter-dependent data can be processed by constructing
# lists of makeDataFrames arguments which define configurations that will be mapped
# to run in parallel through Python multiprocessing.
#
##################################################################################
# License Statement
##################################################################################
#
# Copyright 2023 CW3E, Contact Colin Grudzien cgrudzien@ucsd.edu
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
import multiprocessing 
from multiprocessing import Pool
from config_DataFrames import *

##################################################################################
# Construct hyper-paramter array for batch processing ASCII outputs
##################################################################################
# convert to date times
if not STRT_DT.isdigit() or len(STRT_DT) != 10:
    print('ERROR: STRT_DT\n' + STRT_DT + '\n is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    iso = STRT_DT[:4] + '-' + STRT_DT[4:6] + '-' + STRT_DT[6:8] + '_' +\
            STRT_DT[8:]
    strt_dt = dt.fromisoformat(iso)

if not STRT_DT.isdigit() or len(STOP_DT) != 10:
    print('ERROR: STOP_DT\n' + STOP_DT + '\n is not in YYYYMMDDHH format.')
    sys.exit(1)
else:
    iso = STOP_DT[:4] + '-' + STOP_DT[4:6] + '-' + STOP_DT[6:8] + '_' +\
            STOP_DT[8:]
    stop_dt = dt.fromisoformat(iso)

if not CYC_INC.isdigit():
    print('ERROR: CYC_INC\n' + CYC_INC + '\n is not in HH format.')
    sys.exit(1)
else:
    cyc_inc = CYC_INC + 'H'

if not ANL_MIN.isdigit():
    print('ERROR: ANL_MIN\n' + ANL_MIN + '\n is not in HH format.')
    sys.exit(1)
else:
    anl_min = int(ANL_MIN)

if not ANL_MAX.isdigit():
    print('ERROR: ANL_MAX\n' + ANL_MAX + '\n is not in HH format.')
    sys.exit(1)
else:
    anl_max = int(ANL_MAX)

if not ANL_INC.isdigit():
    print('ERROR: ANL_INC\n' + ANL_INC + '\n is not in HH format.')
    sys.exit(1)
else:
    anl_inc = int(ANL_INC)

if (anl_max - anl_min) % anl_inc != 0:
    print('ERROR: the interval [ANL_MIN, ANL_MAX]')
    print('[' + ANL_MIN + ',' + ANL_MAX+ ']')
    print('must be evenly divisible into increments of ANL_INC,' +\
            ANL_INC + '.')

print('Parsing analysis lead times:')
for i_anl in range(anl_min, anl_max + anl_inc, anl_inc):
    print(INDT + str(i_anl))

PFXS = []
if CMP_ACC:
    if not ACC_MIN.isdigit():
        print('ERROR: ACC_MIN, ' + ACC_MIN + ', is not in HH format.')
        sys.exit(1)
    else:
        acc_min = int(ACC_MIN)
    
    if not ACC_MAX.isdigit():
        print('ERROR: ACC_MAX, ' + ACC_MAX + ', is not in HH format.')
        sys.exit(1)
    else:
        acc_max = int(ACC_MAX)
    
    if not ACC_INC.isdigit():
        print('ERROR: ACC_INC, ' + ACC_INC + ', is not in HH format.')
        sys.exit(1)
    else:
        acc_inc = int(ACC_INC)

    if (acc_max - acc_min) % acc_inc != 0:
        print('ERROR: the interval [ACC_MIN, ACC_MAX]')
        print('[' + ACC_MIN + ',' + ACC_MAX+ ']')
        print('must be evenly divisible into increments of ACC_INC,' +\
                ACC_INC + '.')

    print('Parsing precipitation accumulations:')
    for i_acc in range(acc_min, acc_max + acc_inc, acc_inc):
        acc_hr = str(i_acc) + 'hr'
        print(INDT + acc_hr)
        PFXS += [PRFX + '_' + acc_hr]

else:
    print('Not parsing precipitation accumulation.')
    PFXS += [PRFX]

# container for map
CFGS = []

# generate the date range for the analyses
anl_dt = pd.date_range(start=strt_dt, end=stop_dt, freq=cyc_inc).to_pydatetime()

print('Processing configurations:')
for anl_dt in anl_dt:
    anl_strng = anl_dt.strftime('%Y%m%d%H')
    print(INDT + 'Forecast start: ' + anl_strng)

    for CTR_FLW in CTR_FLWS:
        print(INDT * 2 + 'Control flow: ' + CTR_FLW)

        for MEM_ID in MEM_IDS:
            print(INDT * 3 + 'Ensemble member ID: ' + MEM_ID)
            
            for GRD in GRDS:
                print(INDT * 4 + 'Model grid: ' + GRD)

                for PFX in PFXS:
                    print(INDT * 5 + 'Stat prefix: ' + PFX)

                    if MEM_ID == '':
                        mem_id = ''
                    else:
                        mem_id = '/' + MEM_ID

                    if GRD == '':
                        grd = ''
                    else:
                        grd = '/' + GRD

                    # storage for configuration settings as arguments of makeDataFrames
                    # the function definition and role of these arguments are in the
                    # next section directly below
                    CFG = []

                    # forecast zero hour date time
                    CFG.append(anl_strng)
    
                    # control flow / directory name
                    CFG.append(CTR_FLW)

                    # ensemble member ID
                    CFG.append(MEM_ID)
    
                    # grid to be processed
                    CFG.append(GRD)
    
                    # path to ASCII input cycle directories from IN_ROOT
                    DIR_NME = IN_ROOT + '/' + CTR_FLW + '/' + MET_TOOL
                    CFG.append(DIR_NME)
                    print(INDT * 5 + 'IN_DT_ROOT:')
                    print(INDT * 6 + DIR_NME)
                    
                    # path to ASCII outputs from cycle directory
                    DIR_NME = mem_id + grd
                    CFG.append(DIR_NME)
                    print(INDT * 5 + 'IN_DT_SUBDIR:')
                    print(INDT * 6 + DIR_NME)
    
                    # path to output pandas cycle directories from OUT_ROOT
                    DIR_NME = OUT_ROOT + '/' + CTR_FLW + '/' + MET_TOOL
                    CFG.append(DIR_NME)
                    print(INDT * 5 + 'OUT_DT_ROOT:')
                    print(INDT * 6 + DIR_NME)
    
                    # path to pandas outputs from cycle directory
                    DIR_NME = ''
                    CFG.append(DIR_NME)
                    print(INDT * 5 + 'OUT_DT_SUBDIR:')
                    print(INDT * 6 + DIR_NME)

                    # prefix for ASCII output generated by MET
                    print(INDT * 5 + 'ASCII file prefix:')
                    print(INDT * 6 + PFX)
                    CFG.append(PFX)

                    # append configuration to be mapped
                    CFGS.append(CFG)

##################################################################################
# Data processing routines
##################################################################################
#  function for multiprocessing parameter map
def makeDataFrames(cfg):
    # unpack argument list
    anl_strng, ctr_flw, mem_id, grid, in_dt_root, in_dt_subdir,\
            out_dt_root, out_dt_subdir, pfx = cfg

    # include underscore if ID / grid is of nonzero length
    if len(mem_id) > 0:
        mem = '_' + mem_id
    else:
        mem = ''

    if len(grid) > 0:
        grd = '_' + grid
    else:
        grd = ''

    log_dir = OUT_ROOT + '/batch_logs'
    os.system('mkdir -p ' + log_dir)

    with open(log_dir + '/DataFrame_' + pfx + '_' + ctr_flw + mem + grd +\
            '_' + anl_strng + '.log', 'w') as log_f:

        cmd = 'mkdir -p ' + out_dt_root
        print(cmd, file=log_f)
        os.system(cmd)
        
        # check for input / output root directory
        error = 0
        if not os.path.isdir(in_dt_root):
            print('ERROR: input data root directory ' + in_dt_root +\
                    ' does not exist.', file=log_f)
            error = 1
        
        # check for input / output root directory
        elif not os.path.isdir(out_dt_root):
            print('ERROR: output data root directory ' + out_dt_root +\
                    ' does not exist.', file=log_f)
            error = 1
        
        # initiate empty dictionary for storage of dataframes by keyname
        data_dict = {}
    
        # define the ASCII files to open based on the analysis date
        # looping the analysis times
        in_files = []
        for i_anl in range(anl_min, anl_max + anl_inc, anl_inc):
            in_dir = in_dt_root + '/' + anl_strng + in_dt_subdir 
           
            if not os.path.isdir(in_dir):
                print('ERROR: input data cycle directory ' + in_dir +\
                        ' does not exist.', file=log_f)
                error = 1
            
            in_glob = in_dir + '/' + pfx +'_' + str(i_anl) + '0000L' + '*.txt'
            print('Searching path pattern:\n' + INDT + in_glob, file=log_f)
            in_paths = sorted(glob.glob(in_glob))
            if len(in_paths) == 0:
                print(INDT + 'ERROR: no files match the pattern:', file=log_f)
                print(INDT * 2 + in_glob, file=log_f)
                error = 1
            else:
                for path in in_paths:
                    print(INDT + 'Found ' + path, file=log_f)
                    in_files += [ path ] 

            for in_file in in_files:
                print('Opening file ' + in_file, file=log_f)
    
                # cut the diagnostic type from file name
                fname = in_file.split('/')[-1]
                split_name = fname.split('_')
                postfix = split_name[-1].split('.')
                postfix = postfix[0]
    
                # open file, load column names, then loop lines
                with open(in_file) as f:
                    cols = f.readline()
                    cols = cols.split()
                    
                    if len(cols) > 0:
                        fname_df = {} 
                        tmp_dict = {}
                        df_indx = 1
    
                        print(INDT + 'Loading columns:', file=log_f)
                        for col_name in cols:
                            print(INDT * 2 + col_name, file=log_f)
                            fname_df[col_name] = [] 
    
                        fname_df = pd.DataFrame.from_dict(fname_df,
                                                          orient='columns')
    
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
                            tmp_dict = pd.DataFrame.from_dict(tmp_dict,
                                                              orient='columns')
                            fname_df = pd.concat([fname_df, tmp_dict], axis=0)
                            df_indx += 1
    
                        fname_df['line'] = fname_df['line'].astype(int)
                        
                        if postfix in data_dict.keys():
                            last_indx = data_dict[postfix].index[-1]
                            fname_df['line'] = fname_df['line'].add(last_indx)
                            fname_df = fname_df.set_index('line')
                            data_dict[postfix] = pd.concat([data_dict[postfix],
                                                            fname_df], axis=0)
    
                        else:
                            fname_df = fname_df.set_index('line')
                            data_dict[postfix] = fname_df
    

                    else:
                        print('ERROR: file ' + in_path + ' is empty.', file=log_f)
                        error = 1
    
                print('Closing file ' + in_file, file=log_f)
    
        if bool(data_dict):
            # define the output binary file for pickled dataframe per date
            out_dir = out_dt_root + '/' + anl_strng + out_dt_subdir 
            os.system('mkdir -p ' + out_dir)
            if not os.path.isdir(in_dir):
                print('ERROR: output data cycle directory ' + out_dir +\
                        ' does not exist.', file=log_f)
                error = 1

            out_path = out_dir + '/' + pfx + mem + grd + '_' + anl_strng + '.bin'
            print('Writing out data to ' + out_path, file=log_f)
            with open(out_path, 'wb') as f:
                pickle.dump(data_dict, f)
        cfg_nme = pfx + '_' + ctr_flw + mem + grd + '_' + anl_strng
        print(INDT + 'Completed:\n' + 2 * INDT + cfg_nme)
        return [cfg_nme, error]

##################################################################################
# Runs multiprocessing on parameter grid
##################################################################################
# infer available cpus for workers
n_workers = multiprocessing.cpu_count() - 1
print('Running makeDataFrames with ' + str(n_workers) + ' total workers.')

with Pool(n_workers) as pool:
    print(*pool.map(makeDataFrames, CFGS))

##################################################################################
# end
