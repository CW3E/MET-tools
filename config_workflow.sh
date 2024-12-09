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
# PREAMBLE (DO NOT CHANGE)
##################################################################################
# Sets Xauthority for x11 forwarding before changing HOME variable
export XAUTHORITY="$HOME/.Xauthority"

##################################################################################
# SYSTEM-DEPENDENT WORKLFOW SETTINGS (EDIT TO LOCAL SETTINGS)
##################################################################################
# Full path of clone used as BASH HOME for embedded Cylc installation
export HOME="/expanse/nfs/cw3e/cwp168/MET-tools"

# Define the site-specific configuration to source for HPC globals
# New "sites" can be defined by copying the directory structure of the
# expanse-cwp168 template and edited to set local paths / computing environment
export SITE="expanse-cwp168"

# If plotting will be called from containerized envrionment (sets path binds)
export IF_CNTR_PLT="TRUE"

##################################################################################
# WORKFLOW RELATIVE PATHS (DO NOT CHANGE)
##################################################################################
# Source the site-specific settings from the configuration file
source ${HOME}/settings/sites/${SITE}/config.sh

# Root directory of source codes
export SRC="${HOME}/src"

# Root directory of task driver scripts
export DRIVERS="${SRC}/drivers"

# Defines constants / patterns used for driver scripts
export CNST="${DRIVERS}/CONSTANTS.sh"

# Root directory of task supporting scripts
export UTLTY="${SRC}/utilities"

# Directory for plotting routines
export PLT="${SRC}/plotting"

# Root directory of shared task settings
export SHARED="${HOME}/settings/shared"

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
# PLOTTING UTILITIES AND DEFS (DO NOT CHANGE)
##################################################################################
# Add the plotting directory to Python path in raw and containerized paths
export PYTHONPATH="${SRC}:/src_dir"

# Define MET-tools-py Python execution with directory binds
MTPY="singularity exec -B "
MTPY+="${SRC}:/src_dir:ro,${VRF_ROOT}:/in_root:ro,${VRF_ROOT}:/out_root:rw "
MTPY+="${MET_TOOLS_PY} python /src_dir/"

# simple wrapper function for interactive shell calls of plotting scripts
mtplot() {
  cmd="${MTPY}plotting/$1"
  echo "${cmd}"; eval ${cmd}
}

##################################################################################
