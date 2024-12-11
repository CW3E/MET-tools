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
from WRF_cf import *
from cdo import Cdo

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
    # check for regridding (1/0), convert to bool
    rgrd = bool(int(sys.argv[5]))
except:
    # no regridding unless specified
    rgrd = False

try:
    # check for initialization offset value, e.g., for restart
    init_offset = int(sys.argv[6])
    print('Initialization times will be computed with an offset of minus ' +\
            str(init_offset) + ' hours.')

except:
    init_offset=0
    pass

# load dataset in xarray with empty output dataset to merge variables
ds_in = xr.open_dataset(f_in)
ds_out = global_attrs(xr.Dataset())

if pcp_prd:
    ds_precip = cf_precip(ds_in, init_offset=init_offset)
    ds_out = ds_out.merge(ds_precip)

if ivt_prd:
    ds_ivt = cf_ivt(ds_in, init_offset=init_offset)
    ds_out = ds_out.merge(ds_ivt)

ds_out.to_netcdf(path=f_out)

if rgrd:
    # use CDO for regridding the data for MET compatibility
    cdo = Cdo()
    rgrd_ds = cdo.sellonlatbox(LON1, LON2, LAT1, LAT2,
            input=cdo.remapbil(GRES, input=f_out, returnXDataset=True),
            returnXDataset=True, options='-f nc4' )

    tmp_ds = xr.open_dataset(f_out)
    rgrd_ds['forecast_reference_time'] = tmp_ds.forecast_reference_time
    os.system('rm -f ' + f_out)
    rgrd_ds.to_netcdf(path=f_out)

##################################################################################
