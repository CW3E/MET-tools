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
export CSE=2024010300_valid_date

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
export IN_ROOT=${VRF_ROOT}/${CSE}

# root directory for cycle time (YYYYMMDDHH) directories of gridstat outputs
export OUT_ROOT=${VRF_ROOT}/${CSE}

# Array of control flow names to be processed
export CTR_FLWS=( 
                 "NRT_ECMWF"
		 "NRT_GFS"
                )

# Prefix for ensemble members directory names
export ENS_PRFX="ens_"

# Min and max ensemble index to process (includes control index)
export ENS_MIN=00
export ENS_MAX=02

# Number of digits to padd ensemble index to
export ENS_PDD=2

# Define control member index, not to be used in ensemble spread calculation,
# defined as empty string if not necessary
export CTR_MEM=00

# Model grid / domain to be processed
export GRDS=( 
             "d01"
             "d02"
	     "d03"
            )

# Neighborhood widths for neighborhood methods,
# references model grid with 1-1 correspondence
export NBRHD_WDTHS=(
                    "3"
                    "3"
		    "3"
                   )

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=10.0, >=25.0, >=50.0, >=100.0 ]"

# Define the verification field
export VRF_FLD=QPF

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2024010300
export STOP_DT=2024012400

# Define the increment between forecast initializations (HH)
export CYC_INC=24

# Define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=120

# Define the increment at which to process forecast outputs (HH)
export ANL_INC=24

# Compute precipitation accumulation, TRUE or FALSE
export CMP_ACC=TRUE

# Require all ensemble members, no missing files, TRUE or FALSE
export FULL_ENS=TRUE

# Defines the min / max accumulation interval for precip
export ACC_MIN=24
export ACC_MAX=72

# Defines the steps between min / max to compute accumulation intervals
export ACC_INC=24
