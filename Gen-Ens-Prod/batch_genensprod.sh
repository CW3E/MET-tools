#!/bin/bash
#SBATCH --account=ddp181
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=120G
#SBATCH -p shared
#SBATCH -t 01:00:00
#SBATCH -J batch_genensprod
#SBATCH -o ./logs/batch_genensprod-%A_%a.out
#SBATCH --export=ALL
#SBATCH --array=0-1
##################################################################################
# Description
##################################################################################
# This script utilizes SLURM job arrays to batch process collections of cf
# the companion run_genensprod.sh script as a job array map, allowing batch
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

# Source configuration files to define majority of required variables
source ../MET-tools_config.sh
source ./GenEnsProd_config.sh

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
export IN_ROOT=${VRF_ROOT}/${CSE}

# root directory for cycle time (YYYYMMDDHH) directories of gridstat outputs
export OUT_ROOT=${VRF_ROOT}/${CSE}

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
num_grds=${#GRDS[@]}
for (( i_f = 0; i_f < ${num_flws}; i_f++ )); do
  for (( i_g = 0; i_g < ${num_grds}; i_g++ )); do
    CTR_FLW=${CTR_FLWS[$i_f]}
    GRD=${GRDS[$i_g]}
				NBRHD_WDTH=${NBRHD_WDTHS[$i_g]}

    cfg_indx="cfg_${i_f}${i_g}"
    cmd="${cfg_indx}=()"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"NBRHD_WDTH=${NBRHD_WDTH}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"IN_CYC_DIR=${IN_ROOT}/${CTR_FLW}/Preprocess\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"OUT_CYC_DIR=${OUT_ROOT}/${CTR_FLW}/GenEnsProd\")"
    printf "${cmd}\n"; eval "${cmd}"

    # subdirectory of cycle-named directory containing data to be analyzed,
				# leading to ensemble indexed directory
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=\"\"\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    # subdirectory of cycle-named directory where output is to be saved
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=/${GRD}\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    # subdirectory of ensemble indexed directory for input data
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_ENS_SUBDIR=/${GRD}\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    cmd="cfgs+=( \"${cfg_indx}\" )"
    printf "${cmd}\n"; eval "${cmd}"
  done
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

cmd="cd ${USR_HME}/Gen-Ens-Prod"
printf "${cmd}\n"; eval "${cmd}"

log_dir=${OUT_ROOT}/batch_logs
cmd="mkdir -p ${log_dir}"
printf "${cmd}\n"; eval "${cmd}"

cmd="./run_genensprod.sh ${!job} > ${log_dir}/genensprod_${jbid}_${indx}.log 2>&1"
printf "${cmd}\n"; eval "${cmd}"

##################################################################################
# end

exit 0
