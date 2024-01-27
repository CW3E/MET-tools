#!/bin/bash
#################################################################################
# Description
#################################################################################
# This script runs a batch processing routine for a given control flow /
# grid configuration and date range as defined in the companion batch and config
# scripts. This driver script loops the calls to the WRF preprocessing script
# wrfout_to_cf.ncl to ready WRF outputs for MET, and will optionally compute
# accumulated precip in addition. This script is based on original
# source code provided by Rachel Weihs, Caroline Papadopoulos and Daniel
# Steinhoff.  This is re-written to homogenize project structure and to include
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
# Check for required fields
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
  scrpt_dir=${USR_HME}/preprocessWRF
  if [ ! -d ${scrpt_dir} ]; then
    printf "ERROR: preprocessingWRF directory\n ${scrpt_dir}\n does not exist.\n"
    exit 1
  fi
fi

# verification domain for the forecast data
if [[ ! ${GRD} =~ ^d[0-9]{2}$ ]]; then
  printf "ERROR: grid name must be in dXX format.\n"
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

if [[ ${RGRD} = ${TRUE} ]]; then
  # standard coordinates that can be used to regrid West-WRF
  printf "WRF outputs will be regridded for MET compatibility.\n"
  gres=(0.08 0.027 0.009)
  lat1=(5 29 35)
  lat2=(65 51 40.5)
  lon1=(162 223.5 235)
  lon2=(272 253.5 240.5)
elif [[ ${RGRD} = ${FALSE} ]]; then
  printf "WRF outputs will be used with MET in their native grid.\n"
else
  printf "ERROR: \${RGRD} must equal 'TRUE' or 'FALSE' (case insensitive).\n"
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
elif [[ ${CMP_ACC} =~ ${FALSE} ]]; then
  printf "run_preprocessWRF does not compute precip accumulations.\n"
else
  msg="ERROR: \${CMP_ACC} must be set to 'TRUE' or 'FALSE' to decide if "
  msg+="computing precip accumulation from wrfcf files."
  printf "${msg}"
  exit 1
fi

if [ ! -x ${NETCDF_TOOLS} ]; then
  msg="NetCDF tools singularity image\n ${NETCDF_TOOLS}\n does not exist"
  msg+=" or is not executable.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -r ${scrpt_dir}/wrfout_to_cf.ncl ]; then
  msg="Auxiliary script\n ${scrpt_dir}/wrfout_to_cf.ncl\n does not exist"
  msg+=" or is not executable.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -x ${MET} ]; then
  msg="MET singularity image\n ${MET}\n does not exist or is not executable.\n"
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
  in_dir=${IN_DT_ROOT}/${cyc_dt}${IN_DT_SUBDIR}

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

  # clean work directory from previous wrfcf files
  cmd="rm ${wrk_dir}/wrfcf*"
  printf "${cmd}\n"; eval "${cmd}"

  # clean work directory from previous accumulation files
  cmd="rm ${wrk_dir}/WRF_*QPF*"
  printf "${cmd}\n"; eval "${cmd}"

  # set input paths
  if [ ! -d ${in_dir} ]; then
    msg="WARNING: data input path\n ${in_dir}\n does not exist,"
    msg+="skipping analysis for ${cyc_dt}.\n"
    printf "${msg}"
  else
    printf "Processing forecasts in\n ${in_dir}\n directory.\n"
  
    # Define directory privileges for singularity exec NETCDF_TOOLS
    netcdf_tools="singularity exec -B ${wrk_dir}:/wrk_dir:rw,"
    netcdf_tools+="${in_dir}:/in_dir:ro,${scrpt_dir}:/scrpt_dir:ro "
    netcdf_tools+="${NETCDF_TOOLS} "

    # Define directory privileges for singularity exec MET
    met="singularity exec -B ${wrk_dir}:/wrk_dir:rw,${wrk_dir}:/in_dir:ro ${MET}"

    # loop lead hours for forecast valid time for each initialization time
    for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INC} )); do
      # define valid times for wrfcf precip evenly spaced
      anl_hr=$(( ${lead_hr} + ${cyc_hr} ))
      anl_dt=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_hr} hours"`

      # set input file names
      f_in="wrfout_${GRD}_${anl_dt}"
      
      # set output file names
      f_out="wrfcf_${anl_dt}.nc"

      if [[ -r ${in_dir}/${f_in} ]]; then
        cmd="/expanse/nfs/cw3e/cwp157/cgrudzien/JEDI-MPAS-Common-Case/SOFT_ROOT/Micromamba/envs/xarray/bin/"
        cmd+="python wrfout_to_cf.py"
        cmd+=" '${in_dir}/${f_in}' '${wrk_dir}/${f_out}'"
        printf "${cmd}\n"; eval "${cmd}"

        #cmd="${netcdf_tools} \
        #ncl 'file_in=\"/in_dir/${f_in}\"' \
        #'file_out=\"/wrk_dir/${f_out}\"' /scrpt_dir/wrfout_to_cf.ncl"
        #printf "${cmd}\n"; eval "${cmd}"

        if [[ ${RGRD} = ${TRUE} ]]; then
          #-remapbil,global_${gres} -selname,precip,IVT,IVTU,IVTV,IWV \
          # regrids to lat-lon from native grid with CDO
          cmd="${netcdf_tools} \
          cdo -f nc4 sellonlatbox,${lon1},${lon2},${lat1},${lat2} \
          -remapbil,global_${gres} -selname,precip \
          /wrk_dir/${f_out} /wrk_dir/${f_out}_tmp"
          printf "${cmd}\n"; eval "${cmd}"

          # Adds forecast_reference_time back in from first output
          cmd="${netcdf_tools} \
          ncks -A -v forecast_reference_time \
          /wrk_dir/${f_out} /wrk_dir/${f_out}_tmp"
          printf "${cmd}\n"; eval "${cmd}"

          # removes temporary data with regridded cf compliant outputs
          cmd="mv ${wrk_dir}/${f_out}_tmp ${wrk_dir}/${f_out}"
          printf "${cmd}\n"; eval "${cmd}"
        fi

      else
        msg="Input\n ${f_in}\n is not readable or "
        msg+="does not exist, skipping forecast initialization ${cyc_dt}, "
        msg+="forecast hour ${lead_hr}.\n"
        printf "${msg}"
      fi
      if [[ ${CMP_ACC} = ${TRUE} ]]; then
        for acc_hr in ${acc_hrs[@]}; do
          if [ ${lead_hr} -ge ${acc_hr} ]; then
            # define accumulation start / stop hours
            acc_strt=$(( ${lead_hr} + ${cyc_hr} ))
            acc_stop=$(( ${lead_hr} + ${cyc_hr} - ${acc_hr} ))

            # start / stop date strings
            anl_strt=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${acc_strt} hours"`
            anl_stop=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${acc_stop} hours"`

            # define padded forecast hour for name strings
            pdd_hr=`printf %03d $(( 10#${lead_hr} ))`

            init_dt=`date +%Y%m%d%H -d "${strt_dt}"`

            # WRF QPF file name convention following similar products
            wrf_acc=WRF_${acc_hr}QPF_${init_dt}_F${pdd_hr}.nc

            # Combine precip to accumulation period 
            cmd="${met} pcp_combine \
            -subtract /in_dir/wrfcf_${anl_strt}.nc /in_dir/wrfcf_${anl_stop}.nc\
            /wrk_dir/${wrf_acc} \
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
