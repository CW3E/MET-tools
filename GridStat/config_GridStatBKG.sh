#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the GridStat related verification parameters.
# These will be passed to steps in the workflow for generating statistics.
#
##################################################################################
# GridStat PARAMETERS
##################################################################################
# Source HPC parameters
source ../config_MET-tools.sh

# Define the case-wise sub-directory for path names with case-study nesting,
# leave as empty string "" if not needed
export CSE=""

# Array of control flow names to be processed
export CTR_FLWS=( 
                 "ECMWF"
                 "GFS"
                )

# Define interpolation neighborhood size in 1-1 correspondence with control flows
export INT_WDTHS=( 
                  "3"
                  "3"
                 )

# Define the verification field
export VRF_FLD=QPF

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=10.0, >=25.0, >=50.0, >=100.0 ]"

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2023021818
export STOP_DT=2023022200

# Define the increment between forecast initializations (HH)
export CYC_INC=6

# Define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=168

# Define the increment at which to process forecast outputs (HH)
export ANL_INC=24

# Compute precipitation accumulation, TRUE or FALSE
export CMP_ACC=TRUE

# Defines the min / max accumulation interval for precip
export ACC_MIN=24
export ACC_MAX=24

# Defines the increment between min / max to compute accumulation intervals
export ACC_INC=24

# Neighborhood width for neighborhood methods (references StageIV grid)
export NBRHD_WDTH=9

# Number of bootstrap resamplings, set 0 for off
export BTSTRP=0

# Rank correlation computation flag, TRUE or FALSE
export RNK_CRR=FALSE
