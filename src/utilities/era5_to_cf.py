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
from ERA5_cf import *
import ipdb

##################################################################################
# Define script parameters
##################################################################################
f_in = '/p/work2/cgrudz/test/ERA5_2023-03-10T00_to_2023-03-15T23.grib'
f_out_dir = '/p/work2/cgrudz/DATA/VERIFICATION_STATIC/ERA5/valid_date_2023-03-15T00'
anl_inc = 6

#print('Splitting file:')
#print(INDT + f_in)
#print('to outputs in directory:')
#print(INDT + f_out_dir)
#print('with averages taken on ' + str(anl_inc) + ' hour intervals.')
#
## split the large grib into dates and return list of files
##f_list = split_grib_on_dates(f_in, f_out_dir, 'ERA5-datesplit')
f_list = sorted(glob.glob(f_out_dir + '/ERA5-datesplit*'))

avg_list = []
for i_f, fname in enumerate(f_list):
    date = fname.split('_')[-1]
    ds_in = xr.open_dataset(fname)
    ds_out = cf_ivt(ds_in)
    f_out = f_out_dir + '/ERA5_00IVT_' + date
    ds_out.to_netcdf(path=f_out)
    print('Created instantaneous IVT file:')
    print(INDT + f_out)
    avg_list.append(f_out)

    if i_f % anl_inc == 0 and not i_f == 0:
        f_range = avg_list[i_f - anl_inc: i_f + 1]
        f_out = average_ivt(f_range)
        print('Created averaged IVT file:')
        print(INDT + f_out)

print('Completed splitting file for IVT outputs.')
#print('Removing temporary split files.')
#os.system('rm ' + f_out_dir + '/ERA5-datesplit*')

##################################################################################
