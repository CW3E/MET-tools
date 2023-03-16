#!/bin/bash
#SBATCH -p shared
#SBATCH --nodes=1
#SBATCH --mem=120G
#SBATCH -t 02:00:00
#SBATCH -J batch_gridstat
#SBATCH --export=ALL
#SBATCH --array=0
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

# root directory for MET-tools git clone
export USR_HME=/cw3e/mead/projects/cwp106/scratch/cgrudzien/MET-tools

# root directory for verification data
export DATA_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/DATA/StageIV
#DATA_ROOT=/cw3e/mead/projects/cnt102/METMODE_PreProcessing/data/StageIV

# root directory for MET software
export SOFT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/SOFT_ROOT/MET_CODE
export MET_SNG=${SOFT_ROOT}/met-10.0.1.simg

# Root directory for landmask
export MSK_ROOT=${SOFT_ROOT}/polygons/region

# specify thresholds levels for verification
export CAT_THR="[ >0.0, >=10.0, >=25.4, >=50.8, >=101.6 ]"

# array of control flow names to be processed
CTR_FLWS=( 
          "deterministic_forecast_lag00_b0.00"
         )

# NOTE: the grids in the GRDS array and the interpolation methods /
# neighborhbood widths in the below INT_MTHDS and INT_WDTHS must be
# in 1-1 correspondence
GRDS=(
      "d02"
     )

# define the interpolation method and related parameters
INT_MTHDS=(
           "DW_MEAN"
          )
INT_WDTHS=(
           "9"
          )

# define the case-wise sub-directory
export CSE=VD

# define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2019021100
export END_DT=2019021400

# define the interval between forecast initializations (HH)
export CYC_INT=24

# define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=96

# define the interval at which to process forecast outputs (HH)
export ANL_INT=24

# define the accumulation interval for verification valid times
export ACC_INT=24

# define the verification field
export VRF_FLD=QPF

# Landmask for verification region file name with extension
export MSK=CALatLonPoints.txt

# neighborhood width for neighborhood methods
export NBRHD_WDTH=9

# number of bootstrap resamplings, set 0 for off
export BTSTRP=1000

# rank correlation computation flag, TRUE or FALSE
export RNK_CRR=TRUE

# compute accumulation from cf file, TRUE or FALSE
export CMP_ACC=TRUE

# optionally define a gridstat output prefix, use a blank string for no prefix
export PRFX=""

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
export IN_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/cycling_sensitivity_testing

# subdirectory of cycle-named directory containing data to be analyzed,
# includes leading '/', left as blank string if not needed
export IN_DATE_SUBDIR=/${GRD}

# root directory for cycle time (YYYYMMDDHH) directories of gridstat outputs
export OUT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/cycling_sensitivity_testing

# subdirectory of cycle-named directory where output is to be saved
export OUT_DATE_SUBDIR=/${GRD}

##################################################################################
# Contruct job array and environment for submission
##################################################################################
# create array of arrays to store the hyper-parameter grid settings, configs
# run based on SLURM job array index
cnfgs=()

num_grds=${#GRDS[@]}
for (( i = 0; i < ${num_grds}; i++ )); do
  for CTR_FLW in ${CTR_FLWS}; do
    GRD=${GRDS[$i]}
    INT_MTHD=${INT_MTHDS[$i]}
    INT_WDTH=${INT_WDTHS[$i]}

    cnfg=()
    cnfg+=("export CTR_FLW=${CTR_FLW}")
    cnfg+=("export GRD=${GRD}")
    cnfg+=("export INT_MTHD=${INT_MTHD}")
    cnfg+=("export INT_WDTH=${INT_WDTH}")
    cnfg+=("export IN_CYC_DIR=${IN_ROOT}/${CSE}/${CTR_FLW}/MET_analysis")
    cnfg+=("export OUT_CYC_DIR=${OUT_ROOT}/${CSE}/${CTR_FLW}/MET_analysis")

    cnfgs+=${cnfg}
  done
done

##################################################################################
# run the processing script looping parameter arrays
indx=${SLURM_ARRAY_TASK_ID}

echo "Processing data for job index ${indx}."
echo "Loading configuration parameters:"

job_cnfg=${cnfgs[$indx]}
for cmd in ${job_cnfg[@]}; do
  echo ${cmd}; eval ${cmd}
done

cmd="cd ${USR_HME}"
echo ${cmd}; eval ${cmd}

cmd="./run_gridstat"
echo ${cmd}; eval ${cmd}

##################################################################################
# end

exit 0
