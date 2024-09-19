#!/bin/bash
##################################################################################
# Description
##################################################################################
# This configuration file is used to define the location of the git clone of the
# repository on the host system, the site configruation with HPC system specific
# parameters and the pre-configured workflow relative paths and Cylc parameters
# for the embedded installation.
#
##################################################################################
# SYSTEM-DEPENDENT WORKLFOW SETTINGS (EDIT TO LOCAL SETTINGS)
##################################################################################
# Full path of clone used as BASH HOME for embedded Cylc installation
export HOME="/expanse/nfs/cw3e/cwp168/MET-tools"

# Define the site-specific configuration to source for HPC globals
# New "sites" can be defined by copying the directory structure of the
# expanse-cwp168 template and edited to set local paths / computing environment
export SITE="expanse-cwp168"

##################################################################################
# WORKFLOW RELATIVE PATHS (DO NOT CHANGE)
##################################################################################
# Source the site-specific settings from the configuration file
source ${HOME}/settings/sites/${SITE}/config.sh

# Root directory of task driver scripts
export DRIVERS="${HOME}/src/drivers"

# Root directory of task driver scripts
export UTLTY="${HOME}/src/utilities"

# Root directory for landmasks
export MSK_ROOT="${HOME}/settings/mask-root"

##################################################################################
# EMBEDDED CYLC CONFIGURATION SETTINGS (DO NOT CHANGE)
##################################################################################
# Cylc environment name
export CYLC_ENV_NAME="cylc-8.3"

# Root directory of Cylc installation
export CYLC_ROOT="${HOME}/cylc"
export PATH="${CYLC_ROOT}:${PATH}"

# Location of Micromamba cylc environment
export CYLC_HOME_ROOT_ALT="${CYLC_ROOT}/Micromamba/envs"

# Set Cylc global.cylc configuration path to template
export CYLC_CONF_PATH="${CYLC_ROOT}"

# Cylc auto-completion prompts
if [[ $- =~ i && -f ${CYLC_ROOT}/cylc-completion.bash ]]; then
    . ${CYLC_ROOT}/cylc-completion.bash
fi

# Micromamba settings
export MAMBA_EXE="${CYLC_ROOT}/Micromamba/micromamba"
export MAMBA_ROOT_PREFIX="${CYLC_ROOT}/Micromamba"
__mamba_setup="$("$MAMBA_EXE" shell hook --shell bash --root-prefix \
  "$MAMBA_ROOT_PREFIX" 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__mamba_setup"
else
    alias micromamba="$MAMBA_EXE"  # Fallback on help from mamba activate
fi
unset __mamba_setup

##################################################################################
