#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the NRT preprocessing related parameters.
# These will be passed to steps in the workflow for generating cf compliant and
# accumulation files from NRT outputs.
#
##################################################################################
# WRF preprocessing parameters
##################################################################################
# Source HPC parameters
source ../config_MET-tools.sh

# Define the case-wise sub-directory for path names with case-study nesting,
# leave as empty string "" if not needed
export CSE=2024010300_valid_date

# root directory for cycle time (YYYYMMDDHH) directories of NRT output files
export IN_ROOT=${SIM_ROOT}

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant outputs
export OUT_ROOT=${VRF_ROOT}/${CSE}

# Array of control flow names to be processed
export CTR_FLWS=( 
                 "NRT_ECMWF"
		 "NRT_GFS"
                )

# array for file handling
export NRT_NAMES=(
		  "ecmwf"
		  "gfs"
		 )

# Generate ensemble indices to process
ENS_PRFX="ens_"
MEM_IDS=()
for indx in {00..02..01}; do
    MEM_IDS+=( ${ENS_PRFX}${indx} )
done

# export MEM_IDS as an array containing an empty string if no indices or use array
# construction as above, this is passed to batch_nrt_preprocess
export MEM_IDS

# Model grid / domain to be processed
export GRDS=( 
             "d01"
             "d02"
	     "d03"
            )

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2024010300
export STOP_DT=2024012400

# Define the increment between forecast initializations (HH)
export CYC_INC=24

# Define min / max forecast hours for cf outputs to be generated
export ANL_MIN=0
export ANL_MAX=120

# Define the increment at which to generate cf outputs (HH)
export ANL_INC=24

# Regrid to generic lat-lon for MET if native grid errors (TRUE or FALSE)
export RGRD=TRUE

# Compute precipitation accumulations from cf files, TRUE or FALSE
export CMP_ACC=TRUE

# Defines the min / max accumulation interval for precip
export ACC_MIN=24
export ACC_MAX=72

# Defines the increment between min / max to compute accumulation intervals
export ACC_INC=24
