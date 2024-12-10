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
from MPAS_cf import *

##################################################################################
# file name paths are taken as script arguments
f_in = sys.argv[1]
f_out = sys.argv[2]

try:
    pcp_prd = bool(int(sys.argv[3]))
except:
    print('ERROR: precipitation product flag must be set to 0 or 1')
    sys.exit(1)

try:
    ivt_prd = bool(int(sys.argv[4]))
except:
    print('ERROR: IVT product flag must be set to 0 or 1')
    sys.exit(1)

try:
    # optionally provide file path to derive time information from
    f_time = sys.argv[5]
except:
    f_time = None

# load datasets in xarray
ds_in = xr.open_dataset(f_in)
ds_out = xr.Dataset()

if pcp_prd:
    ds_precip = cf_precip(ds_in, f_time)
    ds_out = xr.merge(ds_precip, ds_out)

if ivt_prd:
    ds_ivt = cf_ivt(ds_in, f_time)
    ds_out = xr.merge(ds_ivt, ds_out)

ds_out.to_netcdf(path=f_out)

##################################################################################
