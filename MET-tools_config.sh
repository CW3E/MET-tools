#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the MET-tools workflow. These environmental 
# variables are defined for the use of bash scripts in the 
# workflow, defining HPC system settings
#
##################################################################################
# HPC PARAMETERS
##################################################################################
# Using GMT time zone for time computations
export TZ="GMT"

# Root directory for MET-tools git clone
export USR_HME=/expanse/lustre/projects/ddp181/cgrudzien/JEDI-MPAS-Common-Case/MET-tools

# Root directory of simulation IO
export SIM_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/SIMULATION_IO/WRF_Cycles

# Root directory of simulation verification IO
export VRF_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/VERIFICATION/WRF_Analysis

# Root directory for verification static data
export STC_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/DATA/DeepDive/Verification/StageIV

# Root directory for software environment singularity images
export SOFT_ROOT=/expanse/lustre/projects/ddp181/cgrudzien/SOFT_ROOT

# NetCDF tools singularity image path
export NETCDF_TOOLS=${SOFT_ROOT}/MET_tools_conda_netcdf.sif

# MET version
export MET_VER="11.0.1"

# MET singularity image path 
export MET=${SOFT_ROOT}/met-${MET_VER}.sif

# Module loads
module load singularitypro/3.9
