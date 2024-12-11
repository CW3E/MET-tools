#!/bin/bash
#################################################################################
# Description
#################################################################################
# This script runs a batch processing routine for a given control flow /
# grid configuration and date range as defined in the companion batch and config
# scripts. This driver script loops the calls to the WRF preprocessing script
# wrfout_to_cf.py to ready WRF outputs for MET, and will optionally compute
# accumulated precip in addition.
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
#################################################################################
# CHECK WORKFLOW PARAMETERS
#################################################################################

if [ ! -x ${CNST} ]; then
  msg="ERROR: constants file\n ${CNST}\n does not exist or is not executable.\n"
  printf "${msg}"
  exit 1
else
  # Read constants into the current shell
  cmd=". ${CNST}"
  printf "${cmd}\n"; eval "${cmd}"
fi

if [[ ${FULL_DATA} =~ ${TRUE} ]]; then
  printf "Preprocessing breaks on missing data.\n"
elif [[ ${FULL_DATA} =~ ${FALSE} ]]; then
  printf "Preprocessing allows missing data.\n"
else
  msg="ERROR: \${FULL_DATA} must be set to 'TRUE' or 'FALSE' to decide if "
  msg+="missing input data is allowed."
  printf "${msg}"
  exit 1
fi

# define the increment at which to process forecast outputs (HH)
if [[ ! ${ANL_INC} =~ ${INT_RE} ]]; then
  msg="ERROR: hours increment between analyses \${ANL_INC},\n ${ANL_INC}\n"
  msg+=" is not an integer.\n"
  printf "${msg}"
  exit 1
elif [ ! $(( (${ANL_MAX} - ${ANL_MIN}) % ${ANL_INC} )) = 0 ]; then
  msg="ERROR: the interval [\${ANL_MIN}, \${ANL_MAX}]\n"
  msg+=" [${ANL_MIN}, ${ANL_MAX}]\n" 
  msg+=" must be evenly divisible into increments of \${ANL_INC}, ${ANL_INC}.\n"
  printf "${msg}"
  exit 1
fi

# compute accumulation from cf file, TRUE or FALSE
if [[ ${PCP_PRD} =~ ${TRUE} ]]; then
  pcp_prd=1
  printf "run_preprocessWRF creates accumulated precip products.\n"
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
  elif [[ ! ${ACC_INT} =~ ${INT_RE} ]]; then
    msg="ERROR: interval between computing precip accumulations \${ACC_INT}"
    msg+=" is not integer.\n"
    printf "${msg}"
    exit 1
  elif [ ! $(( (${ACC_MAX} - ${ACC_MIN}) % ${ACC_INC} )) = 0 ]; then
    msg="ERROR: the interval [\${ACC_MIN}, \${ACC_MAX}]\n"
    msg+=" [${ACC_MIN}, ${ACC_MAX}] must be evenly divisible into\n"
    msg+=" increments of \${ACC_INC}, ${ACC_INC}.\n"
    printf "${msg}"
    exit 1
  elif [ ! $(( ${ACC_INT} % ${ANL_INC} )) = 0 ]; then
    msg="ERROR: the interval at which precip accumulations are computed,"
    msg+=" \${ACC_INT}, ${ACC_INT} is not divisible by the interval at"
    msg+=" which cf files are created, ${ANL_INC}.\n" 
    printf "${msg}"
    exit 1
  else
    # define array of accumulation interval computation hours
    acc_hrs=()
    for (( acc_hr=${ACC_MIN}; acc_hr <= ${ACC_MAX}; acc_hr += ${ACC_INC} )); do
      # check that the precip accumulations are summable from cf files
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
elif [[ ${PCP_PRD} =~ ${FALSE} ]]; then
  pcp_prd=0
  printf "run_preprocessWRF does not compute accumulations.\n"
else
  msg="ERROR: \${PCP_PRD} must be set to 'TRUE' or 'FALSE' to decide if "
  msg+="computing accumulations from cf files."
  printf "${msg}"
  exit 1
fi

# create averaged IVT product from cf file, TRUE or FALSE
if [[ ${IVT_PRD} =~ ${TRUE} ]]; then
  ivt_prd=1
  printf "run_preprocessWRF creates averaged IVT products.\n"
  if [[ ! ${IVT_AVG} =~ ${INT_RE} ]]; then
    msg="ERROR: IVT average window \${IVT_AVG},\n ${IVT_AVG}\n"
    msg+=" is not an integer.\n"
    printf "${msg}"
    exit 1
  elif [[ ! ${IVT_INC} =~ ${INT_RE} ]]; then
    msg="ERROR: hour increment between IVT files \${IVT_INC},\n ${IVT_INC}\n"
    msg+=" is not an integer.\n"
    printf "${msg}"
    exit 1
  elif [[ ! ${IVT_INT} =~ ${INT_RE} ]]; then
    msg="ERROR: hour increment between IVT averags \${IVT_INT},\n ${IVT_INT}\n"
    msg+=" is not an integer.\n"
    printf "${msg}"
    exit 1
  elif [ ! $(( ${IVT_AVG} % ${IVT_INC} )) = 0 ]; then
    msg="ERROR: the interval [0, \${IVT_AVG}]\n"
    msg+=" [0, ${IVT_AVG}] must be evenly divisible into\n"
    msg+=" increments of \${IVT_INC}, ${IVT_INC}.\n"
    printf "${msg}"
    exit 1
  elif [ ! $(( ${IVT_INT} % ${ANL_INC} )) = 0 ]; then
    msg="ERROR: the interval at which IVT averages are taken, \${IVT_INT},"
    msg+=" ${IVT_INT} is not divisible by the interval at which cf files"
    msg+=" are created, ${ANL_INC}.\n" 
    printf "${msg}"
    exit 1
  fi
elif [[ ${IVT_PRD} =~ ${FALSE} ]]; then
  ivt_prd=0
  printf "run_preprocessWRF does not create averaged IVT products.\n"
else
  msg="ERROR: \${IVT_PRD} must be set to 'TRUE' or 'FALSE' to decide if "
  msg+="creating IVT products from cf files."
  printf "${msg}"
  exit 1
fi

if [[ ${RGRD} =~ ${TRUE} ]]; then
  # standard coordinates that can be used to regrid West-WRF
  printf "WRF outputs will be regridded for MET compatibility.\n"
  rgrd="1"
elif [[ ${RGRD} =~ ${FALSE} ]]; then
  printf "WRF outputs will be used with MET in their native grid.\n"
  rgrd="0"
else
  printf "ERROR: \${RGRD} must equal 'TRUE' or 'FALSE' (case insensitive).\n"
  exit 1
fi

if [ -z ${WRF_PRFX} ]; then
  msg="ERROR: WRF file type \${WRF_PRFX} is undefined.  Supply an output"
  msg+=" name e.g., wrfout / wrfcf, to source fields from.\n"
  printf "${msg}"
  exit 1
fi

if [[ ! ${CYC_DT} =~ ${ISO_RE} ]]; then
  msg="ERROR: cycle date \${CYC_DT}\n ${CYC_DT}\n"
  msg+=" is not in YYYYMMDDHH format.\n"
  printf "${msg}"
  exit 1
else
  # Convert CYC_DT from 'YYYYMMDDHH' format to cyc_dt Unix date format
  cyc_dt="${CYC_DT:0:8} ${CYC_DT:8:2}"
  cyc_dt=`date -d "${cyc_dt}"`
fi

# define min / max forecast hours for forecast outputs to be processed
if [[ ! ${ANL_MIN} =~ ${INT_RE} ]]; then
  msg="ERROR: min forecast hour \${ANL_MIN},\n ${ANL_MIN}\n is not"
  msg+=" an integer.\n"
  printf "${msg}"
  exit 1
elif [ ${ANL_MIN} -lt 0 ]; then
  printf "ERROR: min forecast hour ${ANL_MIN} must be non-negative.\n"
  exit 1
elif [[ ! ${ANL_MAX} =~ ${INT_RE} ]]; then
  msg="ERROR: max forecast hour \${ANL_MAX},\n ${ANL_MAX}\n is not"
  msg+=" an integer.\n"
  printf "${msg}"
  exit 1
elif [ ${ANL_MAX} -lt ${ANL_MIN} ]; then
  msg="ERROR: max forecast hour ${ANL_MAX} must be greater than or equal to"
  msg+="min forecast hour ${ANL_MIN}.\n"
  printf "${msg}"
  exit 1
fi

if [ -z ${EXP_VRF} ]; then
  anl_max="${ANL_MAX}"
  msg="No stop date is set - preprocessWRF runs until max forecast"
  msg+=" hour ${ANL_MAX}.\n"
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

if [ -z ${INIT_OFFSET} ]; then
  init_offset=0
  msg="No forecast initialization offset is defined, cf files will inherit"
  msg+=" initialization time from wrf outputs.\n"
  printf "${msg}"
elif [[ ! ${INIT_OFFSET} =~ ${INT_RE} ]]; then
  msg="ERROR: forecast initialization offset,\n ${INIT_OFFSET}\n"
  msg+=" is not integer.\n"
  printf "${msg}"
  exit 1
else
  init_offset=$(( 10#${INIT_OFFSET} ))
fi

# control flow to be processed
if [ -z ${CTR_FLW} ]; then
  printf "ERROR: control flow name \${CTR_FLW} is not defined.\n"
  exit 1
fi

# verification domain for the forecast data
if [[ ! ${GRD} =~ ^d[0-9]{2}$ ]]; then
  printf "ERROR: grid name \${GRD},\n ${GRD}\n must be in dXX format.\n"
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
  printf "${msg}"
  exit 1
fi

if [ ! -r ${UTLTY}/WRF_cf.py ]; then
  msg="ERROR: Utility module\n ${UTLTY}/WRF_cf.py\n does not exist.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -r ${UTLTY}/wrfout_to_cf.py ]; then
  msg="ERROR: Utility script\n ${UTLTY}/wrfout_to_cf.py\n does not exist.\n"
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
met_tools_py+="${WRK_DIR}:/wrk_dir:rw,${IN_DIR}:/in_dir:ro,${SRC}:/src_dir:ro "
met_tools_py+="${MET_TOOLS_PY} python"

# move to work directory
cmd="cd ${WRK_DIR}"
printf "${cmd}\n"; eval "${cmd}"

# clean work directory from previous files
cmd="rm -f wrfcf*; rm -f ${CTR_FLW}_*"
printf "${cmd}\n"; eval "${cmd}"

# create trigger for handling errors
error_check=0

for (( anl_hr = ${ANL_MIN}; anl_hr <= ${anl_max}; anl_hr += ${ANL_INC} )); do
  # define valid times for wrfcf precip evenly spaced
  anl_dt=`date +%Y?%m?%d?%H?%M?%S -d "${cyc_dt} ${anl_hr} hours"`

  # set input file names
  f_in=`ls ${IN_DIR}/*${WRF_PRFX}*_${GRD}_${anl_dt}`
  
  if [[ -r ${f_in} ]]; then
    # Cut system path from input file
    f_in=`basename ${f_in}`

    # Reset date string with underscore formatting
    anl_dt=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${anl_hr} hours"`

    # set output file name with underscore formatting
    f_out="wrfcf_${anl_dt}.nc"

    cmd="${met_tools_py} /src_dir/utilities/wrfout_to_cf.py"
    cmd+=" '/in_dir/${f_in}' '/wrk_dir/${f_out}' '${pcp_prd}' '${ivt_prd}'"
    cmd+=" '${rgrd}' '${init_offset}'; error=\$?"
    printf "${cmd}\n"; eval "${cmd}"
    printf "wrfout_to_cf.py exited with status ${error}.\n"
    if [ ${error} -ne 0 ]; then
      msg="ERROR: wrfout_to_cf.py failed to produce cf file\n"
      msg+=" ${f_out}\n"
      printf "${msg}"
      error_check=1
    fi
  else
    if [[ ${FULL_DATA} =~ ${TRUE} ]]; then
      f_in="${IN_DIR}/wrfout_${GRD}_${anl_dt}"
      msg="ERROR: no input file matching pattern\n ${f_in}\n is readable.\n"
      printf "${msg}"
      error_check=1
    else
      f_in="${IN_DIR}/wrfout_${GRD}_${anl_dt}"
      msg="WARNING: no input file matching pattern\n ${f_in}\n is readable,"
      msg+=" skipping forecast hour ${anl_hr}.\n"
      printf "${msg}"
    fi
  fi
  if [[ ${IVT_PRD} =~ ${TRUE} ]]; then
    if [[ ${anl_hr} -ge ${IVT_AVG} && $(( ${anl_hr} % ${IVT_INT} )) -eq 0 ]]; then
      # set flag to skip computing accumulation if missing files
      avg_check=1
      avg_files=()

      for (( back_hr = ${IVT_AVG}; back_hr >= 0; back_hr -= ${IVT_INC} )); do
        # Currently looking backward to hr_val
        hr_val=$(( ${anl_hr}  - ${back_hr} ))
        hr_iso=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${hr_val} hours"`
        cf_file="wrfcf_${hr_iso}.nc"

        if [ ! -r "${WRK_DIR}/${cf_file}" ]; then
          if [[ ${FULL_DATA} =~ ${TRUE} ]]; then
            msg="ERROR: cf file\n ${WRK_DIR}/${cf_file}\n does not exist" 
            msg+=" or is not readable to compute forecast hour ${anl_hr} IVT"
            msg+=" averaged over previous ${IVT_AVG} hours.\n"
            error_check=1
            printf "${msg}"
          else
            msg="WARNING: cf file\n ${WRK_DIR}/${cf_file}\n does not exist" 
            msg+=" or is not readable, skipping forecast hour ${anl_hr} /"
            msg+=" averaged over ${IVT_AVG} hours.\n"
            printf "${msg}"
          fi
        else
          # store readable files in a list
          avg_files+=( "${cf_file}" )

          # At least one file is needed to take the average
          avg_check=0
        fi
      done
      if [ ${avg_check} = 0 ]; then
        # define padded forecast hour for name strings
        pdd_hr=`printf %03d $(( 10#${anl_hr} ))`

        # CTR_FLW QPF file name convention following similar products
        cf_avg="${CTR_FLW}_${IVT_AVG}IVT_${CYC_DT}_F${pdd_hr}.nc"

        # Combine precip to accumulation period
        cmd="${met} pcp_combine -derive mean "
        for fname in ${avg_files[@]}; do
          cmd+="/in_dir/${fname} "
        done
        cmd+="/wrk_dir/${cf_avg} \
        -field 'name=\"IVT\"; level=\"(0,*,*)\";'\
        -name \"IVT_${IVT_AVG}hr\"; error=\$?"
        printf "${cmd}\n"; eval "${cmd}"
        printf "pcp_combine exited with status ${error}.\n"
        if [ ${error} -ne 0 ]; then
          error_check=1
          msg="ERROR: pcp_combine failed to produce average file\n"
          msg+=" ${cf_avg}\n"
          printf "${msg}"
        fi
      fi
    fi
  fi
  if [[ ${PCP_PRD} =~ ${TRUE} ]]; then
    for acc_hr in ${acc_hrs[@]}; do
      if [[ ${anl_hr} -ge ${acc_hr} && $(( ${anl_hr} % ${ACC_INT} )) -eq 0 ]]; then
        # define accumulation start / stop hours
        acc_strt=$(( ${anl_hr}  - ${acc_hr} ))
        acc_stop=${anl_hr}

        # set flag to skip computing accumulation if missing files
        acc_check=0

        # start / stop date strings
        anl_strt=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${acc_strt} hours"`
        anl_stop=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${acc_stop} hours"`
        cf_strt="wrfcf_${anl_strt}.nc"
        cf_stop="wrfcf_${anl_stop}.nc"
	cf_files=( "${cf_strt}" "${cf_stop}" )

	for fname in ${cf_files[@]}; do
          if [ ! -r "${WRK_DIR}/${fname}" ]; then
            acc_check=1
            if [[ ${FULL_DATA} =~ ${TRUE} ]]; then
              msg="ERROR: cf file\n ${WRK_DIR}/${fname}\n does not exist" 
              msg+=" or is not readable to compute forecast hour ${anl_hr} /"
              msg+=" accumulation hour ${acc_hr}.\n"
              error_check=1
              printf "${msg}"
            else
              msg="WARNING: cf file\n ${WRK_DIR}/${fname}\n does not exist" 
              msg+=" or is not readable, skipping forecast hour ${anl_hr} /"
              msg+=" accumulation hour ${acc_hr}.\n"
              printf "${msg}"
            fi
          fi
        done
        if [ ${acc_check} = 0 ]; then
          # define padded forecast hour for name strings
          pdd_hr=`printf %03d $(( 10#${anl_hr} ))`

          # CTR_FLW QPF file name convention following similar products
          cf_acc=${CTR_FLW}_${acc_hr}QPF_${CYC_DT}_F${pdd_hr}.nc

          # Combine precip to accumulation period
          cmd="${met} pcp_combine \
          -subtract /in_dir/${cf_stop} /in_dir/${cf_strt}\
          /wrk_dir/${cf_acc} \
          -field 'name=\"precip\"; level=\"(0,*,*)\";'\
          -name \"QPF_${acc_hr}hr\"; error=\$?"
          printf "${cmd}\n"; eval "${cmd}"
          printf "pcp_combine exited with status ${error}.\n"
          if [ ${error} -ne 0 ]; then
            error_check=1
            msg="ERROR: pcp_combine failed to produce accumulation file\n"
            msg+=" ${cf_acc}\n"
            printf "${msg}"
          fi
        fi
      fi
    done
  fi
done

if [ ${error_check} = 1 ]; then
  msg="ERROR: preprocessing did not complete successfully, see above errors.\n"
  printf "${msg}"
  exit 1
else
  msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`,"
  msg+="verify outputs at \${WRK_DIR}:\n ${WRK_DIR}\n"
  printf "${msg}"
fi

#################################################################################
# end

exit 0
