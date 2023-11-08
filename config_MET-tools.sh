#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the MET-tools workflow. These environmental 
# variables are defined for the use of bash scripts in the 
# workflow, defining HPC system settings
#
##################################################################################
# MODULE LOADS
##################################################################################
module load singularitypro/3.9
module load cpu/0.17.3b
module load gcc/10.2.0/npcyll4
module load openmpi/4.1.1

##################################################################################
# HPC PARAMETERS
##################################################################################
# Root directory for MET-tools git clone
export USR_HME=/expanse/lustre/projects/ddp181/cgrudzien/JEDI-MPAS-Common-Case/MET-tools

# Root directory of simulation IO
export SIM_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/SIMULATION_IO

# Root directory of simulation verification IO
export VRF_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/VERIFICATION

# Root directory for verification static data
export STC_ROOT=/expanse/lustre/scratch/cgrudzien/temp_project/JEDI-MPAS-Common-Case/DATA/DeepDive/Verification

# Root directory for software environment singularity images
export SOFT_ROOT=/expanse/lustre/projects/ddp181/cgrudzien/SOFT_ROOT

# NetCDF tools singularity image path
export NETCDF_TOOLS=${SOFT_ROOT}/MET_tools_conda_netcdf.sif

# Conda / Mamba installation path
export MAMBA_EXE=${SOFT_ROOT}/Micromamba/micromamba
export MAMBA_ROOT_PREFIX=${SOFT_ROOT}/Micromamba

# create aliases for Conda / Mamba environment calls
export DATAFRAMES="${MAMBA_EXE} run -n DataFrames python"

# MET version
export MET_VER="11.0.1"

# MET singularity image path 
export MET=${SOFT_ROOT}/met-${MET_VER}.sif

##################################################################################
# WORKFLOW UTILITY DEFINITIONS
##################################################################################
# Using GMT time zone for time computations
export TZ="GMT"

# Defines case-insensitive switch commands
export TRUE=[Tt][Rr][Uu][Ee]
export FALSE=[Ff][Aa][Ll][Ss][Ee]

# Defines numeric regular expression
export N_RE=^[0-9]+$

# Defines YYYYMMDDHH iso regular expression
export ISO_RE=^[0-9]{10}$

# Defines Pythonic string indentation
export INDT="    "
