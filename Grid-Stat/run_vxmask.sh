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
#################################################################################
# READ WORKFLOW PARAMETERS
#################################################################################
# make checks for workflow parameters
# these parameters are shared with run_wrfout_cf.sh

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


# Landmasks for verification region file name with extension
if [ ! -r ${MSKS} ]; then
  echo "ERROR: landmask list file \${MSKS} does not exist or is not readable."
  exit 1
fi

if [ ! ${MSK_ROOT} ]; then
  echo "ERROR: landmask root directory \${MSK_ROOT} is not defined."
  exit 1
fi

if [ ! ${MSK_OUT} ]; then
  echo "ERROR: landmask output directory \${MSK_OUT} is not defined."
  exit 1
fi

# loop lines of the mask file, set temporary exit status before searching for masks
estat=0
while read msk; do
  fpath=${MSK_ROOT}/${msk}
  # check for watershed lat-lon and mask files
  if [ -r "${fpath}.txt" ]; then
    echo "Found ${fpath}.txt lat-lon file."
  fi
  if [ -r "${fpath}_mask_regridded_with_StageIV.nc" ]; then
    echo "Found ${fpath}_mask_regridded_with_StageIV.nc landmask." 
  fi

  # if neither lat-lon nor mask files exist
  if [[ ! -r "${fpath}.txt" && ! -r "${fpath}_mask_regridded_with_StageIV.nc" ]]; then
    msg="ERROR: verification region landmask, ${fpath}, lat-lon .txt files and"
    msg+="regridded StageIV .nc files do not exist or or are not readable."
    echo ${msg}

    # create exit status flag to kill program, after checking all files in list
    estat=1
  fi
done <${MSKS}

if [ ${estat} -eq 1 ]; then
  msg="ERROR: Exiting due to missing land-masks, please see the above error "
  msg+="messages and verify the location for these files."
  exit 1
fi


