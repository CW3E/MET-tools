#!/bin/bash
##################################################################################
# Description
##################################################################################
#
##################################################################################
# License Statement:
##################################################################################
# This software is Copyright © 2024 The Regents of the University of California.
# All Rights Reserved. Permission to copy, modify, and distribute this software
# and its documentation for educational, research and non-profit purposes,
# without fee, and without a written agreement is hereby granted, provided that
# the above copyright notice, this paragraph and the following three paragraphs
# appear in all copies. Permission to make commercial use of this software may
# be obtained by contacting:
#
#     Office of Innovation and Commercialization
#     9500 Gilman Drive, Mail Code 0910
#     University of California
#     La Jolla, CA 92093-0910
#     innovation@ucsd.edu
#
# This software program and documentation are copyrighted by The Regents of the
# University of California. The software program and documentation are supplied
# "as is", without any accompanying services from The Regents. The Regents does
# not warrant that the operation of the program will be uninterrupted or
# error-free. The end-user understands that the program was developed for
# research purposes and is advised not to rely exclusively on the program for
# any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED
# HEREUNDER IS ON AN “AS IS” BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO
# OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
# MODIFICATIONS.
# 
##################################################################################
# MODULE LOADS
##################################################################################
module load singularitypro/3.11
module load cpu/0.17.3b
module load gcc/10.2.0/npcyll4
module load openmpi/4.1.1

##################################################################################
# HPC SYSTEM PATHS
##################################################################################
# Root directory for software environment singularity images
export SOFT_ROOT="/expanse/nfs/cw3e/cwp168/SOFT_ROOT"

# Root directory of simulation IO
export SIM_ROOT="/expanse/nfs/cw3e/cwp168/SIMULATION_IO"

# Root directory of simulation verification IO
export VRF_ROOT="/expanse/nfs/cw3e/cwp168/VERIFICATION_IO"

# Root directory for verification static data
export STC_ROOT="/expanse/nfs/cw3e/cwp168/DATA/VERIFICATION_STATIC"

# Root directory for MPAS static files for sourcing static IO streams
export MSH_ROOT="/expanse/nfs/cw3e/cwp168/Ensemble-DA-Cycling-Template/cylc-src"

##################################################################################
# MET EXECUTABLE AND DEPENDENCIES PATHS
##################################################################################
# MET version
export MET_VER="11.0.1"

# MET singularity image path 
export MET="${SOFT_ROOT}/met-${MET_VER}.sif"

# MET-tools-py singularity image path
export MET_TOOLS_PY="${SOFT_ROOT}/MET-tools-py.sif"

# convert_mpas singularity image path
export CONVERT_MPAS="${SOFT_ROOT}/convert_mpas.sif"

# Root directory for landmask gridded files outputs
export MSK_GRDS="${STC_ROOT}/vxmask"

##################################################################################
# HPC SYSTEM WORKLOAD MANAGER PARAMETERS
##################################################################################
# System scheduler
export SCHED="slurm"

# Define additional sub-cases for system platform, currently only includes penguin
# define as empty string if not needed
export SYS_TYPE=""

# Project billing account
export PROJECT="cwp168"

# Compute queue for standard mpi jobs
export PART_CMP="cw3e-compute"

# Debug queue for small / rapid parallel jobs
export PART_DBG="cw3e-compute"

# Serial queue for non-mpi jobs
export PART_SRL="cw3e-shared"

##################################################################################
