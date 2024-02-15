#!/bin/bash
##################################################################################
# Description
##################################################################################
#
##################################################################################
# Parameters for plotting postprocessed DataFrames
##################################################################################
source ../config_MET-tools.sh

export SCRPT_DIR=${USR_HME}/plotDataFrames
export IF_SING=TRUE

# Define MET-tools-py Python execution with directory binds
MTPY="singularity exec -B "
MTPY+="${SCRPT_DIR}:/scrpt_dir:ro,${VRF_ROOT}:/in_root:ro,${VRF_ROOT}:/out_root:rw "
MTPY+="${MET_TOOLS_PY} python /scrpt_dir/"

# simple wrapper function for interactive shell python-like calls of scripts
mtpython() {
  cmd="${MTPY}$1 $2"
  echo "${cmd}"; eval ${cmd}
}

##################################################################################
