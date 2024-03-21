#!/bin/bash

#PBS -q main
#PBS -A UCSD0047 
#PBS -l select=1:ncpus=128:mpiprocs=32
#PBS -l walltime=03:00:00
#PBS -N GridStatMPAS 
#PBS -o ./logs/GridStatMPAS
#PBS -j oe 
#PBS -J 0-1
##################################################################################
# Description
##################################################################################
# This script utilizes SLURM job arrays to batch process collections of cf
# compliant, preprocessed MPAS outputs and / or preprocessed global model data
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
# RENAME LOG FILE
##################################################################################
mv ./logs/GridStatMPAS ./logs/GridStatMPAS_${PBS_JOBID}_${PBS_ARRAY_INDEX}
##################################################################################
# SET GLOBAL PARAMETERS
##################################################################################
# uncoment to make verbose for debugging
#set -x

# Source configuration for gridstat MPAS
source ./config_GridStatMPAS.sh
source ../vxmask/config_vxmask.sh

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
export IN_ROOT=${VRF_ROOT}/${CSE}

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
num_mems=${#MEM_IDS[@]}
for (( i_f = 0; i_f < ${num_flws}; i_f++ )); do
  if [[ ${IF_ENS_MEAN} =~ ${TRUE} ]]; then
    CTR_FLW=${CTR_FLWS[$i_f]}
  
    cfg_indx="cfg_${i_f}${i_g}_mean"
    cmd="${cfg_indx}=()"
    printf "${cmd}\n"; eval "${cmd}"
  
    cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
    printf "${cmd}\n"; eval "${cmd}"
  
    cmd="${cfg_indx}+=(\"IF_ENS_PRD=TRUE\")"
    printf "${cmd}\n"; eval "${cmd}"
  
    cmd="${cfg_indx}+=(\"ENS_MIN=${ENS_MIN}\")"
    printf "${cmd}\n"; eval "${cmd}"
  
    cmd="${cfg_indx}+=(\"ENS_MAX=${ENS_MAX}\")"
    printf "${cmd}\n"; eval "${cmd}"
  
    cmd="${cfg_indx}+=(\"INT_WDTH=${INT_WDTH}\")"
    printf "${cmd}\n"; eval "${cmd}"
  
    cmd="${cfg_indx}+=(\"IN_DT_ROOT=${IN_ROOT}/${CTR_FLW}/GenEnsProd\")"
    printf "${cmd}\n"; eval "${cmd}"
  
    cmd="${cfg_indx}+=(\"OUT_DT_ROOT=${OUT_ROOT}/${CTR_FLW}/GridStat\")"
    printf "${cmd}\n"; eval "${cmd}"
  
    # subdirectory of cycle-named directory containing data to be analyzed,
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=\"\"\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    # subdirectory of cycle-named directory where output is to be saved
    cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=/mean/\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    cmd="cfgs+=( \"${cfg_indx}\" )"
    printf "${cmd}\n"; eval "${cmd}"

  fi

  if [[ ${IF_ENS_MEMS} =~ ${TRUE} ]]; then
    for (( i_m = 0; i_m < ${num_mems}; i_m++ )); do
      CTR_FLW=${CTR_FLWS[$i_f]}
      MEM=${MEM_IDS[$i_m]}
  
      cfg_indx="cfg_${i_g}${i_f}${i_m}"
      cmd="${cfg_indx}=()"
      printf "${cmd}\n"; eval "${cmd}"
  
      cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
      printf "${cmd}\n"; eval "${cmd}"
  
      cmd="${cfg_indx}+=(\"IF_ENS_PRD=FALSE\")"
      printf "${cmd}\n"; eval "${cmd}"
  
      cmd="${cfg_indx}+=(\"INT_WDTH=${INT_WDTH}\")"
      printf "${cmd}\n"; eval "${cmd}"
  
      cmd="${cfg_indx}+=(\"IN_DT_ROOT=${IN_ROOT}/${CTR_FLW}/Preprocess\")"
      printf "${cmd}\n"; eval "${cmd}"
  
      cmd="${cfg_indx}+=(\"OUT_DT_ROOT=${OUT_ROOT}/${CTR_FLW}/GridStat\")"
      printf "${cmd}\n"; eval "${cmd}"
  
      # subdirectory of cycle-named directory containing data to be analyzed,
      # includes leading '/', left as blank string if not needed
      cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=/${MEM}\")"
      printf "${cmd}\n"; eval "${cmd}"
      
      # subdirectory of cycle-named directory where output is to be saved
      cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=/${MEM}\")"
      printf "${cmd}\n"; eval "${cmd}"
      
      cmd="cfgs+=( \"${cfg_indx}\" )"
      printf "${cmd}\n"; eval "${cmd}"
  
    done
  fi
done

##################################################################################
# run the processing script looping parameter arrays
jbid=${PBS_JOBID}
indx=${PBS_ARRAY_INDEX}

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

cmd="./run_GridStat.sh ${!job} > ${log_dir}/GridStatMPAS_${jbid}_${indx}.log 2>&1"
printf "${cmd}\n"; eval "${cmd}"

##################################################################################
# end

exit 0
