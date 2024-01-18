#!/bin/bash
#SBATCH --account=cwp157
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=64
#SBATCH --mem=20G
#SBATCH -p cw3e-shared
#SBATCH -t 00:30:00
#SBATCH -J makeDataFrames
#SBATCH -o ./logs/makeDataFrames-%A_%a.out
#SBATCH --export=ALL
##################################################################################
# Description
##################################################################################
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
source ../config_MET-tools.sh
export SCRPT_ROOT=${USR_HME}/postprocessDataFrames

##################################################################################
# run the batch processing with native Python multiprocessing
cmd="cd ${SCRPT_ROOT}"
printf "${cmd}\n"; eval ${cmd}

cmd="${DATAFRAMES} -u run_makeDataFrames.py"
printf "${cmd}\n"; eval ${cmd}

##################################################################################
# end

exit 0
