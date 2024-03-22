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
export CSE=2023021818_cycle_start

# Array of control flow names to be processed
export CTR_FLWS=( 
                 "nghido_letkf_OIE60km_WarmStart_aro_01.02"
		             "nghido_letkf_OIE60km_WarmStart_ctrl_01.01"
                )

# If computing ensemble mean verification
export IF_ENS_MEAN=FALSE

# min / max ensemble indices used to compute ensemble product
# used in ensemble product naming conventions
export ENS_MIN=00
export ENS_MAX=05

# If computing individual ensemble member verification
export IF_ENS_MEMS=TRUE

# Generate ensemble indices to process, used for individual member verification
ENS_PRFX="ens_"
MEM_IDS=( "mean" )

# export MEM_IDS as an array containing an empty string if no indices or use array
# construction as above, this is passed to batch_gridstat
export MEM_IDS

# Define interpolation neighborhood size in 1-1 correspondence with model grids
export INT_WDTH=3

# Define the verification field
export VRF_FLD=QPF

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=10.0, >=25.0, >=50.0, >=100.0 ]"

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2023021818
export STOP_DT=2023022000

# Define the increment between forecast initializations (HH)
export CYC_INC=6

# Define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=0
export ANL_MAX=168

# Define the increment at which to process forecast outputs (HH)
export ANL_INC=12

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
export RNK_CRR=TRUE
