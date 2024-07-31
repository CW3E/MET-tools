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
module load singularitypro/3.11
module load cpu/0.17.3b
module load gcc/10.2.0/npcyll4
module load openmpi/4.1.1

##################################################################################
# HPC PARAMETERS
##################################################################################
# Root directory for MET-tools git clone
export USR_HME=/expanse/nfs/cw3e/cwp168/MET-tools

# Root directory of simulation IO
export SIM_ROOT=/expanse/nfs/cw3e/cwp168/SIMULATION_IO

# Root directory of simulation verification IO
export VRF_ROOT=/expanse/nfs/cw3e/cwp168/VERIFICATION_IO

# Root directory for verification static data
export STC_ROOT=/expanse/nfs/cw3e/cwp168/DATA/VERIFICATION_STATIC

# Root directory for landmasks, lat-lon files, and reference grids
export MSK_ROOT=${USR_HME}/vxmask

# Root directory for software environment singularity images
export SOFT_ROOT=/expanse/nfs/cw3e/cwp168/SOFT_ROOT

# MET version
export MET_VER="11.0.1"

# MET singularity image path 
export MET=${SOFT_ROOT}/met-${MET_VER}.sif

# MET-tools-py singularity image path
export MET_TOOLS_PY=${SOFT_ROOT}/MET-tools-py.sif

# convert_mpas singularity image path
export CONVERT_MPAS=${SOFT_ROOT}/convert_mpas.sif

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
