#!/bin/bash
#################################################################################
# Description
#################################################################################
# This script defines the batch processing routine for a given control flow /
# grid configuration and date range as defined in the companion batch_wrfout_cf.sh
# script. This driver script loops the calls to the WRF preprocessing script
# wrfout_to_cf.ncl to ready WRF outputs for MET. This script is based on original
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
# make checks for workflow parameters

# define the working scripts directory
if [ ! ${USR_HME} ]; then
  printf "ERROR: MET-tools clone directory \${USR_HME} is not defined.\n"
  exit 1
elif [ ! -d ${USR_HME} ]; then
  printf "ERROR: MET-tools clone directory\n ${USR_HME}\n does not exist.\n"
  exit 1
else
  scrpt_dir=${USR_HME}/Grid-Stat
  if [ ! -d ${scrpt_dir} ]; then
    printf "ERROR: Grid-Stat script directory\n ${scrpt_dir}\n does not exist.\n"
    exit 1
  fi
fi

# control flow to be processed
if [ ! ${CTR_FLW} ]; then
  printf "ERROR: control flow name \${CTR_FLW} is not defined.\n"
  exit 1
fi

# verification domain for the forecast data
if [ ! ${GRD} ]; then
  printf "ERROR: grid name \${GRD} is not defined.\n"
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

# Convert STOP_DT from 'YYYYMMDDHH' format to end_dt Unix date format 
if [ ${#STOP_DT} -ne 10 ]; then
  printf "ERROR: \${STOP_DT} is not in YYYYMMDDHH format.\n"
  exit 1
else
  end_dt="${STOP_DT:0:8} ${STOP_DT:8:2}"
  end_dt=`date -d "${end_dt}"`
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

# define the accumulation interval for verification valid times
if [ ! ${ACC_INT} ]; then
  printf "ERROR: hours accumulation interval for verification not defined.\n"
  exit 1
fi

# check for input data root
if [ ! -d ${IN_CYC_DIR} ]; then
  printf "ERROR: input data root directory\n ${IN_CYC_DIR}\n does not exist.\n"
  exit 1
fi

# create output directory if does not exist
if [ ! ${OUT_CYC_DIR} ]; then
  printf "ERROR: output data root directory \${OUT_CYC_DIR} is not defined.\n"
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

if [ ${RGRD} = TRUE ]; then
  # standard coordinates that can be used to regrid West-WRF
  printf "WRF outputs will be regridded for MET compatibility.\n"
  gres=(0.08 0.027 0.009)
  lat1=(5 29 35)
  lat2=(65 51 40.5)
  lon1=(162 223.5 235)
  lon2=(272 253.5 240.5)
elif [ ${RGRD} = FALSE ]; then
  printf "WRF outputs will be used with MET in their native grid.\n"
else
  printf "ERROR: \${RGRD} must equal 'TRUE' or 'FALSE' (case sensitive).\n"
  exit 1
fi

if [ ! -x ${NETCDF_TOOLS} ]; then
  msg="NetCDF tools singularity image\n ${NETCDF_TOOLS}\n does not exist"
  msg+=" or is not executable.\n"
  printf "${msg}"
  exit 1
fi

if [ ! -x ${scrpt_dir}/wrfout_to_cf.ncl ]; then
  msg="Auxiliary script\n ${scrpt_dir}/wrfout_to_cf.ncl\n does not exist"
  msg+=" or is not executable.\n"
  printf "${msg}"
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# define the number of dates to loop
fcst_hrs=$(( (`date +%s -d "${end_dt}"` - `date +%s -d "${strt_dt}"`) / 3600 ))

for (( cyc_hr = 0; cyc_hr <= ${fcst_hrs}; cyc_hr += ${CYC_INT} )); do
  # directory string for forecast analysis initialization time
  dirstr=`date +%Y%m%d%H -d "${strt_dt} ${cyc_hr} hours"`
  in_dir=${IN_CYC_DIR}/${dirstr}${IN_DT_SUBDIR}

  # set output path
  wrk_dir=${OUT_CYC_DIR}/${dirstr}${OUT_DT_SUBDIR}
  cmd="mkdir -p ${wrk_dir}"
  printf "${cmd}\n"; eval "${cmd}"
      
  # set input paths
  if [ ! -d ${in_dir} ]; then
    msg="WARNING: data input path\n ${in_dir}\n does not exist,"
    msg+="skipping analysis for ${dirstr}.\n"
    printf "${msg}"
  else
    printf "Processing forecasts in\n ${in_dir}\n directory.\n"
  
    # Define directory privileges for singularity exec
    netcdf_tools="singularity exec -B ${wrk_dir}:/wrk_dir:rw,"
    netcdf_tools+="${in_dir}:/in_dir:ro,${scrpt_dir}:/scrpt_dir:ro "
    netcdf_tools+="${NETCDF_TOOLS} "

    # loop lead hours for forecast valid time for each initialization time
    for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INT} )); do
      # define valid times for accumulation    
      anl_strt_hr=$(( ${lead_hr} + ${cyc_hr} - ${ACC_INT} ))
      anl_stop_hr=$(( ${lead_hr} + ${cyc_hr} ))
      anl_strt=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_strt_hr} hours"`
      anl_stop=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_stop_hr} hours"`

      # set input file names
      f_pr="wrfout_${GRD}_${anl_strt}"
      f_in="wrfout_${GRD}_${anl_stop}"
      
      # set output file name
      f_out="wrfcf_${GRD}_${anl_strt}_to_${anl_stop}.nc"

      if [[ -r ${in_dir}/${f_pr} && -r ${in_dir}/${f_in} ]]; then
        cmd="${netcdf_tools} \
        ncl 'file_in=\"/in_dir/${f_in}\"' 'file_prev=\"/in_dir/${f_pr}\"' \
        'file_out=\"/wrk_dir/${f_out}\"' /scrpt_dir/wrfout_to_cf.ncl"
        printf "${cmd}\n"; eval "${cmd}"

        if [ ${RGRD} = TRUE ]; then
          # regrids to lat-lon from native grid with CDO
          cmd="${netcdf_tools} \
          cdo -f nc4 sellonlatbox,${lon1},${lon2},${lat1},${lat2} \
          -remapbil,global_${gres} -selname,precip,precip_bkt,IVT,IVTU,IVTV,IWV \
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
        msg="Either\n ${f_pr}\n or\n ${f_in}\n is not readable or "
        msg+="does not exist, skipping forecast initialization ${dirstr}, "
        msg+="forecast hour ${lead_hr}.\n"
        printf "${msg}"
      fi
    done

  fi
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`,"
msg+="verify outputs at out_root:\n ${OUT_CYC_DIR}\n"
printf "${msg}"

#################################################################################
# end

exit 0
