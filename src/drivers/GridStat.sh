#################################################################################
# Description
#################################################################################
# The purpose of this script is to compute grid statistics using MET
# after pre-procssing model forecast and ground truth data for verifying
# forecast skill.
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
  printf "GenEnsProd breaks on missing data.\n"
elif [[ ${FULL_DATA} =~ ${FALSE} ]]; then
  printf "GenEnsProd allows missing data.\n"
else
  msg="ERROR: \${FULL_DATA} must be set to 'TRUE' or 'FALSE' to decide if "
  msg+="missing input data is allowed."
  printf "${msg}"
  exit 1
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
    msg="ERROR: max precip accumulation interval ${ACC_MAX} must be greater"
    msg+=" than min accumulation interval ${ACC_MIN}.\n"
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
  msg+="computing statistics on accumulation fields."
  printf "${msg}"
  exit 1
fi

if [[ ! ${CYC_DT} =~ ${INT_RE} ]]; then
  msg="ERROR: cycle date directory string \${CYC_DT}\n ${CYC_DT}\n is not numeric."
  printf "${msg}"
  exit 1
else
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

if [ -z ${EXP_VRF} ]; then
  anl_max="${ANL_MAX}"
  msg="No stop date is set - GenEnsProd runs until max forecast"
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

# define the verification field
if [ -z "${VRF_REF}" ]; then
  printf "ERROR: verification obs type \${VRF_REF} is not defined.\n"
  exit 1
fi

# define the verification field
if [ -z "${VRF_FLD}" ]; then
  printf "ERROR: verification field \${VRF_FLD} is not defined.\n"
  exit 1
fi

if [ -z "${CAT_THR}" ]; then
  printf "ERROR: thresholds \${CAT_THR} is not defined.\n"
  exit 1
fi

# List of landmasks for verification region, file name with extension
if [ -z ${MSK_LST} ]; then
  printf "ERROR: landmask list file \${MSK_LST} is not defined.\n"
  exit 1
elif [ ! -r ${MSK_LST} ]; then
  msg="ERROR: landmask list file\n ${MSK_LST}\n does not exist or is"
  msg+=" not readable.\n"
  printf "${msg}"
  exit 1
elif [ -z ${MSK_GRDS} ]; then
  printf "ERROR: landmask directory \${MSK_GRDS} is not defined.\n"
  exit 1
elif [[ ! -d ${MSK_GRDS} || ! -x ${MSK_GRDS} ]]; then
  msg="ERROR: landmask directory ${MSK_GRDS} does not exist or is not"
  msg+=" executable.\n"
  printf "${msg}"
  exit 1
else
  # loop lines of the mask list, set temporary exit status before searching for masks
  error_check=0
  while read msk; do
    fpath=${MSK_GRDS}/${msk}_${VRF_REF}.nc
    if [ -r "${fpath}" ]; then
      printf "Found\n ${fpath}\n landmask.\n"
    else
      msg="ERROR: verification region landmask\n ${fpath}\n"
      msg+=" does not exist or is not readable.\n"
      printf "${msg}"
      # create exit status flag to kill program, after checking all files in list
      error_check=1
    fi
  done < "${MSK_LST}"
  if [ ${error_check} -eq 1 ]; then
    msg="ERROR: Exiting due to missing landmasks, please see the above error "
    msg+="messages and verify the location for these files. These files can be "
    msg+="generated from lat-lon text files using the run_vxmask.sh script."
    printf "${msg}"
    exit 1
  fi
fi

# neighborhood width for neighborhood methods
if [[ ! ${NBRHD_WDTH} =~ ${INT_RE} ]]; then
  msg="ERROR: neighborhood statistics width \${NBRHD_WDTH}\n ${NBRHD_WDTH}\n"
  msg+=" is not an integer.\n"
  exit 1
fi

# number of bootstrap resamplings, set equal to 0 to turn off
if [[ ! ${BTSTRP} =~ ${INT_RE} || ${BTSTRP} -lt 0 ]]; then
  msg="ERROR: bootstrap resampling iterations \${BTSRP} is not a non-negative"
  msg+=" integer, set \${BTSTRP} to a positive integer or to 0 to turn off.\n"
  printf "${msg}"
  exit 1
fi

# rank correlation computation flag, TRUE or FALSE
if [[ ${RNK_CRR} != "TRUE" && ${RNK_CRR} != "FALSE" ]]; then
  msg="ERROR: \${RNK_CRR} must be set to 'TRUE' or 'FALSE' to decide "
  msg+="if computing rank statistics.\n"
  printf "${msg}"
  exit 1
fi

# control flow to be processed
if [ -z ${CTR_FLW} ]; then
  printf "ERROR: control flow name \${CTR_FLW} is not defined.\n"
  exit 1
fi

# define the interpolation neighborhood size
if [[ ! ${INT_WDTH} =~ ${INT_RE} ]]; then 
  msg="ERROR: interpolation neighborhood width \${INT_WDTH}\n ${INT_WDTH}\n"
  msg+=" is not an integer.\n"
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

# if GenEnsProd output for ensemble mean verification
if [[ ${IF_ENS_PRD} =~ ${TRUE} ]]; then
  if [ -z ${ENS_PAD+x} ]; then
    msg="ERROR: ensemble index padding \${ENS_PAD} is undeclared, set to empty"
    msg+=" string if not used.\n"
    printf "${msg}"
    exit 1
  elif [[ ! ${ENS_PAD} =~ ${INT_RE} ]]; then
    msg="ERROR: ensemble index padding \${ENS_PAD}\n ${ENS_PAD}\n is not"
    msg+=" an integer.\n"
    printf "${msg}"
    exit 1
  elif [ -z ${ENS_PRFX+x} ]; then
    msg="ERROR: ensemble member prefix to index value"
    msg+=" is undeclared, set to empty string if not used.\n"
    printf "${msg}"
    exit 1
  fi
  if [[ ! ${ENS_MIN} =~ ${INT_RE} ]]; then
    msg="ERROR: min ensemble index \${ENS_MIN}\n ${ENS_MIN}\n is not"
    msg+=" an integer.\n"
    printf "${msg}"
    exit 1
  else
    # ensure correct padding
    ens_min=`printf %0${ENS_PAD}d $(( 10#${ens_min} ))`
  fi
  if [[ ! ${ENS_MAX} =~ ${INT_RE} ]]; then
    msg="ERROR: max ensemble index \${ENS_MAX}\n ${ENS_MAX}\n is not"
    msg+="an integer.\n"
    printf "${msg}"
    exit 1
  else
    # ensure correct padding
    ens_max=`printf %0${ENS_PAD}d $(( 10#${ENS_MAX} ))`
  fi
  if [ ${ens_min} -lt 0 ]; then
    printf "ERROR: min ensemble index ${ENS_MIN} must be non-negative.\n"
    exit 1
  elif [ ${ens_max} -lt ${ens_min} ]; then
    msg="ERROR: max ensemble index ${ENS_MAX} must be greater than or equal"
    msg+=" to the minimum ensemble index.\n"
    printf "${msg}"
    exit 1
  fi
  pstfx="_${ENS_PRFX}${ens_min}-${ENS_PRFX}${ens_max}_prd"
  msg="Computing gridstat on ${CTR_FLW} ensemble product from members"
  msg+=" ${ens_min} to ${ens_max}.\n"
  printf "${msg}"
elif [[ ${IF_ENS_PRD} =~ ${FALSE} ]]; then
  pstfx=""
  printf "Computing gridstat on non-ensemble product.\n"
else
  msg="ERROR: \${IF_ENS_PRD} must be TRUE or FALSE (case insensitive)"
  msg+=" if verifying GenEnsProd output.\n"
  printf "${msg}"
  exit 1
fi

# check for software and data deps.
if [ -z ${STC_ROOT} ]; then
  printf "ERROR: \${STC_ROOT} is not defined.\n"   
  exit 1
elif [[ ! -d ${STC_ROOT} || ! -x ${STC_ROOT} ]]; then
  msg="ERROR: static verification data directory\n ${STC_ROOT}\n"
  msg+=" does not exist or is not executable.\n"
  printf "${msg}"
  exit 1
fi

if [ -z ${MET_VER} ]; then
  msg="MET version \${MET_VER} is not defined.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -x ${MET} ]; then
  msg="MET singularity image\n ${MET}\n does not exist or is not executable.\n"
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

if [ ! -r ${UTLTY}/DataFrames.py ]; then
  msg="ERROR: Utility module\n ${UTLTY}/DataFrames.py\n"
  msg+=" does not exist.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -r ${UTLTY}/ASCII_to_DataFrames.py ]; then
  msg="ERROR: Utility script\n ${UTLTY}/ASCII_to_DataFrames.py\n"
  msg+=" does not exist.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -r ${SHARED}/GridStatConfigTemplate ]; then
  msg="GridStatConfig template \n ${SHARED}/GridStatConfigTemplate\n"
  msg+=" does not exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# Define directory privileges for singularity exec
met="singularity exec -B ${WRK_DIR}:/wrk_dir:rw,"
met+="${STC_ROOT}:/STC_ROOT:ro,${MSK_GRDS}:/MSK_GRDS:ro,"
met+="${IN_DIR}:/in_dir:ro ${MET}"

# Define directory privileges for singularity exec MET_TOOLS_PY
met_tools_py="singularity exec -B "
met_tools_py+="${WRK_DIR}:/wrk_dir:rw,${WRK_DIR}:/in_dir:ro,${SRC}:/src_dir:ro "
met_tools_py+="${MET_TOOLS_PY} python"

# clean old data
rm -f ${WRK_DIR}/grid_stat_${VRF_FLD}*.txt
rm -f ${WRK_DIR}/grid_stat_${VRF_FLD}*.stat
rm -f ${WRK_DIR}/grid_stat_${VRF_FLD}*.nc
rm -f ${WRK_DIR}/GridStatConfig_${VRF_FLD}*
rm -f ${WRK_DIR}/PLY_MSK.txt

# loop lines of the mask list, generate PLY_MSK.txt for GridStatConfig insert
msk_count=`wc -l < ${MSK_LST}`
line_count=1
while read msk; do
  if [ ${line_count} -lt ${msk_count} ]; then
    ply_msk="\"/MSK_GRDS/${msk}_${VRF_REF}.nc\",\n"
    printf ${ply_msk} >> ${WRK_DIR}/PLY_MSK.txt
  else
    ply_msk="\"/MSK_GRDS/${msk}_${VRF_REF}.nc\""
    printf ${ply_msk} >> ${WRK_DIR}/PLY_MSK.txt
  fi
  line_count=$(( ${line_count} + 1 ))
done <${MSK_LST}

# create trigger for handling errors
error_check=0

# loop lead hours for forecast valid time for each initialization time
for (( anl_hr = ${ANL_MIN}; anl_hr <= ${anl_max}; anl_hr += ${ANL_INC} )); do
  # define valid times for verification
  anl_dt=`date +%Y%m%d%H -d "${cyc_dt} ${anl_hr} hours"`
  pdd_hr=`printf %03d $(( 10#${anl_hr} ))`

  for acc_hr in ${acc_hrs[@]}; do
    if [[ ${CMP_ACC} =~ ${TRUE} && ${acc_hr} -le ${anl_hr} ]]; then
      for_in=${CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}${pstfx}.nc
      if [[ ${IF_ENS_PRD} =~ ${TRUE} ]]; then
        fld=${VRF_FLD}_${acc_hr}hr_0_all_all_ENS_MEAN
      else
        fld=${VRF_FLD}_${acc_hr}hr
      fi

      # obs file defined in terms of valid time, path relative to STC_ROOT
      if [[ "${VRF_REF}" = "StageIV" ]]; then
        obs_in=StageIV/StageIV_QPE_${anl_dt}.nc
      fi

      if [ -r ${IN_DIR}/${for_in} ]; then
        if [ -r ${STC_ROOT}/${obs_in} ]; then
          # update GridStatConfigTemplate archiving file in working directory
          # this remains unchanged on inner loop
          if [ ! -r ${WRK_DIR}/GridStatConfig_${VRF_FLD}_${acc_hr}hr ]; then
            cat ${SHARED}/GridStatConfigTemplate \
              | sed "s/CTR_FLW/model = \"${CTR_FLW}\"/" \
              | sed "s/INT_WDTH/width = ${INT_WDTH}/" \
              | sed "s/RNK_CRR/rank_corr_flag      = ${RNK_CRR}/" \
              | sed "s/VRF_FLD/name       = \"${fld}\"/" \
              | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
              | sed "/PLY_MSK/r ${WRK_DIR}/PLY_MSK.txt" \
              | sed "/PLY_MSK/d " \
              | sed "s/BTSTRP/n_rep    = ${BTSTRP}/" \
              | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
              | sed "s/PRFX/output_prefix    = \"${VRF_FLD}_${acc_hr}hr\"/" \
              | sed "s/MET_VER/version           = \"V${MET_VER}\"/" \
              > ${WRK_DIR}/GridStatConfig_${VRF_FLD}_${acc_hr}hr
          fi

          # Run gridstat
          cmd="${met} grid_stat -v 10 \
          /in_dir/${for_in} \
          /STC_ROOT/${obs_in} \
          /wrk_dir/GridStatConfig_${VRF_FLD}_${acc_hr}hr \
          -outdir /wrk_dir; error=\$?"
          printf "${cmd}\n"; eval "${cmd}"
          printf "grid_stat exited with status ${error}.\n"
          if [ ${error} -ne 0 ]; then
            msg="ERROR: grid_stat failed to produce verification for input\n"
            msg+=" ${for_in}\n and ground truth\n ${obs_in}\n"
            printf "${msg}" 
            error_check=1
          fi
          
        else
          if [[ ${FULL_DATA} =~ ${TRUE} ]]; then
            msg="ERROR: Observation verification file\n ${STC_ROOT}/${obs_in}\n"
            msg+=" is not readable or does not exist.\n"
            printf "${msg}"
            error_check=1
          else
            msg="WARNING: Observation verification file\n ${STC_ROOT}/${obs_in}\n"
            msg+=" is not readable or does not exist, skipping grid_stat for"
            msg+=" forecast initialization ${CYC_DT}, forecast hour ${anl_hr}.\n"
            printf "${msg}"
          fi
        fi
      else
        if [[ ${FULL_DATA} =~ ${TRUE} ]]; then
          msg="ERROR: gridstat input file\n ${IN_DIR}/${for_in}\n is not"
          msg+=" readable or does not exist.\n"
          printf "${msg}"
          error_check=1
        else
          msg="WARNING: gridstat input file\n ${IN_DIR}/${for_in}\n is not"
          msg+=" readable or does not exist, skipping grid_stat for forecast"
          msg+=" initialization ${CYC_DT}, forecast hour ${anl_hr}.\n"
          printf "${msg}"
        fi
      fi

      # clean up working directory from accumulation time
      cmd="rm -f ${WRK_DIR}/${for_in}"
      printf "${cmd}\n"; eval "${cmd}"
    elif [[ ${CMP_ACC} =~ ${FALSE} ]]; then
      for_in=${CTR_FLW}_${VRF_FLD}_${CYC_DT}_F${pdd_hr}${pstfx}.nc

      if [[ ${IF_ENS_PRD} =~ ${TRUE} ]]; then
        fld=${VRF_FLD}_0_all_all_ENS_MEAN
      else
        fld=${VRF_FLD}
      fi

      # obs file defined in terms of valid time
      obs_in=${VRF_REF}_${VRF_FLD}_${CYC_DT}_F${pdd_hr}.nc
      
      if [ -r ${IN_DIR}/${for_in} ]; then
        if [ -r ${STC_ROOT}/${obs_in} ]; then
          # update GridStatConfigTemplate archiving file in working directory
          # this remains unchanged on inner loop
          if [ ! -r ${WRK_DIR}/GridStatConfig_${VRF_FLD} ]; then
            cat ${SHARED}/GridStatConfigTemplate \
              | sed "s/CTR_FLW/model = \"${CTR_FLW}\"/" \
              | sed "s/INT_WDTH/width = ${INT_WDTH}/" \
              | sed "s/RNK_CRR/rank_corr_flag      = ${RNK_CRR}/" \
              | sed "s/VRF_FLD/name       = \"${fld}\"/" \
              | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
              | sed "/PLY_MSK/r ${WRK_DIR}/PLY_MSK.txt" \
              | sed "/PLY_MSK/d " \
              | sed "s/BTSTRP/n_rep    = ${BTSTRP}/" \
              | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
              | sed "s/PRFX/output_prefix    = \"${VRF_FLD}\"/" \
              | sed "s/MET_VER/version           = \"V${MET_VER}\"/" \
              > ${WRK_DIR}/GridStatConfig_${VRF_FLD}
          fi

          # Run gridstat
          cmd="${met} grid_stat -v 10 \
          /in_dir/${for_in} \
          /STC_ROOT/${obs_in} \
          /wrk_dir/GridStatConfig_${VRF_FLD} \
          -outdir /wrk_dir; error=\$?"
          printf "${cmd}\n"; eval "${cmd}"
          printf "grid_stat exited with status ${error}.\n"
          if [ ${error} -ne 0 ]; then
            msg="ERROR: grid_stat failed to produce verification for input\n"
            msg+=" ${for_in}\n and ground truth\n ${obs_in}\n"
            printf "${msg}" 
            error_check=1
          fi
        else
          if [[ ${FULL_DATA} =~ ${TRUE} ]]; then
            msg="ERROR: Observation verification file\n ${STC_ROOT}/${obs_in}\n"
            msg+=" is not readable or does not exist.\n"
            printf "${msg}"
            error_check=1
          else
            msg="WARNING: Observation verification file\n ${STC_ROOT}/${obs_in}\n"
            msg+=" is not readable or does not exist, skipping grid_stat for"
            msg+=" forecast initialization ${CYC_DT}, forecast hour ${anl_hr}.\n"
            printf "${msg}"
          fi
        fi
      else
        if [[ ${FULL_DATA} =~ ${TRUE} ]]; then
          msg="ERROR: gridstat input file\n ${IN_DIR}/${for_in}\n is not"
          msg+=" readable or does not exist.\n"
          printf "${msg}"
          error_check=1
        else
          msg="WARNING: gridstat input file\n ${IN_DIR}/${for_in}\n is not"
          msg+=" readable or does not exist, skipping grid_stat for forecast"
          msg+=" initialization ${CYC_DT}, forecast hour ${anl_hr}.\n"
          printf "${msg}"
        fi
      fi

      # clean up working directory from accumulation time
      cmd="rm -f ${WRK_DIR}/${for_in}"
      printf "${cmd}\n"; eval "${cmd}"
    fi
  done
done

# clean up working directory from forecast start time
cmd="rm -f ${WRK_DIR}/*_StageIV.nc"
printf "${cmd}\n"; eval "${cmd}"

cmd="rm -f ${WRK_DIR}/PLY_MSK.txt"
printf "${cmd}\n"; eval "${cmd}"

if [[ ${CMP_ACC} =~ ${TRUE} ]]; then
  for acc_hr in ${acc_hrs[@]}; do 
    # run makeDataFrames to parse the ASCII outputs
    cmd="${met_tools_py} /src_dir/utilities/ASCII_to_DataFrames.py"
    cmd+=" '${VRF_FLD}_${acc_hr}hr' '/in_dir' '/wrk_dir'; error=\$?"
    printf "${cmd}\n"; eval "${cmd}"
    printf "ASCII_to_DataFrames.py exited with status ${error}.\n"
    if [ ${error} -ne 0 ]; then
      msg="ERROR: ASCII_to_DataFrames.py failed to produce parsed binaries.\n"
      printf "${msg}"
      error_check=1
    fi
  done
else
  # run makeDataFrames to parse the ASCII outputs
  cmd="${met_tools_py} /src_dir/utilities/ASCII_to_DataFrames.py"
  cmd+=" '${VRF_FLD}' '/in_dir' '/wrk_dir'; error=\$?"
  printf "${cmd}\n"; eval "${cmd}"
  printf "ASCII_to_DataFrames.py exited with status ${error}.\n"
  if [ ${error} -ne 0 ]; then
    msg="ERROR: ASCII_to_DataFrames.py failed to produce parsed binaries.\n"
    printf "${msg}"
    error_check=1
  fi
fi

if [ ${error_check} = 1 ]; then
  printf "ERROR: GridStat.sh failed on one or more analyses.\n"
  printf "Check above error messages to diagnose issues.\n"
  exit 1
fi

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at:\n ${WRK_DIR}\n"
printf "${msg}"

#################################################################################
# end

exit 0
