#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the WRF preprocessing related parameters.
# These will be passed to steps in the workflow for generating cf compliant and
# accumulation files from WRF outputs.
#
##################################################################################
# MPAS Preprocessing Settings
##################################################################################
# Source HPC parameters
source ../config_MET-tools.sh

# MSH_ROOT  = "/glade/derecho/scratch/nghido/sio-cw3e/GenerateGFSAnalyses/ExternalAnalyses/60km/2023021900/"
export MSH_ROOT="/glade/derecho/scratch/nghido/sio-cw3e/GenerateGFSAnalyses/ExternalAnalyses/60km/2023021900/"

# Define the case-wise sub-directory for path names with case-study nesting,
# leave as empty string "" if not needed
export CSE=2023021818_cycle_start

# Array of control flow names to be processed
#need to delete CTRL_FLWS or make it empty
export CTR_FLWS=( 
                 "nghido_letkf_OIE60km_WarmStart_aro_01.02"
		 "nghido_letkf_OIE60km_WarmStart_ctrl_01.01"
                )
# Generate ensemble indices to process
ENS_PRFX="mem"
MEM_IDS=()
for indx in {001..001..001}; do
    MEM_IDS+=( ${ENS_PRFX}${indx} )
done
# export MEM_IDS as an array containing an empty string if no indices or use array
# construction as above, this is passed to batch_wrf_preprocess
export MEM_IDS

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2023021818
export STOP_DT=2023022000

# Define the increment between forecast initializations (HH)
export CYC_INC=6

# Define min / max forecast hours for cf outputs to be generated
export ANL_MIN=0
export ANL_MAX=168

# Define the increment at which to generate cf outputs (HH)
export ANL_INC=6

# Compute precipitation accumulations from cf files, TRUE or FALSE
export CMP_ACC=TRUE

# Defines the min / max accumulation interval for precip
export ACC_MIN=24
export ACC_MAX=24

# Defines the increment between min / max to compute accumulation intervals
export ACC_INC=24
