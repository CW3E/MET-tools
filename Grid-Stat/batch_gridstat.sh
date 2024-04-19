#!/bin/bash
#SBATCH -p shared
#SBATCH --nodes=1
#SBATCH --mem=120G
#SBATCH -t 05:00:00
#SBATCH -J batch_gridstat
#SBATCH --export=ALL
#SBATCH --array=0-5
##################################################################################
# Description
##################################################################################
# This script utilizes SLURM job arrays to batch process collections of cf
# compliant, preprocessed WRF outputs and / or preprocessed global model data
# using the MET Grid-Stat tool. This script is designed to set the parameters for
# the companion run_gridstat.sh script as a job array map, allowing batch
# processing over multiple configurations and valid dates with a single call.
##################################################################################
# License Statement:
##################################################################################
# This software is Copyright © 2024 The Regents of the University of California.
# All Rights Reserved. Permission to copy, modify, and distribute this software
# and its documentation for educational, research and non-profit purposes,
# without fee, and without a written agreement is hereby granted, provided that
# the above copyright notice, this paragraph and the following three paragraphs
# appear in all copies. Permission to make commercial use of this software may
# be obtained by contacting:
#
#     Office of Innovation and Commercialization
#     9500 Gilman Drive, Mail Code 0910
#     University of California
#     La Jolla, CA 92093-0910
#     innovation@ucsd.edu
#
# This software program and documentation are copyrighted by The Regents of the
# University of California. The software program and documentation are supplied
# "as is", without any accompanying services from The Regents. The Regents does
# not warrant that the operation of the program will be uninterrupted or
# error-free. The end-user understands that the program was developed for
# research purposes and is advised not to rely exclusively on the program for
# any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED
# HEREUNDER IS ON AN “AS IS” BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO
# OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
# MODIFICATIONS.
# 
# 
##################################################################################
# SET GLOBAL PARAMETERS
##################################################################################
# uncoment to make verbose for debugging
#set -x

# Source the configuration file to define majority of required variables
source pre_processing_config.sh
           
# Root directory of regridded .nc landmasks on StageIV domain
export MSK_IN=${MSK_ROOT}/NRT_Masks

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
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"GRD=${GRD}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"INT_MTHD=${INT_MTHD}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"INT_WDTH=${INT_WDTH}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"IN_CYC_DIR=${IN_ROOT}/${CTR_FLW}\")"
    printf "${cmd}\n"; eval "${cmd}"

    cmd="${cfg_indx}+=(\"OUT_CYC_DIR=${OUT_ROOT}/${CTR_FLW}\")"
    printf "${cmd}\n"; eval "${cmd}"

    # subdirectory of cycle-named directory containing data to be analyzed,
    # includes leading '/', left as blank string if not needed
    cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=/${GRD}\")"
    printf "${cmd}\n"; eval "${cmd}"
    
    # subdirectory of cycle-named directory where output is to be saved
    cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=/${GRD}\")"
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

cmd="cd ${USR_HME}/Grid-Stat"
printf ${cmd}; eval "${cmd}"

log_dir=${OUT_ROOT}/batch_logs
cmd="mkdir -p ${log_dir}"
printf ${cmd}; eval "${cmd}"

cmd="./run_gridstat.sh ${!job} > ${log_dir}/gridstat_${jbid}_${indx}.log 2>&1"
printf ${cmd}; eval "${cmd}"

##################################################################################
# end

exit 0
