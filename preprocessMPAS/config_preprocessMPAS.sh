#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is for the WRF preprocessing related parameters.
# These will be passed to steps in the workflow for generating cf compliant and
# accumulation files from WRF outputs.
#
##################################################################################
# MPAS Preprocessing Settings
##################################################################################
# Source HPC parameters
source ../config_MET-tools.sh

# load MPAS modules used to build convert_mpas executable
# NOTE: this is temporary -- need to wrap convert_mpas into singularity
module load cpu/0.15.4
module load intel/19.1.1.217
module load intel-mpi/2019.8.254
module load netcdf-c/4.7.4
module load netcdf-fortran/4.5.3
module load netcdf-cxx/4.2
module load hdf5/1.10.6
module load parallel-netcdf/1.12.1
module load cmake/3.18.2

# Define the case-wise sub-directory for path names with case-study nesting,
# leave as empty string "" if not needed
export CSE=DeepDive/2022122800_valid_date

# Array of control flow names to be processed
export CTR_FLWS=( 
                 "MPAS"
                )

# Generate ensemble indices to process
ENS_PRFX="ens_"
MEM_IDS=()
for indx in {00..05..01}; do
    MEM_IDS+=( ${ENS_PRFX}${indx} )
done

# export MEM_IDS as an array containing an empty string if no indices or use array
# construction as above, this is passed to batch_wrf_preprocess
export MEM_IDS

# Define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2022122300
export STOP_DT=2022122700

# Define the increment between forecast initializations (HH)
export CYC_INC=24

# Define min / max forecast hours for cf outputs to be generated
export ANL_MIN=0
export ANL_MAX=120

# Define the increment at which to generate cf outputs (HH)
export ANL_INC=24

# Compute precipitation accumulations from cf files, TRUE or FALSE
export CMP_ACC=TRUE

# Defines the min / max accumulation interval for precip
export ACC_MIN=24
export ACC_MAX=72

# Defines the increment between min / max to compute accumulation intervals
export ACC_INC=24
