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
# The purpose of this script is to compute grid land masks using MET for
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
# Copyright 2023 Colin Grudzien, cgrudzien@ucsd.edu
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

# Root directory for MET-tools git clone
USR_HME=/cw3e/mead/projects/cwp106/scratch/MET-tools

# Root directory for verification data
DATA_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/DATA/VD/verification/StageIV
#DATA_ROOT=/cw3e/mead/projects/cnt102/METMODE_PreProcessing/data/StageIV

# Root directory for MET software
SOFT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/SOFT_ROOT/MET_CODE
MET_SNG=${SOFT_ROOT}/met-10.0.1.simg

# Root directory for landmasks, must contain lat-lon .txt files or regridded .nc
MSK_ROOT=${SOFT_ROOT}/polygons/workflow_test

# Path to file with list of landmasks for verification regions
MSKS=${SOFT_ROOT}/polygons/Test_MaskList.txt
            
# Output directory for land masks
MSK_OUT=${SOFT_ROOT}/polygons/workflow_test_out

# define path to StageIV data product for reference verfication grid 
# an arbitrary file with the correct grid is sufficient
OBS_F_IN=StageIV_QPE_2019021500.nc

#################################################################################
# CHECK WORKFLOW PARAMETERS
#################################################################################
# make checks for workflow parameters, should be defined in the above section

# define the working scripts directory
if [ ! ${USR_HME} ]; then
  echo "ERROR: MET-tools clone directory \${USR_HME} is not defined."
  exit 1
elif [ ! -d ${USR_HME} ]; then
  echo "ERROR: MET-tools clone directory ${USR_HME} does not exist."
  exit 1
else
  script_dir=${USR_HME}/Grid-Stat
  if [ ! -d ${script_dir} ]; then
    echo "ERROR: Grid-Stat script directory ${script_dir} does not exist."
    exit 1
  fi
fi

# List of landmasks for verification region, file name with extension
if [ ! -r ${MSKS} ]; then
  echo "ERROR: landmask list file \${MSKS} does not exist or is not readable."
  exit 1
fi

if [ ! ${MSK_ROOT} ]; then
  echo "ERROR: landmask lat-lon file root directory \${MSK_ROOT} is not defined."
  exit 1
elif [ ! -r ${MSK_ROOT} ]; then
  msg="ERROR: landmask lat-lon file root directory does not exist or "
  msg+="is not readable."
  echo ${msg}
  exit 1
fi

# loop lines of the mask file, set temporary exit status before looping masks
estat=0
while read msk; do
  fpath=${MSK_ROOT}/${msk}
  # check for watershed lat-lon files
  if [ -r "${fpath}.txt" ]; then
    echo "Found ${fpath}.txt lat-lon file."
  else
    msg="ERROR: verification region landmask ${fpath}, lat-lon .txt file "
    msg+="does not exist or is not readable."
    echo ${msg}

    # create exit status flag to kill program, after checking all files in list
    estat=1
  fi
done <${MSKS}

if [ ${estat} -eq 1 ]; then
  msg="ERROR: Exiting due to missing landmasks, please see the above error "
  msg+="messages and verify the location for these files."
  exit 1
fi

if [ ! ${MSK_OUT} ]; then
  echo "ERROR: landmask output directory \${MSK_OUT} is not defined."
  exit 1
else
  cmd="mkdir -p ${MSK_OUT}"
  echo ${cmd}; eval ${cmd}
fi

#################################################################################
# Process data
#################################################################################
# Set up singularity container with specific directory privileges
cmd="singularity instance start -B ${MSK_ROOT}:/MSK_ROOT:ro,"
cmd+="${DATA_ROOT}:/DATA_ROOT:ro,${MSK_OUT}:/MSK_OUT:rw ${MET_SNG} met1"
echo ${cmd}; eval ${cmd}

while read msk; do
  # masks are recreated depending on the existence of files from previous analyses
  fpath=${MSK_OUT}/${msk}_mask_regridded_with_StageIV.nc
  if [ ! -r "${fpath}" ]; then
    # regridded mask does not exist in mask out, create from scratch
    cmd="singularity exec instance://met1 gen_vx_mask -v 10 \
    /DATA_ROOT/${OBS_F_IN} \
    -type poly \
    /MSK_ROOT/${msk}.txt \
    /MSK_OUT/${msk}_mask_regridded_with_StageIV.nc"
    echo ${cmd}; eval ${cmd}
  else
    # mask exists and is readable, skip this step
    msg="Land mask ${fpath} already exists in ${MSK_OUT}, skipping this region."
    echo ${msg}
  fi
done<${MSKS}

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at MSK_OUT ${MSK_OUT}"
echo ${msg}

#################################################################################
# end

exit 0
