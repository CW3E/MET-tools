#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the WRF preprocessing related parameters.
# These will be passed to steps in the workflow for generating cf compliant and
# accumulation files from WRF outputs.
#
##################################################################################
# GRID-STAT PARAMETERS
##################################################################################
# Define the case-wise sub-directory for path names with case-study nesting,
# leave as empty string "" if not needed
export CSE=DeepDive

# Array of control flow names to be processed
export CTR_FLWS=( 
                 "2022122800_valid_date_wrf_ensemble"
                )

# Array of ensemble indices to process, include an empty string if no indices
export MEM_LIST=(
                 "00"
                 "01"
                 "02"
                 "03"
                 "04"
                 "05"
                )

# Model grid / domain to be processed
export GRDS=( 
             "d01"
             "d02"
            )

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2022122300
export STOP_DT=2022122300

# Define the interval between forecast initializations (HH)
export CYC_INT=24

# Define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=120

# Define the interval at which to process forecast outputs (HH)
export ANL_INT=24

# Defines the accumulation intervals for verification valid times
export ACC_INTS=(
                 "24"
                 "48"
                 "72"
                )

# Regrid to generic lat-lon for MET if native grid errors (TRUE or FALSE)
export RGRD=TRUE

# Compute precipitation accumulation from cf file, TRUE or FALSE
export CMP_ACC=TRUE
