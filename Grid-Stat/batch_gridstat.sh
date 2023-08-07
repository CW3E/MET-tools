#!/bin/bash
#SBATCH -p shared
#SBATCH --nodes=1
#SBATCH --mem=120G
#SBATCH -t 02:30:00
#SBATCH -J batch_gridstat
#SBATCH --export=ALL
#SBATCH --array=0-1
##################################################################################
# Description
##################################################################################
# This script utilizes SLURM job arrays to batch process collections of cf
# compliant, preprocessed WRF outputs and / or preprocessed global model data
# using the MET Grid-Stat tool. This script is designed to set the parameters for
# the companion run_gridstat.sh script as a job array map, allowing batch
# processing over multiple configurations and valid dates with a single call.
##################################################################################
# License Statement
##################################################################################
#
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

# Using GMT time zone for time computations
export TZ="GMT"

# Root directory for MET-tools git clone
export USR_HME=/cw3e/mead/projects/cwp106/scratch/cgrudzien/MET-tools

# define the case-wise sub-directory
export CSE=CL

# Root directory for verification data
export DATA_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/DATA/${CSE}/verification/StageIV

# Root directory for MET software
export SOFT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/SOFT_ROOT/MET_CODE
export MET_SNG=${SOFT_ROOT}/met-10.0.1.simg

# Root directory for landmasks and lat-lon text files
export MSK_ROOT=${USR_HME}/polygons

# Path to file with list of landmasks for verification regions
export MSKS=${MSK_ROOT}/mask-lists/West_Coast_MaskList.txt
            
# Root directory of regridded .nc landmasks on StageIV domain
export MSK_IN=${MSK_ROOT}/West_Coast_Masks

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=1.0, >=10.0, >=25.0, >=50.0 ]"

# array of control flow names to be processed
CTR_FLWS=( 
          "GFS"
          "ECMWF"
         )

# NOTE: the grids in the GRDS array and the interpolation methods /
# neighborhbood widths in the below INT_MTHDS and INT_WDTHS must be
# in 1-1 correspondence to define the interpolation method / width
# specific to each grid
GRDS=( 
      ""
     )

# define the interpolation method and related parameters
INT_MTHDS=( 
           "DW_MEAN"
          )
INT_WDTHS=( 
           "3"
          )

# define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2020020200
export END_DT=2020020600

# define the interval between forecast initializations (HH)
export CYC_INT=24

# define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=120

# define the interval at which to process forecast outputs (HH)
export ANL_INT=24

# define the accumulation interval for verification valid times
export ACC_INT=24

# define the verification field
export VRF_FLD=QPF

# neighborhood width for neighborhood methods
export NBRHD_WDTH=9

# number of bootstrap resamplings, set 0 for off
export BTSTRP=1000

# rank correlation computation flag, TRUE or FALSE
export RNK_CRR=FALSE

# compute accumulation from cf file, TRUE or FALSE
export CMP_ACC=FALSE

# optionally define a gridstat output prefix, use a blank string for no prefix
export PRFX=""

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
export IN_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/DATA/${CSE}/verification/

# root directory for cycle time (YYYYMMDDHH) directories of gridstat outputs
export OUT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/tuning_figs/gridstat/${CSE}

##################################################################################
# Contruct job array and environment for submission
##################################################################################
# create array of arrays to store the hyper-parameter grid settings, configs
# run based on SLURM job array index
cfgs=()

num_grds=${#GRDS[@]}
num_flws=${#CTR_FLWS[@]}
for (( i = 0; i < ${num_grds}; i++ )); do
  for (( j = 0; j < ${num_flws}; j++ )); do
    CTR_FLW=${CTR_FLWS[$j]}
    GRD=${GRDS[$i]}
    INT_MTHD=${INT_MTHDS[$i]}
    INT_WDTH=${INT_WDTHS[$i]}

    cfg_indx="cfg_${i}${j}"
    cmd="${cfg_indx}=()"
    printf "${cmd}\n"; eval ${cmd}

    cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
    printf "${cmd}\n"; eval ${cmd}

    cmd="${cfg_indx}+=(\"GRD=${GRD}\")"
    printf "${cmd}\n"; eval ${cmd}

    cmd="${cfg_indx}+=(\"INT_MTHD=${INT_MTHD}\")"
    printf "${cmd}\n"; eval ${cmd}

    cmd="${cfg_indx}+=(\"INT_WDTH=${INT_WDTH}\")"
    printf "${cmd}\n"; eval ${cmd}

    cmd="${cfg_indx}+=(\"IN_CYC_DIR=${IN_ROOT}/${CTR_FLW}\")"
    printf "${cmd}\n"; eval ${cmd}

    cmd="${cfg_indx}+=(\"OUT_CYC_DIR=${OUT_ROOT}/${CTR_FLW}\")"
    printf "${cmd}\n"; eval ${cmd}

    # subdirectory of cycle-named directory containing data to be analyzed,
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=/\"\"\")"
    printf "${cmd}\n"; eval ${cmd}
    
    # subdirectory of cycle-named directory where output is to be saved
    cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=/\"\"\")"
    printf "${cmd}\n"; eval ${cmd}

    cmd="cfgs+=( \"${cfg_indx}\" )"
    printf "${cmd}\n"; eval ${cmd}

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

cmd="cd ${USR_HME}/Grid-Stat"
printf ${cmd}; eval ${cmd}

log_dir=${OUT_ROOT}/batch_logs
cmd="mkdir -p ${log_dir}"
printf ${cmd}; eval ${cmd}

cmd="./run_gridstat.sh ${!job} > ${log_dir}/gridstat_${jbid}_${indx}.log 2>&1"
printf ${cmd}; eval ${cmd}

##################################################################################
# end

exit 0
