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
ds_in = xr.open_dataset(f_in)

# extract cf precip
ds_out = cf_precip(ds_in)
ds_out.to_netcdf(path=f_out)

if rgrd:
    # use CDO for regridding the data for MET compatibility
    cdo = Cdo()
    rgr_ds = cdo.sellonlatbox(LON1, LON2, LAT1, LAT2,
            input=cdo.remapbil(GRES, input=f_out,
                returnXarray='precip'),
            returnXarray='precip',  options='-f nc4' )

    rgr_ds = xr.open_dataset(rgr_ds)
    tmp_ds = xr.open_dataset(f_out)
    rgr_ds['forecast_reference_time'] = tmp_ds.forecast_reference_time
    os.system('rm -f ' + f_out)
    rgr_ds.to_netcdf(path=f_out)

##################################################################################
