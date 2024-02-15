#!/bin/bash
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
# take the file path for the convert_mpas singularity image from script argument
CONVERT_MPAS=$1

# take the work directory from script argument
WORK_DIR=$2

# take the inputs directory from script argument
IN_DIR=$3

# take the input file from script argument
F_IN=$4

# Regrid to generic lat-lon grid for MET, passed to convert_mpas tool
# NOTE: need to revise to regrid directly to verification grid
nlat=750
nlon=1375
lat1=4.96
lat2=65.
lon1=162.
lon2=272.

# clean up old configuration files
rm -f ./target_domain
rm -f ./include_fields

# clean up old lalon files
rm -f latlon.nc

# set domain parameters from configuration file
printf "nlat = ${nlat}\n" >> ./target_domain
printf "nlon = ${nlon}\n" >> ./target_domain
printf "startlat = ${lat1}\n" >> ./target_domain
printf "startlon = ${lon1}\n" >> ./target_domain
printf "endlat = ${lat2}\n" >> ./target_domain
printf "endlon = ${lon2}\n" >> ./target_domain

# set fields to be regridded
printf "rainc\n" >> ./include_fields
printf "rainnc\n" >> ./include_fields

# run convert mpas from singularity exec command
singularity exec --home ${WORK_DIR} -B ${IN_DIR}:/in_dir:ro ${CONVERT_MPAS} convert_mpas /in_dir/${F_IN}
error=$?

# remove link / configuration files
rm -f ./target_domain
rm -f ./include_fields

# check exit status
if [ ${error} -ne 0 ]; then
  printf "ERROR: convert_mpas did not complete successfully.\n"
  exit 1
fi

# replace history / diag from input file name with latlon, mv output to name
f_in=`basename ${F_IN}`
IFS="." read -ra tmp_array <<< "$f_in"
str_len=$(( ${#tmp_array[@]} - 1 ))
rename=""
for (( i = 0 ; i < ${str_len} ; i ++ )); do
  tmp_str=${tmp_array[i]}
  if [[ ${tmp_str} = "history" || ${tmp_str} = "diag" ]]; then
    rename="${rename}latlon."
  else
    rename="${rename}${tmp_array[i]}."
  fi
done

rename="${rename}nc"

mv latlon.nc ${rename}

exit 0

##################################################################################
