#!/bin/bash
#SBATCH -p shared
#SBATCH --nodes=1
#SBATCH --mem=120G
#SBATCH -t 12:00:00
#SBATCH -J batch_gridstat
#SBATCH --export=ALL
#SBATCH --array=0-5
##################################################################################
# Description
##################################################################################
#
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
export USR_HME=/cw3e/mead/projects/cwp106/scratch/MET-tools

# Root directory for verification data
export DATA_ROOT=/cw3e/mead/projects/cnt102/METMODE_PreProcessing/data/StageIV

# Root directory for MET software
export SOFT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/SOFT_ROOT/MET_CODE
export MET_SNG=${SOFT_ROOT}/met-10.0.1.simg

# Root directory for landmasks, must contain lat-lon .txt files or regridded .nc
export MSK_ROOT=${SOFT_ROOT}/polygons/NRT

# Path to file with list of landmasks for verification regions
export MSKS=${SOFT_ROOT}/polygons/NRT_MaskList.txt
            
# Output directory for land masks if generated on the fly
export MSK_OUT=${SOFT_ROOT}/polygons/NRT

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=0.1, >=10.0, >=25.0, >=50.0 ]"

# array of control flow names to be processed
CTR_FLWS=( 
          "NRT_gfs"
          "NRT_ecmwf"
         )

# NOTE: the grids in the GRDS array and the interpolation methods /
# neighborhbood widths in the below INT_MTHDS and INT_WDTHS must be
# in 1-1 correspondence to define the interpolation method / width
# specific to each grid
GRDS=( 
      "d01"
      "d02"
      "d03"
     )

# define the interpolation method and related parameters
INT_MTHDS=( 
           "DW_MEAN"
           "DW_MEAN"
           "DW_MEAN"
          )
INT_WDTHS=( 
           "3"
           "9"
           "27"
          )

# define the case-wise sub-directory
export CSE=DeepDive

# define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2022121400
export END_DT=2023011800

# define the interval between forecast initializations (HH)
export CYC_INT=24

# define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=24
#export ANL_MAX=240

# define the interval at which to process forecast outputs (HH)
export ANL_INT=24

# define the accumulation interval for verification valid times
export ACC_INT=24

# define the verification field
export VRF_FLD=QPF

# neighborhood width for neighborhood methods
export NBRHD_WDTH=9

# number of bootstrap resamplings, set 0 for off
export BTSTRP=0

# rank correlation computation flag, TRUE or FALSE
export RNK_CRR=FALSE

# compute accumulation from cf file, TRUE or FALSE
export CMP_ACC=TRUE

# optionally define a gridstat output prefix, use a blank string for no prefix
export PRFX=""

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
export IN_ROOT=/cw3e/mead/projects/cwp106/scratch/${CSE}

# root directory for cycle time (YYYYMMDDHH) directories of gridstat outputs
export OUT_ROOT=/cw3e/mead/projects/cwp106/scratch/${CSE}

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
    echo ${cmd}; eval ${cmd}

    cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
    echo ${cmd}; eval ${cmd}

    cmd="${cfg_indx}+=(\"GRD=${GRD}\")"
    echo ${cmd}; eval ${cmd}

    cmd="${cfg_indx}+=(\"INT_MTHD=${INT_MTHD}\")"
    echo ${cmd} ; eval ${cmd}

    cmd="${cfg_indx}+=(\"INT_WDTH=${INT_WDTH}\")"
    echo ${cmd}; eval ${cmd}

    cmd="${cfg_indx}+=(\"IN_CYC_DIR=${IN_ROOT}/${CTR_FLW}\")"
    echo ${cmd}; eval ${cmd}

    cmd="${cfg_indx}+=(\"OUT_CYC_DIR=${OUT_ROOT}/${CTR_FLW}\")"
    echo ${cmd}; eval ${cmd}

    # subdirectory of cycle-named directory containing data to be analyzed,
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=/${GRD}\")"
    echo ${cmd}; eval ${cmd}
    
    # subdirectory of cycle-named directory where output is to be saved
    cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=/${GRD}\")"
    echo ${cmd}; eval ${cmd}

    cmd="cfgs+=( \"${cfg_indx}\" )"
    echo ${cmd}; eval ${cmd}

  done
done

##################################################################################
# run the processing script looping parameter arrays
jbid=${SLURM_ARRAY_JOB_ID}
indx=${SLURM_ARRAY_TASK_ID}

echo "Processing data for job index ${indx}."
echo "Loading configuration parameters ${cfgs[$indx]}:"

# extract the confiugration key name corresponding to the slurm index
cfg=${cfgs[$indx]}
job="${cfg}[@]"

cmd="cd ${USR_HME}/Grid-Stat"
echo ${cmd}; eval ${cmd}

log_dir=${OUT_ROOT}/batch_logs
cmd="mkdir -p ${log_dir}"
echo ${cmd}; eval ${cmd}

cmd="./run_gridstat.sh ${!job} > ${log_dir}/gridstat_${jbid}_${indx}.log 2>&1"
echo ${cmd}; eval ${cmd}

##################################################################################
# end

exit 0
