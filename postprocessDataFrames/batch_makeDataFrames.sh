#!/bin/bash
#PBS -q main
#PBS -A UCSD0047 
#PBS -l select=1:ncpus=128:mpiprocs=32
#PBS -l walltime=00:30:00
#PBS -N makeDataFrames 
#PBS -o ./logs/makeDataFrames
#PBS -j oe 
##################################################################################
# RENAME LOG FILE
##################################################################################
mv ./logs/vxmask.out ./logs/makeDataFrames_${PBS_JOBID}.out
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
source ./config_DataFrames.sh

##################################################################################
cmd="${MTPY}run_makeDataFrames.py"
printf "${cmd}\n"; eval ${cmd}

##################################################################################
# end

exit 0
