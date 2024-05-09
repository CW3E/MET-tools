#!/bin/bash
#SBATCH --account=cwp168
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=150G
#SBATCH -p cw3e-shared
#SBATCH -t 01:00:00
#SBATCH -J preprocessWRF
#SBATCH -o ./logs/preprocessWRF-%A_%a.out
#SBATCH --export=ALL
#SBATCH --array=0-11
##################################################################################
# Description
##################################################################################
# This script batch preprocesses collections of WRF model outputs in parallel with
# the HPC system scheduler. This script constructs a parameter map for
# run_wrf_preprocess.sh script as a job array, allowing batch processing over
# multiple configurations simultaneously.
#
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

# Source tool configuration
source ./config_preprocessWRF.sh

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
num_grds=${#GRDS[@]}

# NOTE: SLURM JOB ARRAY SHOULD HAVE INDICES CORRESPONDING TO EACH OF THE
# CONFIGURATIONS DEFINED BELOW
for (( i_f = 0; i_f < ${num_flws}; i_f++ )); do
  for (( i_m = 0; i_m < ${num_mems}; i_m++ )); do
    for (( i_g = 0; i_g < ${num_grds}; i_g++ )); do
      CTR_FLW=${CTR_FLWS[$i_f]}
      GRD=${GRDS[$i_g]}
      MEM=${MEM_IDS[$i_m]}

      cfg_indx="cfg_${i_f}${i_m}${i_g}"
      cmd="${cfg_indx}=()"
      printf "${cmd}\n"; eval "${cmd}"

      cmd="${cfg_indx}+=(\"CTR_FLW=${CTR_FLW}\")"
      printf "${cmd}\n"; eval "${cmd}"

      cmd="${cfg_indx}+=(\"GRD=${GRD}\")"
      printf "${cmd}\n"; eval "${cmd}"

      # This path defines the location of each cycle directory relative to IN_ROOT
      cmd="${cfg_indx}+=(\"IN_DT_ROOT=${IN_ROOT}/${CTR_FLW}\")"
      printf "${cmd}\n"; eval "${cmd}"

      # subdirectory of cycle-named directory containing data to be analyzed,
      # left as blank string if not needed
      cmd="${cfg_indx}+=(\"IN_DT_SUBDIR=/wrf/${MEM}\")"
      printf "${cmd}\n"; eval "${cmd}"
      
      # This path defines the location of each cycle directory relative to OUT_ROOT
      cmd="${cfg_indx}+=(\"OUT_DT_ROOT=${OUT_ROOT}/${CTR_FLW}/Preprocess\")"
      printf "${cmd}\n"; eval "${cmd}"

      # subdirectory of cycle-named directory where output is to be saved
      # left as blank string if not needed
      cmd="${cfg_indx}+=(\"OUT_DT_SUBDIR=/${MEM}/${GRD}\")"
      printf "${cmd}\n"; eval "${cmd}"

      cmd="cfgs+=( \"${cfg_indx}\" )"
      printf "${cmd}\n"; eval "${cmd}"
    done
  done
done

##################################################################################
# run the processing script looping parameter arrays
jbid=${SLURM_ARRAY_JOB_ID}
indx=${SLURM_ARRAY_TASK_ID}

printf "Processing data for job index ${indx}.\n"
printf "Loading configuration parameters ${cfgs[$indx]}:\n"

# extract the configuration key name corresponding to the slurm index
cfg=${cfgs[$indx]}
job="${cfg}[@]"

cmd="cd ${USR_HME}/preprocessWRF"
printf "${cmd}\n"; eval "${cmd}"

log_dir=${OUT_ROOT}/batch_logs
cmd="mkdir -p ${log_dir}"
printf "${cmd}\n"; eval "${cmd}"

cmd="./run_preprocessWRF.sh ${!job} \
  > ${log_dir}/preprocessWRF_${jbid}_${indx}.log 2>&1"
printf "${cmd}\n"; eval "${cmd}"

##################################################################################
# end

exit 0
