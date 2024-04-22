#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the GenEnsProd related verification parameters.
# These will be passed to steps in the workflow for generating statistics.
#
##################################################################################
# GenEnsProd PARAMETERS
##################################################################################
# Source HPC parameters
source ../config_MET-tools.sh

# Define the case-wise sub-directory for path names with case-study nesting,
# leave as empty string "" if not needed
export CSE=DeepDive/2022122800_valid_date

# Array of control flow names to be processed
export CTR_FLWS=( 
                 "nghido_letkf_OIE60km_WarmStart_aro_01.02"
		             "nghido_letkf_OIE60km_WarmStart_ctrl_01.01"
                )

# Prefix for ensemble members directory names
export ENS_PRFX="mem"

# Min and max ensemble index to process (includes control index)
export ENS_MIN=001
export ENS_MAX=001

# Number of digits to padd ensemble index to
export ENS_PDD=3

# Define control member index, not to be used in ensemble spread calculation,
# defined as empty string if not necessary
export CTR_MEM=""

# Neighborhood widths for neighborhood methods,
# references model grid with 1-1 correspondence
export NBRHD_WDTH=3

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=10.0, >=25.0, >=50.0, >=100.0 ]"

# Define the verification field
export VRF_FLD=QPF

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2023021818
export STOP_DT=2023022000

# Define the increment between forecast initializations (HH)
export CYC_INC=6

# Define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=0
export ANL_MAX=168

# Define the increment at which to process forecast outputs (HH)
export ANL_INC=6

# Compute precipitation accumulation, TRUE or FALSE
export CMP_ACC=TRUE

# Require all ensemble members, no missing files, TRUE or FALSE
export FULL_ENS=FALSE

# Defines the min / max accumulation interval for precip
export ACC_MIN=24
export ACC_MAX=24

# Defines the steps between min / max to compute accumulation intervals
export ACC_INC=24
