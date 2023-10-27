#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the Grid-Stat related verification parameters.
# These will be passed to steps in the workflow for generating statistics.
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

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=10.0, >=25.0, >=50.0, >=100.0 ]"

# Define the interpolation method and related parameters
export INT_MTHDS=( 
                  "DW_MEAN"
                  "DW_MEAN"
                 )

export INT_WDTHS=( 
                  "3"
                  "9"
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

# Define the accumulation interval for verification valid times
export ACC_INT=24

# Regrid to generic lat-lon for MET if native grid errors (TRUE or FALSE)
export RGRD=TRUE

# Neighborhood width for neighborhood methods (references StageIV grid)
export NBRHD_WDTH=9

# Number of bootstrap resamplings, set 0 for off
export BTSTRP=0

# Rank correlation computation flag, TRUE or FALSE
export RNK_CRR=FALSE

# Optionally define a MET output prefix, use a blank string for no prefix
export PRFX=""
