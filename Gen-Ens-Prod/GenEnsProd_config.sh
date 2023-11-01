#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the Gen-Ens-Prod related verification parameters.
# These will be passed to steps in the workflow for generating statistics.
#
##################################################################################
# GRID-STAT PARAMETERS
##################################################################################
# Define the case-wise sub-directory for path names with case-study nesting,
# leave as empty string "" if not needed
export CSE=DeepDive/2022122800_valid_date

# Array of control flow names to be processed
export CTR_FLWS=( 
                 "WRF"
                )

# Prefix for ensemble members directory names
export ENS_PRFX="ens_"

# Min and max ensemble index to process (includes control index)
export ENS_MIN=00
export ENS_MAX=05

# Define control member index, not to be used in ensemble spread calculation,
# defined as empty string if not necessary
export CTR_MEM=00

# Model grid / domain to be processed
export GRDS=( 
             "d01"
             "d02"
            )

# Neighborhood widths for neighborhood methods,
# references model grid with 1-1 correspondence
export NBRHD_WDTHS=(
                    "3"
                    "9"
                   )

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=10.0, >=25.0, >=50.0, >=100.0 ]"

# Define the interpolation method and related parameters
export INT_MTHDS=( 
                  "DW_MEAN"
                  "DW_MEAN"
                 )

# Define the verification field
export VRF_FLD=QPF

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

# Compute precipitation accumulation from cf file, TRUE or FALSE
export CMP_ACC=TRUE

# Defines the min / max accumulation interval for precip
export ACC_MIN=24
export ACC_MAX=72

# Defines the steps between min / max to compute accumulation intervals
export ACC_INT=24

