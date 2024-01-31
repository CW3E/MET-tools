#################################################################################
# Description
#################################################################################
# The purpose of this script is to compute grid statistics using MET
# after pre-procssing WRF forecast data and StageIV precip data for
# validating the forecast peformance. This script is based on original
# source code provided by Rachel Weihs, Caroline Papadopoulos and Daniel
# Steinhoff. This is re-written to homogenize project structure and to include
# error handling, process logs and additional flexibility with batch processing 
# ranges of data from multiple models and / or workflows.
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
  scrpt_dir=${USR_HME}/GridStat
  if [[ ! -d ${scrpt_dir} || ! -r ${scrpt_dir} ]]; then
    msg="ERROR: GridStat script directory\n ${scrpt_dir}\n does not exist or is"
    msg+=" not readable.\n"
    printf "${msg}"
    exit 1
  fi
fi

# control flow to be processed
if [ ! ${CTR_FLW} ]; then
  printf "ERROR: control flow name \${CTR_FLW} is not defined.\n"
  exit 1
fi

# if GenEnsProd output for ensemble mean verification
if [[ ${IF_ENS_PRD} =~ ${TRUE} ]]; then
  if [[ ! ${ENS_MIN} =~ ${N_RE} ]]; then
    printf "ERROR: min ensemble index \${ENS_MIN} is not numeric.\n"
    exit 1
  elif [[ ! ${ENS_MAX} =~ ${N_RE} ]]; then
    printf "ERROR: max ensemble index \${ENS_MAX} is not numeric.\n"
    exit 1
  else
    pstfx="_ens-${ENS_MIN}-${ENS_MAX}_prd"
    msg="Computing gridstat on ${CTR_FLW} ensemble product from members"
    msg+=" ${ENS_MIN} to ${ENS_MAX}.\n"
    printf ${msg}
  fi
elif [[ ${IF_ENS_PRD} =~ ${FALSE} ]]; then
  pstfx=""
  printf "Computing gridstat on non-ensemble product.\n"
else
  msg="ERROR: \${IF_ENS_PRD} must be TRUE or FALSE (case insensitive)"
  msg+=" if verifying GenEnsProd output.\n"
  printf "${msg}"
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
if [[ ! ${ANL_INC} =~ ${N_RE} ]]; then
  printf "ERROR: hours interval between analyses \${ANL_INC} is not numeric.\n"
  exit 1
elif [ ! $(( (${ANL_MAX} - ${ANL_MIN}) % ${ANL_INC} )) = 0 ]; then
  msg="ERROR: the interval [\${ANL_MIN}, \${ANL_MAX}]\n [${ANL_MIN}, ${ANL_MAX}]\n" 
  msg+=" must be evenly divisible into increments of \${ANL_INC}, ${ANL_INC}.\n"
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
  elif [[ ! ${ACC_INC} =~ ${N_RE} ]]; then
    msg="ERROR: inteval between precip accumulation computations \${ACC_INC}"
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
      # check that the precip accumulations are summable from wrfcf files
      if [ ! $(( ${acc_hr} % ${ANL_INC} )) = 0 ]; then
        printf "ERROR: precip accumulation ${acc_hr} is not a multiple of ${ANL_INC}.\n"
        exit 1
      else
        printf "Computing precipitation accumulation for interval ${acc_hr} hours.\n"
        acc_hrs+=( ${acc_hr} )
      fi
    done
  fi
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
  msg="ERROR: output date root directory \${OUT_DT_ROOT}"
  msg+=" is not defined.\n"
  printf "${msg}"
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
  msg="ERROR: subdirectory for input data \${IN_DT_SUBDIR} is unset,"
  msg+=" set to empty string if not used.\n"
  printf "${msg}"
  exit 1
fi

if [ -z ${OUT_DT_SUBDIR+x} ]; then
  msg="ERROR: subdirectory for output data \${OUT_DT_SUBDIR} is unset,"
  msg+=" set to empty string if not used.\n"
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

# List of landmasks for verification region, file name with extension
if [ ! ${MSK_LST} ]; then
  printf "ERROR: landmask list file \${MSK_LST} is not defined.\n"
  exit 1
elif [ ! -r ${MSK_LST} ]; then
  printf "ERROR: landmask list file ${MSK_LST} does not exist or is not readable.\n"
  exit 1
fi

# Root directory for landmasks
if [ ! ${MSK_GRDS} ]; then
  printf "ERROR: landmask directory \${MSK_GRDS} is not defined.\n"
  exit 1
elif [[ ! -d ${MSK_GRDS} || ! -r ${MSK_GRDS} ]]; then
  printf "ERROR: landmask directory ${MSK_GRDS} does not exist or is not readable.\n"
  exit 1
fi

# loop lines of the mask list, set temporary exit status before searching for masks
error=0
while read msk; do
  fpath=${MSK_GRDS}/${msk}_StageIVGrid.nc
  if [ -r "${fpath}" ]; then
    printf "Found\n ${fpath}\n landmask.\n"
  else
    msg="ERROR: verification region landmask\n ${fpath}\n"
    msg+=" does not exist or is not readable.\n"
    printf "${msg}"

    # create exit status flag to kill program, after checking all files in list
    error=1
  fi
done < "${MSK_LST}"

if [ ${error} -eq 1 ]; then
  msg="ERROR: Exiting due to missing landmasks, please see the above error "
  msg+="messages and verify the location for these files. These files can be "
  msg+="generated from lat-lon text files using the run_vxmask.sh script."
  printf "${msg}"
  exit 1
fi

# define the interpolation neighborhood size
if [ ! ${INT_WDTH} ]; then 
  printf "ERROR: interpolation neighborhood width \${INT_WDTH} is not defined.\n"
  exit 1
fi

# neighborhood width for neighborhood methods
if [ ! ${NBRHD_WDTH} ]; then
  printf "ERROR: neighborhood statistics width \${NBRHD_WDTH} is not defined.\n"
  exit 1
fi

# number of bootstrap resamplings, set equal to 0 to turn off
if [[ ! ${BTSTRP} =~ ${N_RE} || ${BTSTRP} -lt 0 ]]; then
  msg="ERROR: bootstrap resampling number \${BTSRP} is not defined,"
  msg+=" set \${BTSTRP} to a positive integer or to 0 to turn off.\n"
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

# check for software and data deps.
if [ ! ${STC_ROOT} ]; then
  printf "ERROR: \${STC_ROOT} is not defined.\n"   
  exit 1
elif [[ ! -d ${STC_ROOT} || ! -r ${STC_ROOT} ]]; then
  msg="ERROR: static verification data directory\n ${STC_ROOT}\n"
  msg+=" does not exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

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

if [ ! -r ${scrpt_dir}/GridStatConfigTemplate ]; then
  msg="GridStatConfig template \n ${scrpt_dir}/GridStatConfigTemplate\n"
  msg+=" does not exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# define the number of dates to loop
fcst_hrs=$(( (`date +%s -d "${stop_dt}"` - `date +%s -d "${strt_dt}"`) / 3600 ))

for (( cyc_hr = 0; cyc_hr <= ${fcst_hrs}; cyc_hr += ${CYC_INC} )); do
  # directory string for forecast analysis initialization time
  cyc_dt=`date +%Y%m%d%H -d "${strt_dt} ${cyc_hr} hours"`

  # cycle date directory of cf-compliant input files
  in_dir=${IN_DT_ROOT}/${cyc_dt}${IN_DT_SUBDIR}

  # set and clean working directory based on looped forecast start date
  wrk_dir=${OUT_DT_ROOT}/${cyc_dt}${OUT_DT_SUBDIR}
  cmd="mkdir -p ${wrk_dir}"
  printf "${cmd}\n"; eval "${cmd}"

  # check for work directory created successfully
  if [[ ! -d ${wrk_dir} || ! -w ${wrk_dir} ]]; then
    msg="ERROR: work directory\n ${wrk_dir}\n does not"
    msg+=" exist or is not writable.\n"
    printf "${msg}"
    exit 1
  fi

  rm -f ${wrk_dir}/grid_stat_*.txt
  rm -f ${wrk_dir}/grid_stat_*.stat
  rm -f ${wrk_dir}/grid_stat_*.nc
  rm -f ${wrk_dir}/GridStatConfig*
  rm -f ${wrk_dir}/PLY_MSK.txt

  # loop lines of the mask list, generate PLY_MSK.txt for GridStatConfig insert
  msk_count=`wc -l < ${MSK_LST}`
  line_count=1
  while read msk; do
    if [ ${line_count} -lt ${msk_count} ]; then
      ply_msk="\"/MSK_GRDS/${msk}_StageIVGrid.nc\",\n"
      printf ${ply_msk} >> ${wrk_dir}/PLY_MSK.txt
    else
      ply_msk="\"/MSK_GRDS/${msk}_StageIVGrid.nc\""
      printf ${ply_msk} >> ${wrk_dir}/PLY_MSK.txt
    fi
    line_count=$(( ${line_count} + 1 ))
  done <${MSK_LST}

  # Define directory privileges for singularity exec
  met="singularity exec -B ${wrk_dir}:/wrk_dir:rw,"
  met+="${STC_ROOT}:/STC_ROOT:ro,${MSK_GRDS}:/MSK_GRDS:ro,"
  met+="${in_dir}:/in_dir:ro ${MET}"

  # loop lead hours for forecast valid time for each initialization time
  for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INC} )); do
    # define valid times for verification
    anl_stop_hr=$(( ${lead_hr} + ${cyc_hr} ))
    anl_stop=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_stop_hr} hours"`

    vld_Y=${anl_stop:0:4}
    vld_m=${anl_stop:5:2}
    vld_d=${anl_stop:8:2}
    vld_H=${anl_stop:11:2}
    
    pdd_hr=`printf %03d $(( 10#${lead_hr} ))`

    for acc_hr in ${acc_hrs[@]}; do
      if [[ ${CMP_ACC} =~ ${TRUE} && ${acc_hr} -le ${lead_hr} ]]; then
        for_in=${CTR_FLW}_${acc_hr}${VRF_FLD}_${cyc_dt}_F${pdd_hr}${pstfx}.nc
        if [[ ${IF_ENS_PRD} =~ ${TRUE} ]]; then
          fld=${VRF_FLD}_${acc_hr}hr_0_all_all_ENS_MEAN
        else
          fld=${VRF_FLD}_${acc_hr}hr
        fi

        # obs file defined in terms of valid time, path relative to STC_ROOT
        obs_in=StageIV/StageIV_QPE_${vld_Y}${vld_m}${vld_d}${vld_H}.nc

        if [ -r ${in_dir}/${for_in} ]; then
          if [ -r ${STC_ROOT}/${obs_in} ]; then
            # update GridStatConfigTemplate archiving file in working directory
            # this remains unchanged on inner loop
            if [ ! -r ${wrk_dir}/GridStatConfig${acc_hr} ]; then
              cat ${scrpt_dir}/GridStatConfigTemplate \
                | sed "s/CTR_FLW/model = \"${CTR_FLW}\"/" \
                | sed "s/INT_WDTH/width = ${INT_WDTH}/" \
                | sed "s/RNK_CRR/rank_corr_flag      = ${RNK_CRR}/" \
                | sed "s/VRF_FLD/name       = \"${fld}\"/" \
                | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
                | sed "/PLY_MSK/r ${wrk_dir}/PLY_MSK.txt" \
                | sed "/PLY_MSK/d " \
                | sed "s/BTSTRP/n_rep    = ${BTSTRP}/" \
                | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
                | sed "s/PRFX/output_prefix    = \"${VRF_FLD}_${acc_hr}hr\"/" \
                | sed "s/MET_VER/version           = \"V${MET_VER}\"/" \
                > ${wrk_dir}/GridStatConfig${acc_hr}
            fi

            # Run gridstat
            cmd="${met} grid_stat -v 10 \
            /in_dir/${for_in} \
            /STC_ROOT/${obs_in} \
            /wrk_dir/GridStatConfig${acc_hr} \
            -outdir /wrk_dir"
            printf "${cmd}\n"; eval "${cmd}"
            
          else
            msg="Observation verification file\n ${STC_ROOT}/${obs_in}\n is not "
            msg+=" readable or does not exist, skipping grid_stat for forecast "
            msg+="initialization ${cyc_dt}, forecast hour ${lead_hr}.\n"
            printf "${msg}"
          fi

        else
          msg="gridstat input file\n ${in_dir}/${for_in}\n is not readable " 
          msg+=" or does not exist, skipping grid_stat for forecast initialization "
          msg+="${cyc_dt}, forecast hour ${lead_hr}.\n"
          printf "${msg}"
        fi

        # clean up working directory from accumulation time
        cmd="rm -f ${wrk_dir}/${for_in}"
        printf "${cmd}\n"; eval "${cmd}"
      elif [[ ${CMP_ACC} =~ ${FALSE} ]]; then
        for_in=${CTR_FLW}_${VRF_FLD}_${cyc_dt}_F${pdd_hr}${pstfx}.nc

        if [[ ${IF_ENS_PRD} =~ ${TRUE} ]]; then
          fld=${VRF_FLD}_0_all_all_ENS_MEAN
        else
          fld=${VRF_FLD}
        fi

        # obs file defined in terms of valid time
        # NOTE: reference fields other than StageIV still in development
        obs_in=${VRF_REF}_${VRF_FLD}_${cyc_dt}_F${pdd_hr}${pstfx}.nc
        
        if [ -r ${in_dir}/${for_in} ]; then
          if [ -r ${STC_ROOT}/${obs_in} ]; then
            # update GridStatConfigTemplate archiving file in working directory
            # this remains unchanged on inner loop
            if [ ! -r ${wrk_dir}/GridStatConfig${acc_hr} ]; then
              cat ${scrpt_dir}/GridStatConfigTemplate \
                | sed "s/CTR_FLW/model = \"${CTR_FLW}\"/" \
                | sed "s/INT_WDTH/width = ${INT_WDTH}/" \
                | sed "s/RNK_CRR/rank_corr_flag      = ${RNK_CRR}/" \
                | sed "s/VRF_FLD/name       = \"${fld}\"/" \
                | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
                | sed "/PLY_MSK/r ${wrk_dir}/PLY_MSK.txt" \
                | sed "/PLY_MSK/d " \
                | sed "s/BTSTRP/n_rep    = ${BTSTRP}/" \
                | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
                | sed "s/PRFX/output_prefix    = \"${VRF_FLD}\"/" \
                | sed "s/MET_VER/version           = \"V${MET_VER}\"/" \
                > ${wrk_dir}/GridStatConfig${acc_hr}
            fi

            # Run gridstat
            cmd="${met} grid_stat -v 10 \
            /in_dir/${for_in} \
            /STC_ROOT/${obs_in} \
            /wrk_dir/GridStatConfig${acc_hr} \
            -outdir /wrk_dir"
            printf "${cmd}\n"; eval "${cmd}"
            
          else
            msg="Observation verification file\n ${STC_ROOT}/${obs_in}\n is not "
            msg+=" readable or does not exist, skipping grid_stat for forecast "
            msg+="initialization ${cyc_dt}, forecast hour ${lead_hr}.\n"
            printf "${msg}"
          fi

        else
          msg="gridstat input file\n ${in_dir}/${for_in}\n is not readable " 
          msg+=" or does not exist, skipping grid_stat for forecast initialization "
          msg+="${cyc_dt}, forecast hour ${lead_hr}.\n"
          printf "${msg}"
        fi

        # clean up working directory from accumulation time
        cmd="rm -f ${wrk_dir}/${for_in}"
        printf "${cmd}\n"; eval "${cmd}"

      fi
    done
  done

  # clean up working directory from forecast start time
  cmd="rm -f ${wrk_dir}/*_StageIVGrid.nc"
  printf "${cmd}\n"; eval "${cmd}"

  cmd="rm -f ${wrk_dir}/PLY_MSK.txt"
  printf "${cmd}\n"; eval "${cmd}"
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at OUT_DT_ROOT:\n ${OUT_DT_ROOT}\n"
printf "${msg}"

#################################################################################
# end

exit 0
