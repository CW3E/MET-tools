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
