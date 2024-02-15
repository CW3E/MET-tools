#!/bin/bash
#SBATCH --account=cwp157
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --mem=20G
#SBATCH -p cw3e-compute
#SBATCH -t 06:00:00
#SBATCH -J GridStat_BKG
#SBATCH -o ./logs/GridStatBKG-%A_%a.out
#SBATCH --export=ALL
#SBATCH --array=0-2
##################################################################################
# Description
##################################################################################
# This script utilizes SLURM job arrays to batch process collections of cf
# compliant, preprocessed WRF outputs and / or preprocessed global model data
# using the MET GridStat tool. This script is designed to set the parameters for
# the companion run_GridStat.sh script as a job array map, allowing batch
# processing over multiple configurations and valid dates with a single call.
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
# SET GLOBAL PARAMETERS
##################################################################################
# uncoment to make verbose for debugging
#set -x

# Source configuration for gridstat background global models
source ./config_GridStatBKG.sh
source ../vxmask/config_vxmask.sh

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
export IN_ROOT=${STC_ROOT}

# root directory for cycle time (YYYYMMDDHH) directories of gridstat outputs
export OUT_ROOT=${VRF_ROOT}/${CSE}

# set number of openmpi threads
export OMP_NUM_THREADS=128

##################################################################################
# Contruct job array and environment for submission
##################################################################################
# Create array of arrays to store the hyper-parameter grid settings, configs
# run based on SLURM job array index.  NOTE: directory paths dependent on control
# flow, ensemble member and grid settings are defined dynamically in the below and
# should be set in the loops.
##################################################################################
# storage for configuration array names in pseudo-multiarray
cfgs=()

num_flws=${#CTR_FLWS[@]}
for (( i_f = 0; i_f < ${num_flws}; i_f++ )); do
  CTR_FLW=${CTR_FLWS[$i_f]}
  INT_WDTH=${INT_WDTHS[$i_f]}
  
  cfg_indx="cfg_${i_f}"
  cmd="${cfg_indx}=()"
  printf "${cmd}\n"; eval "${cmd}"
  
  cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
  printf "${cmd}\n"; eval "${cmd}"
  
  cmd="${cfg_indx}+=(\"GRD=\"\"\")"
  printf "${cmd}\n"; eval "${cmd}"
  
  cmd="${cfg_indx}+=(\"IF_ENS_PRD=FALSE\")"
  printf "${cmd}\n"; eval "${cmd}"
  
  cmd="${cfg_indx}+=(\"INT_WDTH=${INT_WDTH}\")"
  printf "${cmd}\n"; eval "${cmd}"
  
  cmd="${cfg_indx}+=(\"IN_DT_ROOT=${IN_ROOT}/${CTR_FLW}/Precip\")"
  printf "${cmd}\n"; eval "${cmd}"
  
  cmd="${cfg_indx}+=(\"OUT_DT_ROOT=${OUT_ROOT}/${CTR_FLW}/GridStat\")"
  printf "${cmd}\n"; eval "${cmd}"
  
  # subdirectory of cycle-named directory containing data to be analyzed,
  # includes leading '/', left as blank string if not needed
  cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=\"\"\")"
  printf "${cmd}\n"; eval "${cmd}"
  
  # subdirectory of cycle-named directory where output is to be saved
  cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=\"\"\")"
  printf "${cmd}\n"; eval "${cmd}"
  
  cmd="cfgs+=( \"${cfg_indx}\" )"
  printf "${cmd}\n"; eval "${cmd}"
done

##################################################################################
# run the processing script looping parameter arrays
jbid=${SLURM_ARRAY_JOB_ID}
indx=${SLURM_ARRAY_TASK_ID}

printf "Processing data for job index ${indx}."
printf "Loading configuration parameters ${cfgs[$indx]}:"

# extract the confiugration key name corresponding to the slurm index
cfg=${cfgs[$indx]}
job="${cfg}[@]"

cmd="cd ${USR_HME}/GridStat"
printf "${cmd}\n"; eval "${cmd}"

log_dir=${OUT_ROOT}/batch_logs
cmd="mkdir -p ${log_dir}"
printf "${cmd}\n"; eval "${cmd}"

cmd="./run_GridStat.sh ${!job} > ${log_dir}/GridStatBKG_${jbid}_${indx}.log 2>&1"
printf "${cmd}\n"; eval "${cmd}"

##################################################################################
# end

exit 0
