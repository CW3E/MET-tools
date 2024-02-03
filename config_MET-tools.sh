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
export USR_HME=/expanse/nfs/cw3e/cwp157/cgrudzien/JEDI-MPAS-Common-Case/MET-tools

# Root directory of simulation IO
export SIM_ROOT=/expanse/nfs/cw3e/cwp157/cgrudzien/JEDI-MPAS-Common-Case/SIMULATION_IO

# Root directory of simulation verification IO
export VRF_ROOT=/expanse/nfs/cw3e/cwp157/cgrudzien/JEDI-MPAS-Common-Case/VERIFICATION

# Root directory for verification static data
export STC_ROOT=/expanse/nfs/cw3e/cwp157/cgrudzien/JEDI-MPAS-Common-Case/DATA/DeepDive/Verification

# Root directory for software environment singularity images
export SOFT_ROOT=/expanse/nfs/cw3e/cwp157/cgrudzien/JEDI-MPAS-Common-Case/SOFT_ROOT

# MET-tools-py singularity image path
export MET_TOOLS_PY=${SOFT_ROOT}/MET-tools-py.sif

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
