#!/bin/bash

#PBS -q main
#PBS -A UCSD0047 
#PBS -l select=1:ncpus=128:mpiprocs=32
#PBS -l walltime=01:00:00
#PBS -N preprocessMPAS 
#PBS -o ./logs/preprocessMPAS-
#PBS -j oe 
#PBS -J 0-1

##################################################################################
# Description
##################################################################################
# This script batch preprocesses collections of MPAS model outputs in parallel
# with the HPC system scheduler. This script constructs a parameter map for
# run_mpas_preprocess.sh script as a job array, allowing batch processing over
# multiple configurations simultaneously.
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
# SET GLOBAL PARAMETERS
##################################################################################
# uncoment to make verbose for debugging
#set -x

# Source tool configuration
source ./config_preprocessMPAS.sh

# root directory for cycle time (YYYYMMDDHH) directories of MPAS output files
export IN_ROOT=${SIM_ROOT}/${CSE}

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant outputs
export OUT_ROOT=${VRF_ROOT}/${CSE}

##################################################################################
# Contruct job array and environment for submission
##################################################################################
# Create array of arrays to store the hyper-parameter map settings, configs
# run based on job array index.  NOTE: directory paths dependent on control
# flow, ensemble member and grid settings are defined dynamically IN THE BELOW and
# should be set in the loops.
#
##################################################################################
# storage for configuration array names in pseudo-multiarray
cfgs=()

num_flws=${#CTR_FLWS[@]}
num_mems=${#MEM_IDS[@]}

# NOTE: SLURM JOB ARRAY SHOULD HAVE INDICES CORRESPONDING TO EACH OF THE
# CONFIGURATIONS DEFINED BELOW
for (( i_f = 0; i_f < ${num_flws}; i_f++ )); do
  for (( i_m = 0; i_m < ${num_mems}; i_m++ )); do
    CTR_FLW=${CTR_FLWS[$i_f]}
    MEM=${MEM_IDS[$i_m]}

    cfg_indx="cfg_${i_f}${i_m}${i_g}"
    cmd="${cfg_indx}=()"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    # This path defines the location of each cycle directory relative to IN_ROOT
    cmd="${cfg_indx}+=(\"IN_DT_ROOT=${IN_ROOT}/${CTR_FLW}/ExtendedFC\")"
    printf "${cmd}\n"; eval "${cmd}"

    # subdirectory of cycle-named directory containing data to be analyzed,
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=/${MEM}\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    # This path defines the location of each cycle directory relative to OUT_ROOT
    cmd="${cfg_indx}+=(\"OUT_DT_ROOT=${OUT_ROOT}/${CTR_FLW}/Preprocess\")"
    printf "${cmd}\n"; eval "${cmd}"

    # subdirectory of cycle-named directory where output is to be saved
    cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=/${MEM}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"IN_MSH_DIR=${MSH_ROOT}/${CTR_FLW}\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    cmd="${cfg_indx}+=(\"IN_MSH_F=\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    cmd="cfgs+=( \"${cfg_indx}\" )"
    printf "${cmd}\n"; eval "${cmd}"
  done
done

##################################################################################
# run the processing script looping parameter arrays
jbid=${PBS_JOBID}
indx=${PBS_ARRAY_INDEX}

mv ./logs/preprocessMPAS- ./logs/preprocessMPAS_${jbid}_${indx}

printf "Processing data for job index ${indx}.\n"
printf "Loading configuration parameters ${cfgs[$indx]}:\n"

# extract the configuration key name corresponding to the slurm index
cfg=${cfgs[$indx]}
job="${cfg}[@]"

cmd="cd ${USR_HME}/preprocessMPAS"
printf "${cmd}\n"; eval "${cmd}"

log_dir=${OUT_ROOT}/batch_logs
cmd="mkdir -p ${log_dir}"
printf "${cmd}\n"; eval "${cmd}"

cmd="./run_preprocessMPAS.sh ${!job} \
  > ${log_dir}/preprocessMPAS_${jbid}_${indx}.log 2>&1"
printf "${cmd}\n"; eval "${cmd}"

##################################################################################
# end

exit 0
