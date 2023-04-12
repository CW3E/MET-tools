#!/bin/bash
#SBATCH -p shared
#SBATCH --nodes=1
#SBATCH --mem=120G
#SBATCH -t 02:30:00
#SBATCH -J batch_wrfout_cf
#SBATCH --export=ALL
#SBATCH --array=0-5
##################################################################################
# Description
##################################################################################
# This script utilizes SLURM job arrays to batch process collections of WRF model
# outputs as a preprocessing step to ingestion into the MET Grid-Stat tool. This
# script is designed to set the parameters for the companion run_wrfout_cf.sh
# script as a job array map, allowing easy batch processing over multiple
# configurations simultaneously.
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

# initiate bash and source bashrc to initialize environement
conda init bash
source /home/USER/.bashrc

# set local environment for ncl and related dependencies
conda activate netcdf

# root directory for MET-tools git clone
export USR_HME=/cw3e/mead/projects/cwp106/scratch/MET-tools

# array of control flow names to be processed
CTR_FLWS=( 
          "NRT_gfs"
          "NRT_ecmwf"
         )

# model grid / domain to be processed
GRDS=( 
      "d01"
      "d02"
      "d03"
     )

# define the case-wise sub-directory for path names, leave as empty string if not needed
export CSE=DeepDive

# define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2022121400
export END_DT=2023011800

# define the interval between forecast initializations (HH)
export CYC_INT=24

# define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=240

# define the interval at which to process forecast outputs (HH)
export ANL_INT=24

# define the accumulation interval for verification valid times
export ACC_INT=24

# root directory for cycle time (YYYYMMDDHH) directories of WRF output files
export IN_ROOT=/cw3e/mead/datasets/cw3e/NRT/2022-2023

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant script outputs
export OUT_ROOT=/cw3e/mead/projects/cwp106/scratch/${CSE}

# set to regrid to lat / long for MET compatibility when handling grid errors
# must be equal to TRUE or FALSE
export RGRD=TRUE

##################################################################################
# Contruct job array and environment for submission
##################################################################################
# Create array of arrays to store the hyper-parameter grid settings, configs
# run based on SLURM job array index.  NOTE: directory paths dependent on control
# flow and grid settings are defined dynamically in the below and shold be set
# in the loops.
cfgs=()

num_grds=${#GRDS[@]}
num_flws=${#CTR_FLWS[@]}

# NOTE: SLURM JOB ARRAY SHOULD HAVE INDICES CORRESPONDING TO EACH OF THE
# CONFIGURATIONS DEFINED BELOW
for (( i = 0; i < ${num_grds}; i++ )); do
  for (( j = 0; j < ${num_flws}; j++ )); do
    CTR_FLW=${CTR_FLWS[$j]}
    GRD=${GRDS[$i]}

    cfg_indx="cfg_${i}${j}"
    cmd="${cfg_indx}=()"
    echo ${cmd}; eval ${cmd}

    cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
    echo ${cmd}; eval ${cmd}

    cmd="${cfg_indx}+=(\"GRD=${GRD}\")"
    echo ${cmd}; eval ${cmd}

    # This path defines the location of each cycle directory relative to IN_ROOT
    cmd="${cfg_indx}+=(\"IN_CYC_DIR=${IN_ROOT}/${CTR_FLW}\")"
    echo ${cmd}; eval ${cmd}

    # subdirectory of cycle-named directory containing data to be analyzed,
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=/wrfout\")"
    echo ${cmd}; eval ${cmd}
    
    # This path defines the location of each cycle directory relative to OUT_ROOT
    cmd="${cfg_indx}+=(\"OUT_CYC_DIR=${OUT_ROOT}/${CTR_FLW}/MET_analysis\")"
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

cmd="./run_wrfout_cf.sh ${!job} > wrfout_cf_${jbid}_${indx}.log 2>&1"
echo ${cmd}; eval ${cmd}

##################################################################################
# end

exit 0
