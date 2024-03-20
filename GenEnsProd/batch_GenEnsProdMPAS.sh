#!/bin/bash
#PBS -q main
#PBS -A UCSD0047 
#PBS -l select=1:ncpus=128:mpiprocs=32
#PBS -l walltime=01:00:00
#PBS -N GenEnsProdMPAS 
#PBS -o ./logs/GenEnsProdMPAS.out
#PBS -j oe 
#PBS -J 0-1
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

# Source GenEnsProd parameters for processing MPAS data
source ./config_GenEnsProdMPAS.sh

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
export IN_ROOT=${VRF_ROOT}/${CSE}

# root directory for cycle time (YYYYMMDDHH) directories of gridstat outputs
export OUT_ROOT=${VRF_ROOT}/${CSE}

# set number of openmpi threads
export OMP_NUM_THREADS=16

##################################################################################
# Contruct job array and environment for submission
##################################################################################
# Create array of arrays to store the hyper-parameter grid settings, configs
# run based on SLURM job array index.  NOTE: directory paths dependent on control
# flow, ensemble member and grid settings are defined dynamically in the below and
# should be set in the loops.
##################################################################################
# Convert STRT_DT from 'YYYYMMDDHH' format to strt_dt Unix date format
if [[ ! ${STRT_DT} =~ ${ISO_RE} ]]; then
  msg="ERROR: start date \${STRT_DT}\n ${STRT_DT}\n"
  msg+=" is not in YYYYMMDDHH format.\n"
  printf "${msg}"
  exit 1
else
  strt_dt="${STRT_DT:0:8} ${STRT_DT:8:2}"
  strt_dt=`date -d "${strt_dt}"`
fi

# Convert STOP_DT from 'YYYYMMDDHH' format to stop_dt Unix date format 
if [[ ! ${STOP_DT} =~ ${ISO_RE} ]]; then
  msg="ERROR: stop date \${STOP_DT}\n ${STOP_DT}\n"
  msg+=" is not in YYYYMMDDHH format.\n"
  printf "${msg}"
  exit 1
else
  stop_dt="${STOP_DT:0:8} ${STOP_DT:8:2}"
  stop_dt=`date -d "${stop_dt}"`
fi

# define the number of dates to loop
cyc_hrs=$(( (`date +%s -d "${stop_dt}"` - `date +%s -d "${strt_dt}"`) / 3600 ))

# storage for configuration array names in pseudo-multiarray
cfgs=()

num_flws=${#CTR_FLWS[@]}
for (( i_f = 0; i_f < ${num_flws}; i_f++ )); do
  i_c=0
  for (( cyc_hr = 0; cyc_hr <= ${cyc_hrs}; cyc_hr += ${CYC_INC} )); do
    # directory string for forecast analysis initialization time
    cyc_dt=`date +%Y%m%d%H -d "${strt_dt} ${cyc_hr} hours"`

    CTR_FLW=${CTR_FLWS[$i_f]}

    cfg_indx="cfg_${i_f}${i_c}"
    cmd="${cfg_indx}=()"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"FULL_ENS=${FULL_ENS}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"CYC_DT=${cyc_dt}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"NBRHD_WDTH=${NBRHD_WDTH}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"IN_DT_ROOT=${IN_ROOT}/${CTR_FLW}/Preprocess\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"OUT_DT_ROOT=${OUT_ROOT}/${CTR_FLW}/GenEnsProd\")"
    printf "${cmd}\n"; eval "${cmd}"

    # subdirectory of cycle-named directory containing data to be analyzed,
    # leading to ensemble indexed directory
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=\"\"\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    # subdirectory of cycle-named directory where output is to be saved
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=\"\"\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    # subdirectory of ensemble indexed directory for input data
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_ENS_SUBDIR=\"\"\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    cmd="cfgs+=( \"${cfg_indx}\" )"
    printf "${cmd}\n"; eval "${cmd}"

    i_c=$(( ${i_c} + 1 ))
  done
done

##################################################################################
# run the processing script looping parameter arrays
jbid=${PBS_JOBID}
indx=${PBS_ARRAY_INDEX}

mv ./logs/GenEnsProdMPAS.out ./logs/GenEnsProdMPAS_${jbid}_${indx}.out

printf "Processing data for job index ${indx}."
printf "Loading configuration parameters ${cfgs[$indx]}:"

# extract the confiugration key name corresponding to the slurm index
cfg=${cfgs[$indx]}
job="${cfg}[@]"

cmd="cd ${USR_HME}/GenEnsProd"
printf "${cmd}\n"; eval "${cmd}"

log_dir=${OUT_ROOT}/batch_logs
cmd="mkdir -p ${log_dir}"
printf "${cmd}\n"; eval "${cmd}"

cmd="./run_GenEnsProd.sh ${!job} > "
cmd+="${log_dir}/GenEnsProdMPAS_${jbid}_${indx}.log 2>&1"
printf "${cmd}\n"; eval "${cmd}"

##################################################################################
# end

exit 0
