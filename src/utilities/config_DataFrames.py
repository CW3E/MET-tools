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
import sys
import os
import re
import numpy as np
import pandas as pd
import pickle
import glob
from datetime import datetime as dt

##################################################################################
# UTILITY DEFINITIONS
##################################################################################
INDT = '    '

##################################################################################
# METHODS
##################################################################################

def makeDataFrames(prfx, in_dir, out_dir, log_f=None):

    """Parses ASCII files of MET outputs into Pandas data frames

    Inputs to the method are as follows:

        prfx    -- MET tool prefix for parsing ASCII files
        in_dir  -- full path to directory of MET ASCII outputs
        out_dir -- full path to directory of output binary
        log_f   -- optional full path to log file

    The method globs the input directory for patterns with the MET tool prefix
    and the forecast initialization date and converts all matching files into
    data frames stored in a pickled dictionary at the output path.  Different
    MET stat types are used as key names in the dictionary for the data frames.
    """

    # create trigger for handling errors
    error_check = 0

    # check for input / output root directory
    if not os.path.isdir(in_dir):
        print('ERROR: input data directory ' + in_dir +\
                ' does not exist.', file=log_f)
        error_check = 1
 
    # check for input / output root directory
    if not os.path.isdir(out_dir):
        print('ERROR: output data root directory ' + out_dir +\
                ' does not exist.', file=log_f)
        error_check = 1
 
    # initiate empty dictionary for storage of outputs by stat type
    data_dict = {}

    in_glob = in_dir + '/' + prfx +'_' + '*.txt'
    print('Searching path pattern:\n' + INDT + in_glob, file=log_f)

    # Sorting first on length to handle non-padded forecast hours in MET
    fnames = sorted(glob.glob(in_glob), key=lambda x:(len(x), x))
    if len(fnames) == 0:
        print(INDT + 'ERROR: no files match the pattern:', file=log_f)
        print(INDT * 2 + in_glob, file=log_f)
        error_check = 1
    else:
        for fname in fnames:
            print(INDT + 'Found ' + fname, file=log_f)

    for fname in fnames:
        print('Opening file ' + fname, file=log_f)

        # cut the diagnostic type from file name
        split_name = fname.split('/')[-1]
        split_name = split_name.split('_')
        postfix = split_name[-1].split('.')
        postfix = postfix[0]
 
        # open file, load column names, then loop lines
        with open(fname) as f:
            cols = f.readline()
            cols = cols.split()
 
            if len(cols) > 0:
                tmp_dict = {}
 
                print(INDT + 'Loading columns:', file=log_f)
                for col in cols:
                    print(INDT * 2 + col, file=log_f)
                    tmp_dict[col] = [] 
 
                # parse file by line, concatenating columns
                for line in f:
                    split_line = line.split()
 
                    for i_v, val in enumerate(split_line):
                        if val == 'NA':
                            # filter NA vals
                            val = np.nan
                        tmp_dict[cols[i_v]].append(val)
 
                if postfix in data_dict.keys():
                    for col in tmp_dict.keys():
                        data_dict[postfix][col] = data_dict[postfix][col] +\
                                tmp_dict[col]

                else:
                    data_dict[postfix] = tmp_dict

            else:
                print('ERROR: file ' + in_path + ' is empty.', file=log_f)
                error_check = 1

        print('Closing file ' + fname, file=log_f)
    
    if bool(data_dict):
        # re-define the stored dictionaries as dataframes
        for key in data_dict.keys():
            data_dict[key] = pd.DataFrame.from_dict(data_dict[key], 
                    orient='columns')

        # define the output binary file for pickled dataframe per date
        out_path = out_dir + '/' + prfx + '.bin'
        print('Writing out data to ' + out_path, file=log_f)
        with open(out_path, 'wb') as f:
            pickle.dump(data_dict, f)

    return error_check

##################################################################################
# end
