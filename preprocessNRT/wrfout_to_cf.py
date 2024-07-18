##################################################################################
# Description
##################################################################################
# This script utilizes methods in the config_wrfcf module and CDO Python wrappers
# to postprocess wrfout files into cf-compliant NetCDF files compatible with MET.  
# If the native WRF grid is not compatible with MET, optionally the CDO wrappers
# will regrid the data into a lat-lon grid with parameters defined below.
#
# This is based on NCL script wrfout_to_cf.ncl of Mark Seefeldt and others:
#
#    http://foehn.colorado.edu/wrfout_to_cf/
#
# Regridding method for WRF is based on original code from Dan Steinhoff.
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
from config_wrfcf import *
import sys
from cdo import Cdo

##################################################################################

# file name paths are taken as script arguments
f_in = sys.argv[1]
f_out = sys.argv[2]

try:
    # check for optional regridding argument (1/0), convert to bool
    rgrd = bool(int(sys.argv[3]))

except:
    # no regridding unless specified
    print('Regridding option not specified or not integer, must be 1 or 0.')
    print('Defaulting to regridding - False.')
    rgrd = False

# load dataset in xarray
#ds_in = xr.open_dataset(f_in)

# extract cf precip
#ds_out = cf_precip(ds_in)
#ds_out.to_netcdf(path=f_out)

if rgrd:
    # use CDO for regridding the data for MET compatibility
    cdo = Cdo()
    rgr_ds = cdo.sellonlatbox(LON1, LON2, LAT1, LAT2,
            input=cdo.remapbil(GRES, input=f_in,
                returnXarray='precip'),
            returnXarray='precip',  options='-f nc4' )

    rgr_ds = xr.open_dataset(rgr_ds)
    tmp_ds = xr.open_dataset(f_in)
    rgr_ds['forecast_reference_time'] = tmp_ds.forecast_reference_time
    os.system('rm -f ' + f_out)
    rgr_ds.to_netcdf(path=f_out)

##################################################################################
