#!/bin/bash
#SBATCH -p shared
#SBATCH --nodes=1
#SBATCH --mem=120G
#SBATCH -t 01:00:00
#SBATCH -J run_vxmask
#SBATCH --export=ALL
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
# License Statement
#################################################################################
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
# SET GLOBAL PARAMETERS
##################################################################################
# uncoment to make verbose for debugging
#set -x

# Source the configuration file to define majority of required variables
source pre_processing_config.sh
          
# Path to lat-lon text files for mask generation
MSK_IN=${MSK_ROOT}/lat-lon

#################################################################################
# CHECK WORKFLOW PARAMETERS
#################################################################################
# make checks for workflow parameters, should be defined in the above section

# define the working scripts directory
if [ ! ${USR_HME} ]; then
  printf "ERROR: MET-tools clone directory \${USR_HME} is not defined.\n"
  exit 1
elif [ ! -d ${USR_HME} ]; then
  printf $"ERROR: MET-tools clone directory\n ${USR_HME}\n does not exist.\n"
  exit 1
else
  script_dir=${USR_HME}/Grid-Stat
  if [ ! -d ${script_dir} ]; then
    printf "ERROR: Grid-Stat script directory\n ${script_dir}\n does not exist.\n"
    exit 1
  fi
fi

# List of landmasks for verification region, file name with extension
if [ ! -r ${MSKS} ]; then
  printf "ERROR: landmask list file \${MSKS} does not exist or is not readable.\n"
  exit 1
fi

if [ ! ${MSK_IN} ]; then
  printf "ERROR: landmask lat-lon file root directory \${MSK_IN} is not defined.\n"
  exit 1
elif [ ! -r ${MSK_IN} ]; then
  msg="ERROR: landmask lat-lon file root directory\n ${MSK_IN}\n does not "
  msg+="exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

# loop lines of the mask file, set temporary exit status before looping
estat=0
while read msk; do
  in_path=${MSK_IN}/${msk}.txt
  # check for watershed lat-lon files
  if [ -r "${in_path}" ]; then
    printf "Found\n ${in_path}\n lat-lon file.\n"
  else
    msg="ERROR: verification region landmask\n ${in_path}\n lat-lon file "
    msg+="does not exist or is not readable.\n"
    printf "${msg}"

    # create exit status flag to kill program, after checking all files in list
    estat=1
  fi
done <${MSKS}

if [ ${estat} -eq 1 ]; then
  msg="ERROR: Exiting due to missing landmasks, please see the above error "
  msg+="messages and verify the location for these files.\n"
  printf "${msg}"
  exit 1
fi

if [ ! ${MSK_OUT} ]; then
  printf "ERROR: landmask output directory \${MSK_OUT} is not defined.\n"
  exit 1
else
  cmd="mkdir -p ${MSK_OUT}"
  printf "${cmd}\n"; eval "${cmd}"
fi

#################################################################################
# Process data
#################################################################################
# Set up singularity container with specific directory privileges
cmd="singularity instance start -B ${MSK_ROOT}:/MSK_ROOT:ro,"
cmd+="${MSK_IN}:/MSK_IN:ro,${MSK_OUT}:/MSK_OUT:rw ${MET_SNG} met1"
printf "${cmd}\n"; eval "${cmd}"

while read msk; do
  # masks are recreated depending on the existence of files from previous analyses
  out_path=${MSK_OUT}/${msk}_mask_regridded_with_StageIV.nc
  if [ ! -r "${out_path}" ]; then
    # regridded mask does not exist in mask out, create from scratch
    cmd="singularity exec instance://met1 gen_vx_mask -v 10 \
    /MSK_ROOT/${OBS_F_IN} \
    -type poly \
    /MSK_IN/${msk}.txt \
    /MSK_OUT/${msk}_mask_regridded_with_StageIV.nc"
    printf "${cmd}\n"; eval "${cmd}"
  else
    # mask exists and is readable, skip this step
    msg="Land mask\n ${out_path}\n already exists in\n ${MSK_OUT}\n "
    msg+="skipping this region.\n"
    printf "${msg}"
  fi
done<${MSKS}

# End MET Process and singularity stop
cmd="singularity instance stop met1"
printf "${cmd}\n"; eval "${cmd}"

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at MSK_OUT:\n ${MSK_OUT}\n"
printf "${msg}"

#################################################################################
# end

exit 0
