#################################################################################
# Description
#################################################################################
# The purpose of this script is to compute simple ensemble products using MET
# Gen-Ens-Prod Tool after pre-procssing WRF forecast data using WRF-preprocess
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
  scrpt_dir=${USR_HME}/Gen-Ens-Prod
  if [[ ! -d ${scrpt_dir} || ! -r ${scrpt_dir} ]]; then
    msg="ERROR: Gen-Ens-Prod script directory\n ${scrpt_dir}\n does not exist or"
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

# Convert STRT_DT from 'YYYYMMDDHH' format to strt_dt Unix date format
if [[ ! ${STRT_DT} =~ ${ISO_RE} ]]; then
  msg="ERROR: start date \${STRT_DT}\n ${STRT_DT}\n"
		msg+=" is not in YYYYMMDDHH format.\n"
		printf "${msg}"
  exit 1
else
  strt_dt="${STRT_DT:0:8} ${STRT_DT:8:2}"
  strt_dt=`date -d "${strt_dt}"`
fi

# Convert STOP_DT from 'YYYYMMDDHH' format to stop_dt Unix date format 
if [[ ! ${STOP_DT} =~ ${ISO_RE} ]]; then
  msg="ERROR: stop date \${STOP_DT}\n ${STOP_DT}\n"
		msg+=" is not in YYYYMMDDHH format.\n"
		printf "${msg}"
  exit 1
else
  stop_dt="${STOP_DT:0:8} ${STOP_DT:8:2}"
  stop_dt=`date -d "${stop_dt}"`
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
if [[ ! ${ANL_INT} =~ ${N_RE} ]]; then
  printf "ERROR: hours interval between analyses \${ANL_INT} is not numeric.\n"
  exit 1
elif [ ! $(( (${ANL_MAX} - ${ANL_MIN}) % ${ANL_INT} )) = 0 ]; then
  msg="ERROR: the interval [\${ANL_MIN}, \${ANL_MAX}]\n [${ANL_MIN}, ${ANL_MAX}]\n" 
  msg+=" must be evenly divisible into increments of \${ANL_INT}, ${ANL_INT}.\n"
  printf "${msg}"
  exit 1
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
  elif [[ ! ${ACC_INT} =~ ${N_RE} ]]; then
    msg="ERROR: inteval between precip accumulation computations \${ACC_INT}"
  		msg+=" is not numeric.\n"
  		printf "${msg}"
    exit 1
  elif [ ! $(( (${ACC_MAX} - ${ACC_MIN}) % ${ACC_INT} )) = 0 ]; then
    msg="ERROR: the interval [\${ACC_MIN}, \${ACC_MAX}]\n [${ACC_MIN}, ${ACC_MAX}]\n" 
    msg+=" must be evenly divisible into increments of \${ACC_INT}, ${ACC_INT}.\n"
    printf "${msg}"
    exit 1
  else
  		# define array of accumulation interval computation hours
  		acc_hrs=()
  		for (( acc_hr=${ACC_MIN}; acc_hr <= ${ACC_MAX}; acc_hr += ${ACC_INT} )); do
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
		exit 1
fi

# check for input data root
if [ ! ${IN_CYC_DIR} ]; then
		msg="ERROR: directory of ISO date sub-directories \${IN_CYC_DIR} is"
		msg+=" not defined.\n"
		printf "${msg}"
		exit 1
elif [[ ! -d ${IN_CYC_DIR} || ! -r ${IN_CYC_DIR} ]]; then
  msg="ERROR: input data root directory\n ${IN_CYC_DIR}\n"
		msg+=" does not exist or is not readable.\n"
  exit 1
fi

# create output directory if does not exist
if [ ! ${OUT_CYC_DIR} ]; then
  msg="ERROR: cycle gridstat output root directory \${OUT_CYC_DIR} "
  msg+="is not defined.\n"
		printf "${msg}"
  exit 1
else
  cmd="mkdir -p ${OUT_CYC_DIR}"
  printf "${cmd}\n"; eval "${cmd}"
fi

# check for output data root created successfully
if [ ! -d ${OUT_CYC_DIR} ]; then
  printf "ERROR: output data root directory\n ${OUT_CYC_DIR}\n does not exist.\n"
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

# ensemble prefix and mem_ids below construct nested paths from ${IN_DT_SUBDIR}
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

if [ ${ens_min} -lt 0 ]; then
		printf "ERROR: min ensemble index ${ENS_MIN} must be non-negative.\n"
		exit 1
elif [ ${ens_max} -lt ${ens_min} ]; then
		msg="ERROR: max ensemble index ${ENS_MAX} must be greater than or equal"
		msg+=" to the minimum ensemble index."
		exit 1
else 
  # define array of ensemble member ids, padded three digits
  mem_ids=()
  for (( mem_id=${ens_min}; mem_id <= ${ens_max}; mem_id++ )); do
				mem_ids+=( ${ENS_PRFX}`printf %03d $(( 10#${mem_id} ))` )
  done
		ens_min=`printf %03d $(( 10#${ens_min} ))`
		ens_max=`printf %03d $(( 10#${ens_max} ))`
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

if [ -z ${CTR_MEM+x} ]; then
  msg="ERROR: control member name \${CTR_MEM} is unset, set to empty"
		msg+=" string if not used.\n"
  printf "${msg}"
  exit 1
elif [[ ${CTR_MEM} = "" ]]; then
		${ctr_mem}=""
elif [[ ${CTR_MEM} =~ ${N_RE} ]]; then
		ctr_mem="-ctrl ${ENS_PRFX}`printf %03d $(( 10#${CTR_MEM} ))`"
else 
		msg="ERROR: \${CTR_MEM}\n ${CTR_MEM}\n should be set to a numerical index"
		msg+=" or to an emptry string \"\" if unused.\n"
		printf "${msg}"
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
# define the number of dates to loop
fcst_hrs=$(( (`date +%s -d "${stop_dt}"` - `date +%s -d "${strt_dt}"`) / 3600 ))

for (( cyc_hr = 0; cyc_hr <= ${fcst_hrs}; cyc_hr += ${CYC_INT} )); do
  # directory string for forecast analysis initialization time
  dirstr=`date +%Y%m%d%H -d "${strt_dt} ${cyc_hr} hours"`

  # cycle date directory of cf-compliant input files
  in_dir=${IN_CYC_DIR}/${dirstr}${IN_DT_SUBDIR}

  # set and clean working directory based on looped forecast start date
  wrk_dir=${OUT_CYC_DIR}/${dirstr}${OUT_DT_SUBDIR}
  mkdir -p ${wrk_dir}

  # Define directory privileges for singularity exec
  met="singularity exec -B ${wrk_dir}:/wrk_dir:rw,"
  met+="${scrpt_dir}:/scrpt_dir:ro "
  met+="${MET}"
  printf "${cmd}\n"; eval "${cmd}"

  # loop lead hours for forecast valid time for each initialization time
  for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INT} )); do
    # define valid times for accumulation    
    anl_strt_hr=$(( ${lead_hr} + ${cyc_hr} - ${ACC_INT} ))
    anl_stop_hr=$(( ${lead_hr} + ${cyc_hr} ))
    anl_strt=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_strt_hr} hours"`
    anl_stop=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_stop_hr} hours"`

    vld_Y=${anl_stop:0:4}
    vld_m=${anl_stop:5:2}
    vld_d=${anl_stop:8:2}
    vld_H=${anl_stop:11:2}
    
    # forecast file name based on forecast initialization, accumulation and lead
    pdd_hr=`printf %03d $(( 10#${lead_hr} ))`
				for acc_hr in ${acc_hrs[@]}; do
						if [[ ${CMP_ACC} =~ ${TRUE} && ${acc_hr} -ge ${lead_hr} ]] || [[ ${CMP_ACC} =~ ${FALSE} ]]; then
						  for mem_id in ${mem_ids[@]}; do
						  		in_path=${in_dir}/${mem_id}${IN_ENS_SUBDIR}
          f_in=${in_path}/${CTR_FLW}_${acc_hr}${VRF_FLD}_${dirstr}_F${pdd_hr}.nc
										if [ -r ${f_in} ]; then
												# keep a record of the original members used for computation
												printf "${f_in}\n" >> ${wrk_dir}/${CTR_FLW}_${acc_hr}${VRF_FLD}_${dirstr}_F${pdd_hr}_ens_mems.txt

												# generate an ensemble index list on the fly
												printf "/wrk_dir/${mem_id}\n" >> ${wrk_dir}/ens_list.txt

												# link the file to the work directory
            cmd="ln -sf ${f_in} ${wrk_dir}/${mem_id}"
												printf "${cmd}\n"; eval "${cmd}"
										else
												printf "ERROR: ensemble member ${f_in} does not exist or is not readable.\n"
												exit 1
										fi
						  done
								# define output file name depending on parameters
						  f_out=${CTR_FLW}_${acc_hr}${VRF_FLD}_${dirstr}_F${pdd_hr}_ens-${ens_min}-${ens_max}_prd.nc

        # update GenEnsProdConfigTemplate archiving file in working directory
        # this remains unchanged on accumulation intervals
								if [[ ${CMP_ACC} =~ ${TRUE} ]]; then
										fld=${VRF_FLD}_${acc_hr}hr
								else
										fld=${VRF_FLD}
								fi
        if [ ! -r ${wrk_dir}/GenEnsProdConfig ]; then
          cat ${scrpt_dir}/GenEnsProdConfigTemplate \
            | sed "s/VRF_FLD/name       = \"${fld}\"/" \
            | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
            | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
            | sed "s/MET_VER/version           = \"V${MET_VER}\"/" \
            > ${wrk_dir}/GenEnsProdConfig${acc_hr}
        fi

        # Run gen_ens_prod
        cmd="${met} gen_ens_prod -v 10 \
        -ens /wrk_dir/ens_list.txt \
        -out /wrk_dir/${f_out} \
        -config /wrk_dir/GenEnsProdConfig${acc_hr} \
				    ${ctr_mem}"
        printf "${cmd}\n"; eval "${cmd}"
						fi
    done 
  done
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at OUT_CYC_DIR:\n ${OUT_CYC_DIR}\n"
printf "${msg}"

#################################################################################
# end

exit 0
