#!/bin/bash
#################################################################################
# Description
#################################################################################
# This script runs a batch processing routine for a given control flow /
# grid configuration and date range as defined in the companion batch and config
# scripts. This driver script loops the calls to the MPAS preprocessing scripts
# mpas_to_latlon.sh / mpas_to_cf.py to ready MPAS outputs for MET, and will
# optionally compute  accumulated precip in addition. This script is based on
# original source code provided by Rachel Weihs, Caroline Papadopoulos and
# Daniel Steinhoff.  This is re-written to homogenize project structure and to
# include error handling, process logs and additional flexibility with batch
# processing ranges of data from multiple models and / or workflows.
#
#################################################################################
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
#
#################################################################################
# CHECK WORKFLOW PARAMETERS
#################################################################################

if [ ! -x ${CNST} ]; then
  printf "ERROR: constants file\n ${CNST}\n does not exist or is not executable.\n"
  exit 1
else
  # Read constants into the current shell
  cmd=". ${CNST}"
  printf "${cmd}\n"; eval "${cmd}"
fi

# control flow to be processed
if [ ! ${CTR_FLW} ]; then
  printf "ERROR: control flow name \${CTR_FLW} is not defined.\n"
  exit 1
fi

# flag is set to source mesh information from the same stream as the MPAS outputs
# unless a mesh root directory and file name is supplied
in_msh_strm=FALSE
if [ -z ${IN_MSH_DIR+x} ]; then
  printf "ERROR: Static information directory \${IN_MSH_DIR} is not declared.\n"
  msg="Supply a blank string for this variable if static information is derived"
  msg+=" from the same data stream as MPAS output files.\n"
  printf "${msg}"
  exit 1
elif [ -n ${IN_MSH_DIR} ]; then
  if [[ ! -d  ${IN_MSH_DIR} || ! -x ${IN_MSH_DIR} ]]; then
    msg="ERROR: static information directory IN_MSH_DIR\n ${IN_MSH_DIR}\n"
    msg+=" is not a directory or is not executable.\n"
    printf "${msg}"
    exit 1
  elif [[ ! -r ${IN_MSH_DIR}/${IN_MSH_F} ]]; then
    msg="ERROR: static information file\n ${IN_MSH_DIR}/${IN_MSH_F}\n"
    msg+=" is not readable or does not exist.\n"
    printf "${msg}"
    exit 1
  else
    in_msh_strm=TRUE
    in_msh_dir="${IN_MSH_DIR}"
    in_msh_f="${IN_MSH_F}"
    printf "MPAS static fields are sourced from\n ${IN_MSH_DIR}/${IN_MSH_F}\n"
  fi
else
   # When MSH_ROOT is defined as an empty sting, static info sourced from input
    msg="\${IN_MSH_DIR} is an empty string, static information is derived"
    msg+=" from the same data stream as MPAS outputs.\n"
    printf "${msg}"
fi

if [ -z ${MPAS_PRFX} ]; then
  msg="ERROR: MPAS file prefix \${MPAS_PRFX} is not defined. Supply a file"
  msg+=" prefix value, e.g., hist / diag, for the source of model outputs.\n"
  printf "${msg}"
  exit 1
else
  printf "MPAS model outputs are sourced from file prefix\n ${MPAS_PRFX}\n"
fi

# Convert CYC_DT from 'YYYYMMDDHH' format to cyc_dt Unix date format
if [[ ! ${CYC_DT} =~ ${ISO_RE} ]]; then
  msg="ERROR: cycle date \${CYC_DT}\n ${CYC_DT}\n"
  msg+=" is not in YYYYMMDDHH format.\n"
  printf "${msg}"
  exit 1
else
  cyc_dt="${CYC_DT:0:8} ${CYC_DT:8:2}"
  cyc_dt=`date -d "${cyc_dt}"`
fi

# define min / max forecast hours for forecast outputs to be processed
if [[ ! ${ANL_MIN} =~ ${N_RE} ]]; then
  printf "ERROR: min forecast hour \${ANL_MIN} is not numeric.\n"
  exit 1
elif [ ${ANL_MIN} -lt 0 ]; then
  printf "ERROR: min forecast hour ${ANL_MIN} must be non-negative.\n"
  exit 1
elif [[ ! ${ANL_MAX} =~ ${N_RE} ]]; then
  printf "ERROR: max forecast hour \${ANL_MAX} is not numeric.\n"
  exit 1
elif [ ${ANL_MAX} -lt ${ANL_MIN} ]; then
  msg="ERROR: max forecast hour ${ANL_MAX} must be greater than or equal to"
  msg+="min forecast hour ${ANL_MIN}.\n"
  printf "${msg}"
fi

# define the increment at which to process forecast outputs (HH)
if [[ ! ${ANL_INC} =~ ${N_RE} ]]; then
  printf "ERROR: hours increment between analyses \${ANL_INC} is not numeric.\n"
  exit 1
elif [ ! $(( (${ANL_MAX} - ${ANL_MIN}) % ${ANL_INC} )) = 0 ]; then
  msg="ERROR: the interval [\${ANL_MIN}, \${ANL_MAX}]\n [${ANL_MIN}, ${ANL_MAX}]\n" 
  msg+=" must be evenly divisible into increments of \${ANL_INC}, ${ANL_INC}.\n"
  printf "${msg}"
  exit 1
fi

if [ -z ${EXP_VRF} ]; then
  msg="No stop date is set - preprocessMPAS runs until max forecast"
  msg+=" hour ${ANL_MAX}.\n"
  anl_max="${ANL_MAX}"
  printf "${msg}"
elif [[ ! ${EXP_VRF} =~ ${ISO_RE} ]]; then
  msg="ERROR: stop date \${EXP_VRF}\n ${EXP_VRF}\n"
  msg+=" is not in YYYYMMDDHH format.\n"
  printf "${msg}"
  exit 1
else
  # Convert EXP_VRF from 'YYYYMMDDHH' format to exp_vrf Unix date format
  exp_vrf="${EXP_VRF:0:8} ${EXP_VRF:8:2}"
  printf "Stop date is set at `date +%Y-%m-%d_%H_%M_%S -d "${exp_vrf}"`.\n"
  printf "Preprocessing stops automatically for forecasts at this time.\n"
  # Recompute the max forecast hour with respect to exp_vrf
  exp_vrf=`date +%s -d "${exp_vrf}"`
  anl_max=$(( ${exp_vrf} - `date +%s -d "${cyc_dt}"` ))
  anl_max=$(( ${anl_max} / 3600 ))
fi

# compute accumulation from cf file, TRUE or FALSE
if [[ ${CMP_ACC} =~ ${TRUE} ]]; then
  # define the accumulation intervals for precip
  if [[ ! ${ACC_MIN} =~ ${INT_RE} ]]; then
    msg="ERROR: min accumulation interval \${ACC_MIN},\n ${ACC_MIN}\n"
    msg+=" is not an integer.\n"
    printf "${msg}"
    exit 1
  elif [ ${ACC_MIN} -le 0 ]; then
    msg="ERROR: min accumulation interval ${ACC_MIN} must be greater than"
    msg+=" zero.\n"
    printf "${msg}"
    exit 1
  elif [[ ! ${ACC_MAX} =~ ${INT_RE} ]]; then
    msg="ERROR: max accumulation interval \${ACC_MAX},\n ${ACC_MAX}\n"
    msg+=" is not integer.\n"
    printf "${msg}"
    exit 1
  elif [ ${ACC_MAX} -lt ${ACC_MIN} ]; then
    msg="ERROR: max precip accumulation interval ${ACC_MAX} must be greater than"
    msg+=" min accumulation interval ${ACC_MIN}.\n"
    printf "${msg}"
    exit 1
  elif [[ ! ${ACC_INC} =~ ${INT_RE} ]]; then
    msg="ERROR: increment between precip accumulation intervals \${ACC_INC}"
    msg+=" is not integer.\n"
    printf "${msg}"
    exit 1
  elif [ ! $(( (${ACC_MAX} - ${ACC_MIN}) % ${ACC_INC} )) = 0 ]; then
    msg="ERROR: the interval [\${ACC_MIN}, \${ACC_MAX}]\n"
    msg+=" [${ACC_MIN}, ${ACC_MAX}] must be evenly divisible into\n"
    msg+=" increments of \${ACC_INC}, ${ACC_INC}.\n"
    printf "${msg}"
    exit 1
  else
    # define array of accumulation interval computation hours
    acc_hrs=()
    for (( acc_hr=${ACC_MIN}; acc_hr <= ${ACC_MAX}; acc_hr += ${ACC_INC} )); do
      # check that the precip accumulations are summable from wrfcf files
      if [ ! $(( ${acc_hr} % ${ANL_INC} )) = 0 ]; then
        msg="ERROR: precip accumulation ${acc_hr} is not a multiple"
        msg+=" of ${ANL_INC}.\n"
        printf "${msg}"
        exit 1
      else
       msg="Computing precipitation accumulation for interval"
       msg+=" ${acc_hr} hours.\n"
       printf "${msg}"
       acc_hrs+=( ${acc_hr} )
      fi
    done
  fi
elif [[ ${CMP_ACC} =~ ${FALSE} ]]; then
  printf "run_preprocessWRF does not compute accumulations.\n"
else
  msg="ERROR: \${CMP_ACC} must be set to 'TRUE' or 'FALSE' to decide if "
  msg+="computing accumulations from wrfcf files."
  printf "${msg}"
  exit 1
fi

# check software dependencies
if [ ! -x ${MET} ]; then
  msg="ERROR: MET singularity image\n ${MET}\n does not exist"
  msg+=" or is not executable.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -x ${MET_TOOLS_PY} ]; then
  msg="ERROR: MET-tools-py singularity image\n ${MET_TOOLS_PY}\n does not exist"
  msg+=" or is not executable.\n"
  printf "${msg}"
  exit 1
fi

if [[ ! -d ${UTLTY} || ! -x ${UTLTY} ]]; then
  msg="ERROR: utility script directory\n ${UTLTY}\n does not exist"
  msg+=" or is not executable.\n"
  exit 1
fi

if [ ! -r ${UTLTY}/config_mpascf.py ]; then
  msg="ERROR: Utility module\n ${UTLTY}/config_mpas.py\n does not exist.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -r ${UTLTY}/mpas_to_cf.py ]; then
  msg="ERROR: Utility script\n ${UTLTY}/mpas_to_cf.py\n does not exist.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -x ${UTLTY}/mpas_to_latlon.sh ]; then
  msg="ERROR: Utility script\n ${UTLTY}/mpas_to_latlon.sh\n does not exist"
  msg+=" or is not executable.\n"
  printf "${msg}"
  exit 1
fi

# check for input data root
if [ -z ${IN_DIR} ]; then
  printf "ERROR: input data directory \${IN_DIR} is not defined.\n"
  exit 1
elif [[ ! -d ${IN_DIR} || ! -x ${IN_DIR} ]]; then
  msg="ERROR: input data directory\n ${IN_DIR}\n"
  msg+=" does not exist or is not executable.\n"
  printf "${msg}"
  exit 1
fi

# create output directory if does not exist
if [ -z ${WRK_DIR} ]; then
  printf "ERROR: work directory \${WRK_DIR} is not defined.\n"
else
  cmd="mkdir -p ${WRK_DIR}"
  printf "${cmd}\n"; eval "${cmd}"
fi

if [[ ! -d ${WRK_DIR} || ! -w ${WRK_DIR} ]]; then
  msg="ERROR: work directory\n ${WRK_DIR}\n does not"
  msg+=" exist or is not writable.\n"
  printf "${msg}"
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# Define directory privileges for singularity exec MET
met="singularity exec -B ${WRK_DIR}:/wrk_dir:rw,${WRK_DIR}:/in_dir:ro ${MET}"

# Define directory privileges for singularity exec MET_TOOLS_PY
met_tools_py="singularity exec -B "
met_tools_py+="${WRK_DIR}:/wrk_dir:rw,${IN_DIR}:/in_dir:ro,${UTLTY}:/utlty:ro "
met_tools_py+="${MET_TOOLS_PY} python"

# clean work directory from previous mpas regridded lat lon files
cmd="rm -f ${WRK_DIR}/*.latlon.*"
printf "${cmd}\n"; eval "${cmd}"

# clean work directory from previous mpascf files
cmd="rm -f ${WRK_DIR}/mpascf*"
printf "${cmd}\n"; eval "${cmd}"

# clean work directory from previous accumulation files
cmd="rm -f ${WRK_DIR}/${CTR_FLW}_*QPF*"
printf "${cmd}\n"; eval "${cmd}"

for (( anl_hr = ${ANL_MIN}; anl_hr <= ${anl_max}; anl_hr += ${ANL_INC} )); do
  # define valid times for mpascf precip evenly spaced
  anl_dt=`date +%Y?%m?%d?%H?%M?%S -d "${cyc_dt} ${anl_hr} hours"`

  # set input file name
  f_in=`ls ${IN_DIR}/*${MPAS_PRFX}.${anl_dt}.nc`

  if [[ -r ${f_in} ]]; then
    # NOTE: convert_mpas always writes outputs to working directory, need to cd
    cmd="cd ${WRK_DIR}"
    printf "${cmd}\n"; eval "${cmd}"

    # cut down to file name alone
    f_in=`basename ${f_in}`

    # if there is no separate mesh IO stream, source from the input file
    if [ "${in_msh_strm}" = "FALSE" ]; then
      in_msh_dir=${IN_DIR}
      in_msh_f=${f_in}
    fi

    # run script from work directory to hold temp outputs from convert_mpas
    cmd="${UTLTY}/mpas_to_latlon.sh ${CONVERT_MPAS} ${WRK_DIR} ${in_msh_dir} ${in_msh_f} ${IN_DIR} ${f_in}"
    printf "${cmd}\n"
    ${UTLTY}/mpas_to_latlon.sh ${CONVERT_MPAS} ${WRK_DIR} ${in_msh_dir} ${in_msh_f} ${IN_DIR} ${f_in}
    error=$?

    if [ ${error} -ne 0 ]; then
      printf "ERROR: mpas_to_latlon.sh did not complete successfully.\n"
      exit 1
    fi

    # set temporary lat-lon file name from work directory
    f_tmp=`ls *latlon.*${anl_dt}.nc`

    # set output cf file name, convert to cf from latlon tmp
    # NOTE: currently convert_mpas doesn't carry time coords from input
    # to regridded output, f_in is reused here to recover timing information
    anl_dt=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${anl_hr} hours"`
    f_out="mpascf_${anl_dt}.nc"
    cmd="${met_tools_py} /utlty/mpas_to_cf.py"
    cmd+=" '/wrk_dir/${f_tmp}' '/wrk_dir/${f_out}' '/in_dir/${f_in}'"
    printf "${cmd}\n"; eval "${cmd}"

  else
    msg="Input file\n ${f_in}\n is not readable or "
    msg+="does not exist, skipping forecast initialization ${CYC_DT}, "
    msg+="forecast hour ${anl_hr}.\n"
    printf "${msg}"
  fi
  if [[ ${CMP_ACC} = ${TRUE} ]]; then
    for acc_hr in ${acc_hrs[@]}; do
      if [ ${anl_hr} -ge ${acc_hr} ]; then
        # define accumulation start / stop hours
        acc_strt=$(( ${anl_hr}  - ${acc_hr} ))
        acc_stop=${anl_hr}

        # start / stop date strings
        anl_strt=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${acc_strt} hours"`
        anl_stop=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${acc_stop} hours"`

        # define padded forecast hour for name strings
        pdd_hr=`printf %03d $(( 10#${anl_hr} ))`

        # CTR_FLW QPF file name convention following similar products
        mpas_acc=${CTR_FLW}_${acc_hr}QPF_${CYC_DT}_F${pdd_hr}.nc

        # Combine precip to accumulation period
        cmd="${met} pcp_combine \
        -subtract /in_dir/mpascf_${anl_stop}.nc /in_dir/mpascf_${anl_strt}.nc\
        /wrk_dir/${mpas_acc} \
        -field 'name=\"precip\"; level=\"(0,*,*)\";'\
        -name \"QPF_${acc_hr}hr\" "
        printf "${cmd}\n"; eval "${cmd}"
      fi
    done
  fi
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`,"
msg+="verify outputs at \${WRK_DIR}:\n ${WRK_DIR}\n"
printf "${msg}"

#################################################################################
# end

exit 0
