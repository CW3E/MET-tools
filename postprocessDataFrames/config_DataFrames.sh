#!/bin/bash
##################################################################################
# Description
##################################################################################
# Simple wrappers to create singularity binds and calls for conda singularity
# environment. All workflow parameters are included in config_DataFrames.py
#
##################################################################################
# Parameters for ASCII DataFrame conversions
##################################################################################
source ../config_MET-tools.sh

export SCRPT_DIR=${USR_HME}/postprocessDataFrames

# Define MET-tools-py Python execution with directory binds
MTPY="singularity exec -B "
MTPY+="${SCRPT_DIR}:/scrpt_dir:ro,${VRF_ROOT}:/in_root:ro,${VRF_ROOT}:/out_root:rw "
MTPY+="${MET_TOOLS_PY} python /scrpt_dir/"
export MTPY

##################################################################################
