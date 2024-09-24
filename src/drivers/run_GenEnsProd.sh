#################################################################################
# Description
#################################################################################
# The purpose of this script is to compute simple ensemble products using MET
# GenEnsProd Tool after pre-procssing WRF forecast data using WRF-preprocess
# scripts in this repository.
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
  printf "ERROR: constants file\n ${CNST}\n does not exist or is not executable.\n"
  exit 1
else
  # Read constants into the current shell
  cmd=". ${CNST}"
  printf "${cmd}\n"; eval "${cmd}"
fi

# control flow to be processed
if [ -z ${CTR_FLW} ]; then
  printf "ERROR: control flow name \${CTR_FLW} is not defined.\n"
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
  msg="No stop date is set - GenEnsProd runs until max forecast"
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
  exp_vrf=`date +%s -d "${exp_vrf}"`
  # Recompute the max forecast hour with respect to exp_vrf
  anl_max=$(( ${exp_vrf} - `date +%s -d "${cyc_dt}"` ))
  anl_max=$(( ${anl_max} / 3600 ))
  printf "Stop date is set at `date +%Y-%m-%d_%H_%M_%S -d "${exp_vrf}"`.\n"
  printf "Preprocessing stops automatically for forecasts at this time.\n"
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

# ensemble prefix and ens_ids below construct nested paths to loop over and
# link to work directory
if [ -z ${ENS_PRFX+x} ]; then
  msg="ERROR: ensemble member prefix to index value"
  msg+=" is undeclared, set to empty string if not used.\n"
  printf "${msg}"
  exit 1
fi

if [[ ! ${ENS_MIN} =~ ${INT_RE} ]]; then
  printf "ERROR: min ensemble index \${ENS_MIN} is not an integer.\n"
  exit 1
else
  # ensure base 10 for looping
  ens_min=`printf $(( 10#${ENS_MIN} ))`
fi

if [[ ! ${ENS_MAX} =~ ${INT_RE} ]]; then
  printf "ERROR: max ensemble index \${ENS_MAX} is not an integer.\n"
  exit 1
else
  # ensure base 10 for looping
  ens_max=`printf $(( 10#${ENS_MAX} ))`
fi

if [ -z ${CTR_MEM+x} ]; then
  msg="ERROR: control member name \${CTR_MEM} is undeclared, set to empty"
  msg+=" string if not used.\n"
  printf "${msg}"
  exit 1
elif [ -z ${CTR_MEM} ]; then
  printf "No control member is used for ensemble product computation.\n"
  ctr_id=""
  ctr_mem=""
elif [[ ${CTR_MEM} =~ ${INT_RE} ]]; then
  ctr_id="${ENS_PRFX}`printf %0${ENS_PAD}d $(( 10#${CTR_MEM} ))`"
  printf "Ensemble id ${ctr_id} is used as control for ensemble product computation.\n"
  ctr_mem="-ctrl /wrk_dir/${ctr_id}"
else 
  msg="ERROR: \${CTR_MEM}\n ${CTR_MEM}\n should be set to a numerical index"
  msg+=" or to an emptry string \"\" if unused.\n"
  printf "${msg}"
  exit 1
fi

if [ ${ens_min} -lt 0 ]; then
  printf "ERROR: min ensemble index ${ENS_MIN} must be non-negative.\n"
  exit 1
elif [ ${ens_max} -lt ${ens_min} ]; then
  msg="ERROR: max ensemble index ${ENS_MAX} must be greater than or equal"
  msg+=" to the minimum ensemble index.\n"
  exit 1
else 
  # define array of ensemble member ids, padded ${ENS_PAD} digits
  mem_ids=()
  for (( ens_id=${ens_min}; ens_id <= ${ens_max}; ens_id++ )); do
    mem_id=${ENS_PRFX}`printf %0${ENS_PAD}d $(( 10#${ens_id} ))`

    # generate a complete list for looping
    mem_ids+=( ${mem_id} )
  done
  ens_min=`printf %0${ENS_PAD}d $(( 10#${ens_min} ))`
  ens_max=`printf %0${ENS_PAD}d $(( 10#${ens_max} ))`
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

# neighborhood width for neighborhood ensemble (maximum) probability estimates
if [ -z "${NBRHD_WDTH}" ]; then
  printf "ERROR: neighborhood statistics width \${NBRHD_WDTH} is not defined.\n"
  exit 1
fi

# check for software and script deps.
if [ -z "${MET_VER}" ]; then
  msg="MET version \${MET_VER} is not defined.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -x ${MET} ]; then
  msg="MET singularity image\n ${MET}\n does not exist or is not executable.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -r ${SHARED}/GenEnsProdConfigTemplate ]; then
  msg="GenEnsProdConfig template \n ${SHARED}/GenEnsProdConfigTemplate\n"
  msg+=" does not exist or is not readable.\n"
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

# Define the
if [ -z ${IN_DT_SUBDIR+x} ]; then
  msg="ERROR: input data directory subdirectory \${IN_DT_SUBDIR} is not"
  msg+=" declared, define as an empty string if unused.\n"
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

# prepare the work directory, cleaning old data
cmd="rm -f ${WRK_DIR}/${ENS_PRFX}*"
printf "${cmd}\n"; eval "${cmd}"

fname="*${CTR_FLW}_*"
cmd="rm -f ${WRK_DIR}/${fname}"
printf "${cmd}\n"; eval "${cmd}"

fname="GenEnsProdConfig*"
cmd="rm -f ${WRK_DIR}/${fname}"
printf "${cmd}\n"; eval "${cmd}"

# Define directory privileges for singularity exec
met="singularity exec -B ${WRK_DIR}:/wrk_dir:rw ${MET}"

# loop lead hours for forecast valid time for each initialization time
for (( anl_hr = ${ANL_MIN}; anl_hr <= ${ANL_MAX}; anl_hr += ${ANL_INC} )); do
  # define valid times for accumulation    
  vld_dt=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${anl_hr} hours"`

  vld_Y=${vld_dt:0:4}
  vld_m=${vld_dt:5:2}
  vld_d=${vld_dt:8:2}
  vld_H=${vld_dt:11:2}
  
  # forecast file name based on forecast initialization, accumulation and lead
  pdd_hr=`printf %03d $(( 10#${anl_hr} ))`
  for acc_hr in ${acc_hrs[@]}; do
    if [[ ${CMP_ACC} =~ ${TRUE} && ${acc_hr} -le ${anl_hr} ]] ||\
      [[ ${CMP_ACC} =~ ${FALSE} ]]; then
      # create switch to break loop on if missing files
      error=0

      # define output file name depending on parameters
      f_out="${CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}"
      f_out+="_ens-${ens_min}-${ens_max}_prd.nc"

      # define the ensemble member list name and cleanup existing
      mem_lst="ens_list_${CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}"
      mem_lst+="_ens-${ens_min}-${ens_max}_prd.txt"

      cmd="rm -f ${WRK_DIR}/${mem_lst}"
      printf "${cmd}\n"; eval "${cmd}"

      for mem_id in ${mem_ids[@]}; do
        in_path=${IN_DIR}/${mem_id}/${IN_DT_SUBDIR}
        f_in=${in_path}/${CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}.nc
         if [ -r ${f_in} ]; then
           if [ ${mem_id} != ${ctr_id} ]; then
             # generate list of ensemble members used on the fly
             printf "/wrk_dir/${mem_id} " >> ${WRK_DIR}/${mem_lst}
           fi
           # copy the ensemble file to the work directory
           cmd="cp -L ${f_in} ${WRK_DIR}/${mem_id}"
           printf "${cmd}\n"; eval "${cmd}"
         else
           msg="WARNING: ensemble member\n ${f_in}\n does not exist or is not"
           msg+=" readable.\n"
           printf "${msg}"
           if [[ ${FULL_ENS} =~ ${TRUE} ]]; then
             error=1
           fi
         fi
      done
      if [ ${error} = 1 ]; then
        msg="run_GenEnsProd is exiting with errors due to missing ensemble"
        msg+=" members, see above messages to diagnose or run with"
        msg+=" FULL_ENS=FALSE.\n"
        printf "${msg}"
        break
      else
        # update GenEnsProdConfigTemplate archiving file in working directory
        # this remains unchanged on accumulation intervals
        if [[ ${CMP_ACC} =~ ${TRUE} ]]; then
          fld=${VRF_FLD}_${acc_hr}hr
          printf "Computing verification field ${fld}\n."
        else
          fld=${VRF_FLD}
          printf "Computing verification field ${fld}\n."
        fi
        if [ ! -r ${WRK_DIR}/GenEnsProdConfig${acc_hr} ]; then
          cat ${SHARED}/GenEnsProdConfigTemplate \
            | sed "s/CTR_FLW/model = \"${CTR_FLW}\"/" \
            | sed "s/VRF_FLD/name       = \"${fld}\"/" \
            | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
            | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
            | sed "s/MET_VER/version           = \"V${MET_VER}\"/" \
            > ${WRK_DIR}/GenEnsProdConfig${acc_hr}
        fi

        # Run gen_ens_prod
        cmd="${met} gen_ens_prod -v 10 \
        -ens `cat ${WRK_DIR}/${mem_lst}` \
        -out /wrk_dir/${f_out} \
        -config /wrk_dir/GenEnsProdConfig${acc_hr} \
        ${ctr_mem}"
        printf "${cmd}\n"; eval "${cmd}"
      fi
    fi
    for mem_id in ${mem_ids[@]}; do
      cmd="rm -f ${WRK_DIR}/${mem_id}"
      printf "${cmd}\n"; eval "${cmd}"
    done
  done 
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at WRK_DIR:\n ${WRK_DIR}\n"
printf "${msg}"

#################################################################################
# end

exit 0
