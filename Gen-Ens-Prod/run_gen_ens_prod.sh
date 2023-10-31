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
# make checks for workflow parameters

# define the working scripts directory
if [ ! ${USR_HME} ]; then
  printf "ERROR: MET-tools clone directory \${USR_HME} is not defined.\n"
  exit 1
elif [ ! -d ${USR_HME} ]; then
  printf "ERROR: MET-tools clone directory\n ${USR_HME}\n does not exist.\n"
  exit 1
else
  scrpt_dir=${USR_HME}/GenEnsProd
  if [ ! -d ${scrpt_dir} ]; then
    printf "ERROR: GenEnsProd script directory\n ${scrpt_dir}\n does not exist.\n"
    exit 1
  fi
fi

# control flow to be processed
if [ ! ${CTR_FLW} ]; then
  printf "ERROR: control flow name \${CTR_FLW} is not defined.\n"
  exit 1
fi

# verification domain for the forecast data
if [ -z ${GRD+x} ]; then
  msg="ERROR: grid name \${GRD} is not defined, set to an empty string"
  msg+="if not needed.\n"
  printf "${msg}"
  exit 1
fi

# Convert STRT_DT from 'YYYYMMDDHH' format to strt_dt Unix date format
if [ ${#STRT_DT} -ne 10 ]; then
  printf "ERROR: \${STRT_DT} is not in YYYYMMDDHH format.\n"
  exit 1
else
  strt_dt="${STRT_DT:0:8} ${STRT_DT:8:2}"
  strt_dt=`date -d "${strt_dt}"`
fi

# Convert STOP_DT from 'YYYYMMDDHH' format to stop_dt Unix date format 
if [ ${#STOP_DT} -ne 10 ]; then
  printf "ERROR: \${STOP_DT} is not in YYYYMMDDHH format.\n"
  exit 1
else
  stop_dt="${STOP_DT:0:8} ${STOP_DT:8:2}"
  stop_dt=`date -d "${stop_dt}"`
fi

# define min / max forecast hours for forecast outputs to be processed
if [ ! ${ANL_MIN} ]; then
  printf "ERROR: min forecast hour \${ANL_MIN} is not defined.\n"
  exit 1
fi

if [ ! ${ANL_MAX} ]; then
  printf "ERROR: max forecast hour \${ANL_MAX} is not defined.\n"
  exit 1
fi

# define the interval at which to process forecast outputs (HH)
if [ ! ${ANL_INT} ]; then
  printf "ERROR: hours interval between analyses \${HH} is not defined.\n"
  exit 1
fi

if [ ! ${ACC_MIN} ]; then
		printf "ERROR: min precip accumulation interval compuation is not defined\n"
		exit 1
elif [ ${ACC_MIN} -le 0 ]; then
  msg="ERROR: min precip accumulation interval ${ACC_MIN} must be greater than"
		msg+=" zero.\n"
		printf ${msg}
  exit 1
elif [ ! ${ACC_MAX} ]; then
		printf "ERROR: max precip accumulation interval compuation is not defined\n"
		exit 1
elif [ ${ACC_MAX} -lt ${ACC_MIN} ]; then
  msg="ERROR: max precip accumulation interval ${ACC_MAX} must be greater than"
		msg+=" min precip accumulation interval.\n"
		printf ${msg}
  exit 1
elif [ ! ${ACC_INT} ]; then
  msg="ERROR: inteval between precip accumulation computations \${ACC_INT}"
		msg+=" is not defined.\n"
		printf ${msg}
  exit 1
else
		# define array of accumulation interval computation hours
		acc_hrs=()
		for (( acc_hr=${ACC_MIN}; acc_hr <= ${ACC_MAX}; acc_hr += ${ACC_INT} )); do
    acc_hrs+=( ${acc_hr} )
		done
fi

# check for input data root
if [ ! -d ${IN_CYC_DIR} ]; then
  printf "ERROR: input data root directory\n ${IN_CYC_DIR}\n does not exist.\n"
  exit 1
fi

# create output directory if does not exist
if [ ! ${OUT_CYC_DIR} ]; then
  msg="ERROR: cycle gridstat output root directory\n ${OUT_CYC_DIR}\n "
  msg+="is not defined."
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
  printf "ERROR: cycle subdirectory for input data \${IN_DT_SUBDIR} is unset,"
  printf " set to empty string if not used.\n"
  exit 1
fi

if [ -z ${OUT_DT_SUBDIR+x} ]; then
  printf "ERROR: cycle subdirectory for input data \${OUT_DT_SUBDIR} is unset,"
  printf " set to empty string if not used.\n"
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

# List of landmasks for verification region, file name with extension
if [ ! -r ${MSK_LST} ]; then
  printf "ERROR: landmask list file \${MSK_LST} does not exist or is not readable.\n"
  exit 1
fi

# Root directory for landmasks
if [ ! ${MSK_GRDS} ]; then
  printf "ERROR: landmask directory \${MSK_GRDS} is not defined.\n"
  exit 1
fi

# neighborhood width for neighborhood methods
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

if [ ! -r ${scrpt_dir}/GenEnsConfigTemplate ]; then
  msg="GenEnsConfig template \n ${scrpt_dir}/GenEnsConfigTemplate\n"
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
  met+="${in_dir}:/in_dir:ro,${scrpt_dir}:/scrpt_dir:ro "
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
    
    # forecast file name based on forecast initialization and lead
    pdd_hr=`printf %03d $(( 10#${lead_hr} ))`
    for_in=${CTR_FLW}_${acc_hr}${VRF_FLD}_${dirstr}_F${pdd_hr}.nc

    # copy the preprocessed data to the working directory from the data root
    in_path="${in_dir}/${for_in}"
    # update GenEnsProdConfigTemplate archiving file in working directory
    # this remains unchanged on inner loop
    if [ ! -r ${wrk_dir}/GenEnsProdConfig ]; then
      cat ${scrpt_dir}/GenEnsProdConfigTemplate \
        | sed "s/VRF_FLD/name       = \"${VRF_FLD}_${ACC_INT}hr\"/" \
        | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
        | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
        | sed "s/MET_VER/version           = \"V${MET_VER}\"/" \
        > ${wrk_dir}/GenEnsProdConfig
    fi

    # Run gen_ens_prod
    cmd="${met} gen_ens_prod -v 10 \
    -ens /wrk_dir/ens_list.txt \
    -out /wrk_dir/ens_prd.nc \
    -config /wrk_dir/GenEnsProdConfig"
    printf "${cmd}\n"; eval "${cmd}"
    
  done
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at OUT_CYC_DIR:\n ${OUT_CYC_DIR}\n"
printf "${msg}"

#################################################################################
# end

exit 0
