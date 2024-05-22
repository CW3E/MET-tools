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
# Check for required fields
#################################################################################i
#these variables are hard coded for testing purposes. 
#eventually these variables will be automatically constructed just like field_in_dir and f_in
in_msh_dir=/glade/derecho/scratch/nghido/sio-cw3e/GenerateGFSAnalyses/ExternalAnalyses/60km/2023021900/
m_in=x1.163842.init.2023-02-19_00.00.00.nc

# export all configurations supplied as an array of string definitions
printf "Loading configuration parameters:\n"
for cmd in "$@"; do
  printf " ${cmd}\n"; eval "${cmd}"
done

#################################################################################
# CHECK WORKFLOW PARAMETERS
#################################################################################
# set input mesh file name
# the idea is to have a flag variable that is defaulted to true
# if IN_MSH_DIR is correctly supplied, then the flag is changed to false
# then later on in this script, after field_in_dir and f_in have been defined,
# if override_in_msh_dir is true,     in_msh_dir = field_in_dir and in_msh_f = f_in
# if override_in_msh_dir is false, in_msh_dir = IN_MSH_DIR in_msh_f = m_in
# question: how do I specificy where to find m_in? currently it is still hard coded at the top of this script
# also you need to put the mesh data into IN_MSH_DIR
override_in_msh_dir=true
if [ -z ${IN_MSH_DIR+x} ]; then
    msg="IN_MSH_DIR is empty"
    printf "${msg}"
    exit 1                                                                                      
elif [ ${#IN_MSH_DIR[@]} -gt 0 ]; then
  if [ ! -d  ${IN_MSH_DIR} || ! -r ${IN_MSH_DIR} ]; then                                      
    exit 1
  else                                                                                        
    # take an action based on the correctly supplied path which is readable
    override_in_msh_dir=false
    in_msh_dir = IN_MSH_DIR
    in_msh_f = m_in
  fi
  else
    # take an action where the variable is assigned blank, and we can reuse the same file
    # override_in_msh_dir is still set to true
fi

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
  scrpt_dir=${USR_HME}/preprocessMPAS
  if [ ! -d ${scrpt_dir} ]; then
    printf "ERROR: preprocessingMPAS directory\n ${scrpt_dir}\n does not exist.\n"
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

# check for input data root
if [ ! ${IN_DT_ROOT} ]; then
  printf "ERROR: input date root directory \${IN_DT_ROOT} is not defined.\n"
  exit 1
elif [[ ! -d ${IN_DT_ROOT} || ! -r ${IN_DT_ROOT} ]]; then
  msg="ERROR: input date root directory\n ${IN_DT_ROOT}\n"
  msg+=" does not exist or is not readable.\n"
  printf "${msg}"
  exit 1
fi

# create output directory if does not exist
if [ ! ${OUT_DT_ROOT} ]; then
  printf "ERROR: output date root directory \${OUT_DT_ROOT} is not defined.\n"
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

# compute accumulation from cf file, TRUE or FALSE
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
      # check that the precip accumulations are summable from mpascf files
      if [ ! $(( ${acc_hr} % ${ANL_INC} )) = 0 ]; then
        printf "ERROR: precip accumulation ${acc_hr} is not a multiple of ${ANL_INC}.\n"
        exit 1
      else
       printf "Computing precipitation accumulation for interval ${acc_hr} hours.\n"
       acc_hrs+=( ${acc_hr} )
      fi
    done
  fi
elif [[ ${CMP_ACC} =~ ${FALSE} ]]; then
  printf "run_preprocessMPAS does not compute precip accumulations.\n"
else
  msg="ERROR: \${CMP_ACC} must be set to 'TRUE' or 'FALSE' to decide if "
  msg+="computing precip accumulation from mpascf files."
  printf "${msg}"
  exit 1
fi

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

if [ ! -r ${scrpt_dir}/config_mpascf.py ]; then
  msg="ERROR: Python module\n ${scrpt_dir}/config_mpascf.py\n does not exist.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -r ${scrpt_dir}/mpas_to_cf.py ]; then
  msg="ERROR: Auxiliary script\n ${scrpt_dir}/mpas_to_cf.py\n does not exist.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -x ${scrpt_dir}/mpas_to_latlon.sh ]; then
  msg="ERROR: Auxiliary script\n ${scrpt_dir}/mpas_to_latlon.sh\n does not exist"
  msg+=" or is not executable.\n"
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
  field_in_dir=${IN_DT_ROOT}/${cyc_dt}${IN_DT_SUBDIR}

  # set output path
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

  # clean work directory from previous mpas regridded lat lon files
  cmd="rm -f ${wrk_dir}/*latlon*"
  printf "${cmd}\n"; eval "${cmd}"

  # clean work directory from previous mpascf files
  cmd="rm -f ${wrk_dir}/mpascf*"
  printf "${cmd}\n"; eval "${cmd}"

  # clean work directory from previous accumulation files
  cmd="rm -f ${wrk_dir}/${CTR_FLW}_*QPF*"
  printf "${cmd}\n"; eval "${cmd}"

  # set input paths
  if [ ! -d ${field_in_dir} ]; then
    msg="WARNING: data input path\n ${field_in_dir}\n does not exist,"
    msg+="skipping analysis for ${cyc_dt}.\n"
    printf "${msg}"
  else
    printf "Processing forecasts in\n ${field_in_dir}\n directory.\n"
  
    # Define directory privileges for singularity exec MET
    met="apptainer exec -B ${wrk_dir}:/wrk_dir:rw,${wrk_dir}:/field_in_dir:ro ${MET}"

    # Define directory privileges for singularity exec MET_TOOLS_PY
    met_tools_py="apptainer exec -B "
    met_tools_py+="${wrk_dir}:/wrk_dir:rw,${field_in_dir}:/field_in_dir:ro,${scrpt_dir}:/scrpt_dir:ro "
    met_tools_py+="${MET_TOOLS_PY} python"

    # loop lead hours for forecast valid time for each initialization time
    for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INC} )); do
      # define valid times for mpascf precip evenly spaced
      anl_hr=$(( ${lead_hr} + ${cyc_hr} ))
      anl_dt=`date +%Y-%m-%d_%H.%M.%S -d "${strt_dt} ${anl_hr} hours"`

      # set input file name
      cd ${field_in_dir}
      f_in=`ls ${field_in_dir}/diag.${anl_dt}.nc`
      
      if [[ -r ${f_in} ]]; then
        cmd="cd ${wrk_dir}"
        printf "${cmd}\n"; eval "${cmd}"

        # cut down to file name alone
        f_in=`basename ${f_in}`


        # run script from work directory to hold temp outputs from convert_mpas
        cmd="${scrpt_dir}/mpas_to_latlon.sh ${CONVERT_MPAS} ${wrk_dir} ${in_msh_dir} ${m_in} ${field_in_dir} ${f_in}"
        printf "${cmd}\n"
        ${scrpt_dir}/mpas_to_latlon.sh ${CONVERT_MPAS} ${wrk_dir} ${in_msh_dir} ${m_in} ${field_in_dir} ${f_in}
        error=$?

        if [ ${error} -ne 0 ]; then
          printf "ERROR: mpas_to_latlon.sh did not complete successfully.\n"
          exit 1
        fi

        # set temporary lat-lon file name from work directory
        f_tmp=`ls *latlon*${anl_dt}.nc`
        
        # set output cf file name, convert to cf from latlon tmp
        # NOTE: currently convert_mpas doesn't carry time coords from input
        # to regridded output, f_in is reused here to recover timing information
        f_out="mpascf_${anl_dt}.nc"
        cmd="${met_tools_py} /scrpt_dir/mpas_to_cf.py"
        cmd+=" '/wrk_dir/${f_tmp}' '/wrk_dir/${f_out}' '/field_in_dir/${f_in}'"
        printf "${cmd}\n"; eval "${cmd}"

      else
        msg="Input file\n ${f_in}\n is not readable or "
        msg+="does not exist, skipping forecast initialization ${cyc_dt}, "
        msg+="forecast hour ${lead_hr}.\n"
        printf "${msg}"
      fi
      if [[ ${CMP_ACC} = ${TRUE} ]]; then
        for acc_hr in ${acc_hrs[@]}; do
          if [ ${lead_hr} -ge ${acc_hr} ]; then
            # define accumulation start / stop hours
            acc_strt=$(( ${lead_hr} + ${cyc_hr}  - ${acc_hr} ))
            acc_stop=$(( ${lead_hr} + ${cyc_hr} ))

            # start / stop date strings
            anl_strt=`date +%Y-%m-%d_%H.%M.%S -d "${strt_dt} ${acc_strt} hours"`
            anl_stop=`date +%Y-%m-%d_%H.%M.%S -d "${strt_dt} ${acc_stop} hours"`

            # define padded forecast hour for name strings
            pdd_hr=`printf %03d $(( 10#${lead_hr} ))`

            # CTR_FLW QPF file name convention following similar products
            mpas_acc=${CTR_FLW}_${acc_hr}QPF_${cyc_dt}_F${pdd_hr}.nc

            # Combine precip to accumulation period 
            cmd="${met} pcp_combine \
            -subtract /field_in_dir/mpascf_${anl_stop}.nc /field_in_dir/mpascf_${anl_strt}.nc\
            /wrk_dir/${mpas_acc} \
            -field 'name=\"precip\"; level=\"(0,*,*)\";'\
            -name \"QPF_${acc_hr}hr\" "
            printf "${cmd}\n"; eval "${cmd}"
          fi
        done
      fi
    done
  fi
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`,"
msg+="verify outputs at \${OUT_DT_ROOT}:\n ${OUT_DT_ROOT}\n"
printf "${msg}"

#################################################################################
# end

exit 0
