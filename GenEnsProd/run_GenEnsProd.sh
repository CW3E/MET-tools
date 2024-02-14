#################################################################################
# Description
#################################################################################
# The purpose of this script is to compute simple ensemble products using MET
# GenEnsProd Tool after pre-procssing WRF forecast data using WRF-preprocess
# scripts in this repository.
#
#################################################################################
# License Statement
#################################################################################
# Copyright 2023 CW3E, Contact Colin Grudzien cgrudzien@ucsd.edu
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
#
#################################################################################
# READ WORKFLOW PARAMETERS
#################################################################################
# export all configurations supplied as an array of string definitions
printf "Loading configuration parameters:\n"
for cmd in "$@"; do
  printf " ${cmd}\n"; eval "${cmd}"
done

#################################################################################
# CHECK WORKFLOW PARAMETERS
#################################################################################
# define the working scripts directory
if [ ! ${USR_HME} ]; then
  printf "ERROR: MET-tools clone directory \${USR_HME} is not defined.\n"
  exit 1
elif [[ ! -d ${USR_HME} || ! -r ${USR_HME} ]]; then
  msg="ERROR: MET-tools clone directory\n ${USR_HME}\n does not exist or is"
  msg+=" not readable.\n"
  printf "${msg}"
  exit 1
else
  scrpt_dir=${USR_HME}/GenEnsProd
  if [[ ! -d ${scrpt_dir} || ! -r ${scrpt_dir} ]]; then
    msg="ERROR: GenEnsProd script directory\n ${scrpt_dir}\n does not exist or"
    msg+=" is not readable.\n"
    printf "${msg}"
    exit 1
  fi
fi

# control flow to be processed
if [ ! ${CTR_FLW} ]; then
  printf "ERROR: control flow name \${CTR_FLW} is not defined.\n"
  exit 1
fi

if [[ ! ${CYC_DT} =~ ${N_RE} ]]; then
  msg="ERROR: cycle date directory string \${CYC_DT}\n ${CYC_DT}\n is not numeric."
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

# define the interval at which to process forecast outputs (HH)
if [[ ! ${ANL_INC} =~ ${N_RE} ]]; then
  printf "ERROR: hours increment between analyses \${ANL_INC} is not numeric.\n"
  exit 1
elif [ ! $(( (${ANL_MAX} - ${ANL_MIN}) % ${ANL_INC} )) = 0 ]; then
  msg="ERROR: the interval [\${ANL_MIN}, \${ANL_MAX}]\n [${ANL_MIN}, ${ANL_MAX}]\n" 
  msg+=" must be evenly divisible into increments of \${ANL_INC}, ${ANL_INC}.\n"
  printf "${msg}"
  exit 1
else
  printf "Forecast start dates are incremented by ${ANL_INC} hours.\n"
fi

if [[ ${CMP_ACC} =~ ${TRUE} ]]; then
  # define the accumulation intervals for precip
  if [[ ! ${ACC_MIN} =~ ${N_RE} ]]; then
    printf "ERROR: min precip accumulation interval compuation is not numeric.\n"
    exit 1
  elif [ ${ACC_MIN} -le 0 ]; then
    msg="ERROR: min precip accumulation interval ${ACC_MIN} must be greater than"
    msg+=" zero.\n"
    printf "${msg}"
    exit 1
  elif [[ ! ${ACC_MAX} =~ ${N_RE} ]]; then
    printf "ERROR: max precip accumulation interval compuation is not numeric.\n"
    exit 1
  elif [ ${ACC_MAX} -lt ${ACC_MIN} ]; then
    msg="ERROR: max precip accumulation interval ${ACC_MAX} must be greater than"
    msg+=" min precip accumulation interval.\n"
    printf "${msg}"
    exit 1
  elif [[ ! ${ACC_INC} =~ ${N_RE} ]]; then
    msg="ERROR: increment between precip accumulation intervals \${ACC_INC}"
    msg+=" is not numeric.\n"
    printf "${msg}"
    exit 1
  elif [ ! $(( (${ACC_MAX} - ${ACC_MIN}) % ${ACC_INC} )) = 0 ]; then
    msg="ERROR: the interval [\${ACC_MIN}, \${ACC_MAX}]\n [${ACC_MIN}, ${ACC_MAX}]\n" 
    msg+=" must be evenly divisible into increments of \${ACC_INC}, ${ACC_INC}.\n"
    printf "${msg}"
    exit 1
  else
    # define array of accumulation interval computation hours
    acc_hrs=()
    for (( acc_hr=${ACC_MIN}; acc_hr <= ${ACC_MAX}; acc_hr += ${ACC_INC} )); do
      printf "Computing precipitation accumulation for interval ${acc_hr} hours.\n"
      acc_hrs+=( ${acc_hr} )
    done
  fi
elif [[ ${CMP_ACC} =~ ${FALSE} ]]; then
  # load an array with an empty string if no accumulations
  printf "Not computing accumulation statistics.\n"
  acc_hrs=( "" )
else
  msg="ERROR: ${CMP_ACC} must be set 'TRUE' or 'FALSE' (case insensitive)"
  msg+=" to compute accumulation statistics.\n"
  printf "${msg}"
  exit 1
fi

# check for input data root
if [ ! ${IN_DT_ROOT} ]; then
  printf "ERROR: input date root directory \${IN_DT_ROOT} is not defined.\n"
  exit 1
elif [[ ! -d ${IN_DT_ROOT} || ! -r ${IN_DT_ROOT} ]]; then
  msg="ERROR: input data root directory\n ${IN_DT_ROOT}\n"
  msg+=" does not exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

# create output directory if does not exist
if [ ! ${OUT_DT_ROOT} ]; then
  printf "ERROR: output date root directory \${OUT_DT_ROOT} is not defined.\n"
  exit 1
else
  cmd="mkdir -p ${OUT_DT_ROOT}"
  printf "${cmd}\n"; eval "${cmd}"
fi

# check for output data root created successfully
if [[ ! -d ${OUT_DT_ROOT} || ! -w ${OUT_DT_ROOT} ]]; then
  msg="ERROR: output data root directory\n ${OUT_DT_ROOT}\n does not"
  msg+=" exist or is not writable.\n"
  printf "${msg}"
  exit 1
fi

if [ -z ${IN_DT_SUBDIR+x} ]; then
  msg="ERROR: cycle subdirectory for input data \${IN_DT_SUBDIR} is unset,"
  msg+=" set to empty string if not used.\n"
  printf "${msg}"
  exit 1
fi

if [ -z ${OUT_DT_SUBDIR+x} ]; then
  msg="ERROR: cycle subdirectory for input data \${OUT_DT_SUBDIR} is unset,"
  msg+=" set to empty string if not used.\n"
  printf "${msg}"
  exit 1
fi

# ensemble prefix and ens_ids below construct nested paths from ${IN_DT_SUBDIR}
# defined above to loop over and link to work directory
if [ -z ${ENS_PRFX+x} ]; then
  msg="ERROR: ensemble member prefix to index value"
  msg+=" is unset, set to empty string if not used.\n"
  printf "${msg}"
  exit 1
fi

if [[ ! ${ENS_MIN} =~ ${N_RE} ]]; then
  printf "ERROR: min ensemble index \${ENS_MIN} is not numeric.\n"
  exit 1
else
  # ensure base 10 for looping
  ens_min=`printf $(( 10#${ENS_MIN} ))`
fi

if [[ ! ${ENS_MAX} =~ ${N_RE} ]]; then
  printf "ERROR: max ensemble index \${ENS_MAX} is not numeric.\n"
  exit 1
else
  # ensure base 10 for looping
  ens_max=`printf $(( 10#${ENS_MAX} ))`
fi

if [ -z ${CTR_MEM+x} ]; then
  msg="ERROR: control member name \${CTR_MEM} is unset, set to empty"
  msg+=" string if not used.\n"
  printf "${msg}"
  exit 1
elif [[ ${CTR_MEM} = "" ]]; then
  printf "No control member is used for ensemble product computation.\n"
  ctr_id=""
  ctr_mem=""
elif [[ ${CTR_MEM} =~ ${N_RE} ]]; then
  ctr_id="${ENS_PRFX}`printf %0${ENS_PDD}d $(( 10#${CTR_MEM} ))`"
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
  # define array of ensemble member ids, padded ${ENS_PDD} digits
  mem_ids=()
  for (( ens_id=${ens_min}; ens_id <= ${ens_max}; ens_id++ )); do
    mem_id=${ENS_PRFX}`printf %0${ENS_PDD}d $(( 10#${ens_id} ))`

    # generate a complete list for looping
    mem_ids+=( ${mem_id} )
  done
  ens_min=`printf %0${ENS_PDD}d $(( 10#${ens_min} ))`
  ens_max=`printf %0${ENS_PDD}d $(( 10#${ens_max} ))`
fi

# define path from ensemble member indexed directories defined above
if [ -z ${IN_ENS_SUBDIR+x} ]; then
  msg="ERROR: ensemble member subdirectory for input data \${IN_ENS_SUBDIR}"
  msg+=" is unset, set to empty string if not used.\n"
  printf "${msg}"
  exit 1
fi

# define the verification field
if [ ! ${VRF_FLD} ]; then
  printf "ERROR: verification field \${VRF_FLD} is not defined.\n"
  exit 1
fi

if [ ! "${CAT_THR}" ]; then
  printf "ERROR: thresholds \${CAT_THR} is not defined.\n"
  exit 1
fi

# neighborhood width for neighborhood ensemble (maximum) probability estimates
if [ ! ${NBRHD_WDTH} ]; then
  printf "ERROR: neighborhood statistics width \${NBRHD_WDTH} is not defined.\n"
  exit 1
fi

# check for software and script deps.
if [ ! ${MET_VER} ]; then
  msg="MET version \${MET_VER} is not defined.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -x ${MET} ]; then
  msg="MET singularity image\n ${MET}\n does not exist or is not executable.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -r ${scrpt_dir}/GenEnsProdConfigTemplate ]; then
  msg="GenEnsProdConfig template \n ${scrpt_dir}/GenEnsProdConfigTemplate\n"
  msg+=" does not exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# cycle date directory of cf-compliant input files
in_dir=${IN_DT_ROOT}/${CYC_DT}${IN_DT_SUBDIR}

# set and clean working directory based on looped forecast start date
wrk_dir=${OUT_DT_ROOT}/${CYC_DT}${OUT_DT_SUBDIR}
cmd="mkdir -p ${wrk_dir}"
printf "${cmd}\n"; eval "${cmd}"

for mem_id in ${mem_ids[@]}; do
  cmd="rm -f ${wrk_dir}/${mem_id}"
  printf "${cmd}\n"; eval "${cmd}"
done

for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INC} )); do
  for acc_hr in ${acc_hrs[@]}; do
    fname="ens_list_{CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}"
    fname+="_ens-${ens_min}-${ens_max}_prd.nc"
    cmd="rm -f ${wrk_dir}/${fname}"
    printf "${cmd}\n"; eval "${cmd}"

    fname="{CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}"
    fname+="_ens-${ens_min}-${ens_max}_prd.nc"
    cmd="rm -f ${wrk_dir}/${fname}"
    printf "${cmd}\n"; eval "${cmd}"

    fname=GenEnsProdConfig${acc_hr}
    cmd="rm -f ${wrk_dir}/${fname}"
    printf "${cmd}\n"; eval "${cmd}"
  done
done

# Define directory privileges for singularity exec
met="singularity exec -B ${wrk_dir}:/wrk_dir:rw ${MET}"

# loop lead hours for forecast valid time for each initialization time
for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INC} )); do
  # define valid times for accumulation    
  vld_dt=`date +%Y-%m-%d_%H_%M_%S -d "${cyc_dt} ${lead_hr} hours"`

  vld_Y=${vld_dt:0:4}
  vld_m=${vld_dt:5:2}
  vld_d=${vld_dt:8:2}
  vld_H=${vld_dt:11:2}
  
  # forecast file name based on forecast initialization, accumulation and lead
  pdd_hr=`printf %03d $(( 10#${lead_hr} ))`
  for acc_hr in ${acc_hrs[@]}; do
    if [[ ${CMP_ACC} =~ ${TRUE} && ${acc_hr} -le ${lead_hr} ]] ||\
      [[ ${CMP_ACC} =~ ${FALSE} ]]; then
      # create switch to break loop on if missing files
      error=0

      # define output file name depending on parameters
      f_out="${CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}"
      f_out+="_ens-${ens_min}-${ens_max}_prd.nc"

      # define the ensemble member list name and cleanup existing
      mem_lst="ens_list_${CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}"
      mem_lst+="_ens-${ens_min}-${ens_max}_prd.txt"

      cmd="rm -f ${wrk_dir}/${mem_lst}"
      printf "${cmd}\n"; eval "${cmd}"

      for mem_id in ${mem_ids[@]}; do
        in_path=${in_dir}/${mem_id}${IN_ENS_SUBDIR}
        f_in=${in_path}/${CTR_FLW}_${acc_hr}${VRF_FLD}_${CYC_DT}_F${pdd_hr}.nc
         if [ -r ${f_in} ]; then
           if [ ${mem_id} != ${ctr_id} ]; then
             # generate list of ensemble members used on the fly
             printf "/wrk_dir/${mem_id} " >> ${wrk_dir}/${mem_lst}
           fi
           # copy the ensemble file to the work directory
           cmd="cp -L ${f_in} ${wrk_dir}/${mem_id}"
           printf "${cmd}\n"; eval "${cmd}"
         else
           msg="WARNING: ensemble member\n ${f_in}\n does not exist or is not"
           msg+=" readable.\n"
           printf "${msg}"
           if [[ ${FULL_ENS} =~ ${TRUE} ]]; then
             cmd="rm -f ${mem_lst}"
             printf "${cmd}\n"; eval "${cmd}"
             error=1
             break
           fi
         fi
      done
      if [ ${error} = 1 ]; then
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
        if [ ! -r ${wrk_dir}/GenEnsProdConfig ]; then
          cat ${scrpt_dir}/GenEnsProdConfigTemplate \
            | sed "s/CTR_FLW/model = \"${CTR_FLW}\"/" \
            | sed "s/VRF_FLD/name       = \"${fld}\"/" \
            | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
            | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
            | sed "s/MET_VER/version           = \"V${MET_VER}\"/" \
            > ${wrk_dir}/GenEnsProdConfig${acc_hr}
        fi

        # Run gen_ens_prod
        cmd="${met} gen_ens_prod -v 10 \
        -ens `cat ${wrk_dir}/${mem_lst}` \
        -out /wrk_dir/${f_out} \
        -config /wrk_dir/GenEnsProdConfig${acc_hr} \
        ${ctr_mem}"
        printf "${cmd}\n"; eval "${cmd}"
      fi
    fi
    for mem_id in ${mem_ids[@]}; do
      cmd="rm -f ${wrk_dir}/${mem_id}"
      printf "${cmd}\n"; eval "${cmd}"
    done
  done 
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at OUT_DT_ROOT:\n ${OUT_DT_ROOT}\n"
printf "${msg}"

#################################################################################
# end

exit 0
