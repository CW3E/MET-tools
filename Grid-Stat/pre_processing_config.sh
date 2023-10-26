#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the MET-tools workflow. These environmental 
# variables are defined for the use of the pre-processing bash scripts in the 
# workflow. Furthermore, in this file are Singularity container-dependent 
# variables designed for the conda environents implimented in the MET-tools 
# scripts.
#
##################################################################################
# HPC PARAMETERS
##################################################################################
# Root directory for MET-tools git clone
export USR_HME=/expanse/lustre/projects/ddp181/cgrudzien/JEDI-MPAS-Common-Case/MET-tools

# Root directory of simulation IO
export SIM_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/SIMULATION_IO/WRF_Cycles

# Root directory of simulation verification IO
export VRF_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/VERIFICATION/WRF_Analysis

# Root directory for verification static data
export STC_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/DATA/DeepDive/Verification

# Root directory for software environment singularity images
export SOFT_ROOT=/expanse/lustre/projects/ddp181/cgrudzien/SOFT_ROOT

# NetCDF tools singularity image path
export NETCDF_TOOLS=${SOFT_ROOT}/MET_tools_conda_netcdf.sif

# MET singularity image path / MET version
export MET=${SOFT_ROOT}/met-10.0.1.sif

# Module loads
module load singularitypro/3.9

##################################################################################
# VERIFICATION PARAMETERS
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

##################################################################################
# MET-Tools Parameters
##################################################################################
# Using GMT time zone for time computations
export TZ="GMT"

# Root directory for landmasks, lat-lon files, and reference StageIV grid
export MSK_ROOT=${USR_HME}/polygons

# Path to file with list of landmasks for verification regions
export MSKS=${MSK_ROOT}/mask-lists/NRT_MaskList.txt

# Output directory for landmasks generated for verification steps
export MSK_OUT=${MSK_ROOT}/NRT_Masks

# Root directory of regridded .nc landmasks on StageIV domain for verification
export MSK_IN=${MSK_ROOT}/NRT_Masks

# Path to a generic StageIV data product for reference verfication grid
# an arbitrary file with the correct grid is sufficient
export OBS_F_IN=StageIV_QPE_2019021500.nc
