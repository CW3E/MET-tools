#!/bin/bash
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
# take the file path for the convert_mpas singularity image from script argument
CONVERT_MPAS=$1

# take the work directory from script argument
WORK_DIR=$2

# take the mesh directory from script argument
IN_MSH_DIR=$3

# take the mesh file from script argument
IN_MSH_F=$4

# take the inputs directory from script argument
IN_DIR=$5

# take the input file from script argument
F_IN=$6

# 1 / 0 regrid precip fields True / False
PCP_PRD=$7

# 1 / 0 regrid IVT fields True / False
IVT_PRD=$8

printf "Running convert_mpas from singularity image:\n ${CONVERT_MPAS}\n"
printf "Work directory is:\n ${WORK_DIR}\n"
printf "Mesh input file path is:\n ${IN_MSH_DIR}/${IN_MSH_F}\n"
printf "Input file path is:\n ${IN_DIR}/${F_IN}\n"

# Regrid to generic lat-lon grid for MET, passed to convert_mpas tool
# NOTE: need to revise to regrid directly to verification grid
nlat=1500
nlon=2750
lat1=5.
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
if [ ${PCP_PRD} = 1 ]; then
  printf "rainc\n" >> ./include_fields
  printf "rainnc\n" >> ./include_fields
fi
if [ ${IVT_PRD} = 1 ]; then
  printf "pressure\n" >> ./include_fields
  printf "surface_pressure\n" >> ./include_fields
  printf "plrad\n" >> ./include_fields
  printf "qv\n" >> ./include_fields
  printf "uReconstructZonal\n" >> ./include_fields
  printf "uReconstructMeridional\n" >> ./include_fields
fi

# run convert mpas from singularity exec command
cmd="singularity exec --home ${WORK_DIR} -B"
cmd+=" ${IN_MSH_DIR}:/in_msh_dir:ro,${IN_DIR}:/in_dir:ro ${CONVERT_MPAS}"
cmd+=" convert_mpas /in_msh_dir/${IN_MSH_F} /in_dir/${F_IN}; error=$?"
printf "${cmd}\n"; eval "${cmd}"

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
  if [[ "${tmp_str}" = "${MPAS_PRFX}" ]]; then
    rename="${rename}latlon."
  else
    rename="${rename}${tmp_array[i]}."
  fi
done

rename="${rename}nc"

mv latlon.nc ${rename}

exit 0

##################################################################################
