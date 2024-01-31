##################################################################################
# Description
##################################################################################
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
from config_mpascf import *
from cdo import Cdo

##################################################################################
# file name paths are taken as script arguments
f_in = sys.argv[1]
f_out = sys.argv[2]

try:
    f_time = sys.argv[3]

except:
    f_time = None

# load datasets in xarray
ds_in = xr.open_dataset(f_in)

# extract cf precip
ds_out = cf_precip(ds_in, f_time)
ds_out.to_netcdf(path=f_out)

##################################################################################
