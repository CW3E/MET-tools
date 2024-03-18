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
module load gcc/13.2.0
module load ncarenv/23.06
module load apptainer/1.1.7
module load intel/2023.0.0
module load openmpi/main

##################################################################################
# HPC PARAMETERS
##################################################################################
export MPAS_MESH=/glade/derecho/scratch/nghido/sio-cw3e/GenerateGFSAnalyses/ExternalAnalyses/60km/2023021900/x1.163842.init.2023-02-19_00.00.00.nc

# Root directory for MET-tools git clone
export USR_HME=/glade/work/ersawyer/derecho/MET-tools

# Root directory of simulation IO
export SIM_ROOT=/glade/derecho/scratch/ersawyer/sio-cw3e/JEDI-MPAS-Common-Case/SIMULATION_IO

# Root directory of simulation verification IO
export VRF_ROOT=/glade/derecho/scratch/ersawyer/sio-cw3e/JEDI-MPAS-Common-Case/VERIFICATION

# Root directory for verification static data
export STC_ROOT=/glade/derecho/scratch/ersawyer/sio-cw3e/JEDI-MPAS-Common-Case/Verification

# Root directory for software environment singularity images
export SOFT_ROOT=/glade/work/ersawyer/derecho/SOFT_ROOT

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
