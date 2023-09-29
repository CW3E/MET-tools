#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the MET-tools workflow. These environmental 
# variables are defined for the use of the pre-processing bash scripts in the 
# workflow. Furthermore, in this file are a few Singularity container-dependent 
# variables designed for the conda environents implimented in the MET-tools 
# scripts.
#
##################################################################################
# GLOBAL PARAMETERS TO BE SET BY USER
##################################################################################

# Root directory for MET-tools git clone
export USR_HME=/home/jlconti/MET-tools

# Refine the case-wise sub-directory for path names, leave as empty string if not needed
export CSE=jlconti

# Root directory for MET singularity image
export SOFT_ROOT=/home/jlconti

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2022123100
export END_DT=2023011800

# Array of control flow names to be processed
CTR_FLWS=( 
          "NRT_gfs"
          "NRT_ecmwf"
         )

# Model grid / domain to be processed
GRDS=( 
      "d01"
      "d02"
      "d03"
     )

# Specify thresholds levels for verification
export CAT_THR="[ >0.0, >=1.0, >=10.0, >=25.0, >=50.0 ]"

# Define the interpolation method and related parameters
INT_MTHDS=( 
           "DW_MEAN"
           "DW_MEAN"
           "DW_MEAN"
          )

INT_WDTHS=( 
           "3"
           "9"
           "27"
          )

# Singularity Container Variables for NetCDF Environment
export NCKS_CMD="singularity exec --bind /cw3e:/cw3e,/scratch:/scratch /cw3e/mead/projects/cwp106/scratch/MET_tools_conda_netcdf.sif ncks"
export NCL_CMD="singularity exec --bind /cw3e:/cw3e,/scratch:/scratch /cw3e/mead/projects/cwp106/scratch/MET_tools_conda_netcdf.sif ncl"
export CDO_CMD="singularity exec --bind /cw3e:/cw3e,/scratch:/scratch /cw3e/mead/projects/cwp106/scratch/MET_tools_conda_netcdf.sif cdo"

##################################################################################
# GLOBAL PARAMETERS THAT MAY NEED TO CHANGE
##################################################################################

# Root directory for verification data
export DATA_ROOT=/cw3e/mead/projects/cnt102/METMODE_PreProcessing/data/StageIV

# Define the interval between forecast initializations (HH)
export CYC_INT=24

# Define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=240

# Define the interval at which to process forecast outputs (HH)
export ANL_INT=24

# Define the accumulation interval for verification valid times
export ACC_INT=24

# Set to regrid to lat-lon for MET compatibility when handling grid errors (TRUE or FALSE)
export RGRD=TRUE

# Neighborhood width for neighborhood methods
export NBRHD_WDTH=9

# Number of bootstrap resamplings, set 0 for off
export BTSTRP=0

# Rank correlation computation flag, TRUE or FALSE
export RNK_CRR=FALSE

# Compute accumulation from cf file, TRUE or FALSE
export CMP_ACC=FALSE

# Optionally define a gridstat output prefix, use a blank string for no prefix
export PRFX=""

##################################################################################
# GLOBAL PARAMETERS THAT PROBABLY WON'T NEED TO CHANGE
##################################################################################

# Using GMT time zone for time computations
export TZ="GMT"

# MET singularity image path
export MET_SNG=${SOFT_ROOT}/met-10.0.1.simg

# Root directory for landmasks, lat-lon files, and reference StageIV grid
export MSK_ROOT=${USR_HME}/polygons

# Path to file with list of landmasks for verification regions
export MSKS=${MSK_ROOT}/mask-lists/NRT_MaskList.txt

# Output directory for landmasks
export MSK_OUT=${MSK_ROOT}/NRT_Masks

# Define path to StageIV data product for reference verfication grid
# an arbitrary file with the correct grid is sufficient
export OBS_F_IN=StageIV_QPE_2019021500.nc

# Define the verification field
export VRF_FLD=QPF

