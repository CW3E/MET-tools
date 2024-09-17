#!/bin/bash
#################################################################################
# Description
#################################################################################
# The purpose of this script is to compute grid landmasks using MET for
# performing verification over prescribed regions, using lat-lon text files
# defining the region and the StageIV grid for verification. This script is
# based on original source code provided by Rachel Weihs, Caroline Papadopoulos
# and Daniel Steinhoff. This is re-written to homogenize project structure and
# to include error handling, process logs and additional flexibility with batch
# processing.
#
#################################################################################
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
#################################################################################
# CHECK WORKFLOW PARAMETERS
#################################################################################
# Full path to BASH constants used in driver scripts
if [ ! -x ${CNST} ]; then
  printf "ERROR: constants file\n ${CNST}\n does not exist or is not executable.\n"
  exit 1
else
  # Read constants into the current shell
  cmd=". ${CNST}"
  printf "${cmd}\n"; eval "${cmd}"
fi

# List of landmasks for verification region, file name with extension
if [ ! ${MSK_LST} ]; then
  printf "ERROR: landmask list \${MSK_LIST} is not defined.\n"
  exit 1
elif [ ! -r ${MSK_LST} ]; then
  msg="ERROR: landmask list\n ${MSK_LST}\n does not exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

# Root dir for text files with lat-lon coordinates for region polygons
if [ ! ${MSK_LTLN} ]; then
  printf "ERROR: landmask lat-lon file root directory \${MSK_LTLN} is not defined.\n"
  exit 1
elif [ ! -r ${MSK_LTLN} ]; then
  msg="ERROR: landmask lat-lon file root directory\n ${MSK_LTLN}\n does not "
  msg+="exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

# loop lines of the mask file, set temporary exit status before looping
estat=0
while read msk; do
  in_path=${MSK_LTLN}/${msk}.txt
  # check for lat-lon files
  if [ -r "${in_path}" ]; then
    printf "Found\n ${in_path}\n lat-lon file.\n"
  else
    msg="ERROR: verification region landmask\n ${in_path}\n lat-lon file "
    msg+="does not exist or is not readable.\n"
    printf "${msg}"

    # create exit status flag to kill program, after checking all files in list
    estat=1
  fi
done <${MSK_LST}

if [ ${estat} -eq 1 ]; then
  msg="ERROR: Exiting due to missing landmasks, please see the above error "
  msg+="messages and verify the location for these files.\n"
  printf "${msg}"
  exit 1
fi

if [ ! ${MSK_GRDS} ]; then
  printf "ERROR: landmask output directory \${MSK_GRDS} is not defined.\n"
  exit 1
else
  cmd="mkdir -p ${MSK_GRDS}"
  printf "${cmd}\n"; eval "${cmd}"
fi

# Postfix to add to generated mask files identifying the underlying grid
if [ ! ${GRD_NME} ]; then
  printf "ERROR: grid name \${GRD_NME} is not defined.\n"
  exit 1
fi

if [ ! ${STC_ROOT} ]; then
  msg="ERROR: verification static file root directory \${STC_ROOT}"
  msg+=" is not defined\n"
  printf "${msg}"
  exit 1
elif [ ! -d ${STC_ROOT} ]; then
  msg="ERROR: verification static files root\n ${STC_ROOT}\n does not exist"
  msg+=" or is not readable.\n"
  printf "${msg}"
  exit 1
elif [ ! ${GRD_IN} ]; then
  printf "ERROR: grid reference file \${GRD_IN} is not defined.\n"
  exit 1
elif [ ! -r ${STC_ROOT}/${GRD_IN} ]; then
  msg="ERROR: reference file\n ${STC_ROOT}/${GRD_IN}\n does not exist"
  msg+=" or is not readable.\n"
  printf "${msg}"
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# Set up singularity container with specific directory privileges
cmd="singularity instance start -B ${STC_ROOT}:/STC_ROOT:ro,"
cmd+="${MSK_LTLN}:/MSK_LTLN:ro,${MSK_GRDS}:/MSK_GRDS:rw ${MET} MET"
printf "${cmd}\n"; eval "${cmd}"

while read msk; do
  # masks are recreated depending on the existence of files from previous analyses
  out_path=${MSK_GRDS}/${msk}_StageIVGrid.nc
  if [ ! -r "${out_path}" ]; then
    # regridded mask does not exist in mask out, create from scratch
    cmd="singularity exec instance://MET gen_vx_mask -v 10 \
    /STC_ROOT/${GRD_IN} \
    -type poly /MSK_LTLN/${msk}.txt \
    /MSK_GRDS/${msk}_${GRD_NME}.nc"
    printf "${cmd}\n"; eval "${cmd}"
  else
    # mask exists and is readable, skip this step
    msg="Land mask\n ${out_path}\n already exists in\n ${MSK_GRDS}\n "
    msg+="skipping this region.\n"
    printf "${msg}"
  fi
done<${MSK_LST}

# End MET Process and singularity stop
cmd="singularity instance stop MET"
printf "${cmd}\n"; eval "${cmd}"

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at MSK_GRDS:\n ${MSK_GRDS}\n"
printf "${msg}"

#################################################################################
# end

exit 0
