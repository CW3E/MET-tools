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
# Copyright 2023 Colin Grudzien, cgrudzien@ucsd.edu
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
echo "Loading configuration parameters:"
for cmd in "$@"; do
  echo ${cmd}; eval ${cmd}
done

# control flow to be processed
if [ ! ${CTR_FLW} ]; then
  echo "ERROR: control flow name \${CTR_FLW} is not defined."
  exit 1
fi

# verification domain for the forecast data
if [ ! ${GRD} ]; then
  echo "ERROR: grid name \${GRD} is not defined."
  exit 1
fi

# Convert STRT_DT from 'YYYYMMDDHH' format to strt_dt Unix date format
if [ ${#STRT_DT} -ne 10 ]; then
  echo "ERROR: \${STRT_DT} is not in YYYYMMDDHH format."
  exit 1
else
  strt_dt="${STRT_DT:0:8} ${STRT_DT:8:2}"
  strt_dt=`date -d "${strt_dt}"`
fi

# Convert END_DT from 'YYYYMMDDHH' format to end_dt Unix date format 
if [ ${#END_DT} -ne 10 ]; then
  echo "ERROR: \${END_DT} is not in YYYYMMDDHH format."
  exit 1
else
  end_dt="${END_DT:0:8} ${END_DT:8:2}"
  end_dt=`date -d "${end_dt}"`
fi

# define min / max forecast hours for forecast outputs to be processed
if [ ! ${ANL_MIN} ]; then
  echo "ERROR: min forecast hour \${ANL_MIN} is not defined."
  exit 1
fi

if [ ! ${ANL_MAX} ]; then
  echo "ERROR: max forecast hour \${ANL_MAX} is not defined."
  exit 1
fi

# define the interval at which to process forecast outputs (HH)
if [ ! ${ANL_INT} ]; then
  echo "ERROR: hours interval between analyses \${HH} is not defined."
  exit 1
fi

# define the accumulation interval for verification valid times
if [ ! ${ACC_INT} ]; then
  echo "ERROR: hours accumulation interval for verification not defined."
  exit 1
fi

# check for input data root
if [ ! -d ${IN_CYC_DIR} ]; then
  echo "ERROR: input data root directory, ${IN_CYC_DIR}, does not exist."
  exit 1
fi

# check for output data root
if [ ! -d ${OUT_CYC_DIR} ]; then
  echo "ERROR: output data root directory, ${OUT_CYC_DIR}, does not exist."
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# create output directory if does not exist
cmd="mkdir -p ${OUT_CYC_DIR}"
echo ${cmd}; eval ${cmd}

if [ ${RGRD} = TRUE ]; then
  # standard coordinates that can be used to regrid West-WRF
  echo "WRF outputs will be regridded for MET compatibility." 
  gres=(0.08 0.027 0.009)
  lat1=(5 29 35)
  lat2=(65 51 40.5)
  lon1=(162 223.5 235)
  lon2=(272 253.5 240.5)
elif [ ${RGRD} = FALSE ]; then
  echo "WRF outputs will be used with MET in their native grid."
else
  echo "ERROR: \${RGRD} must equal 'TRUE' or 'FALSE' (case sensitive)."
  exit 1
fi

# change to Grid-Stat scripts directory
cmd="cd ${USR_HME}/Grid-Stat"
echo ${cmd}; eval ${cmd}

# define the number of dates to loop
fcst_hrs=$(( (`date +%s -d "${end_dt}"` - `date +%s -d "${strt_dt}"`) / 3600 ))

for (( cyc_hr = 0; cyc_hr <= ${fcst_hrs}; cyc_hr += ${CYC_INT} )); do
  # directory string for forecast analysis initialization time
  dirstr=`date +%Y%m%d%H -d "${strt_dt} ${cyc_hr} hours"`
  in_dir=${IN_CYC_DIR}/${dirstr}${IN_DT_SUBDIR}

  # set output path
  work_root=${OUT_CYC_DIR}/${dirstr}${OUT_DT_SUBDIR}
  cmd="mkdir -p ${work_root}"
  echo ${cmd}; eval ${cmd}
      
  # set input paths
  if [ ! -d ${in_dir} ]; then
    echo "WARNING: data input path ${in_dir} does not exist."
    echo "Skipping analysis for ${dirstr}."
  else
    echo "Processing forecasts in ${in_dir} directory."
  
    # loop lead hours for forecast valid time for each initialization time
    for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INT} )); do
      # define valid times for accumulation    
      (( anl_end_hr = lead_hr + cyc_hr ))
      (( anl_strt_hr = anl_end_hr - ACC_INT ))
      anl_end=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_end_hr} hours"`
      anl_strt=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_strt_hr} hours"`

      # set input file names
      file_1="${in_dir}/wrfout_${GRD}_${anl_strt}"
      file_2="${in_dir}/wrfout_${GRD}_${anl_end}"
      
      # set output file name
      output_file="wrfcf_${GRD}_${anl_strt}_to_${anl_end}.nc"
      out_name="${work_root}/${output_file}"
      
      if [[ -r ${file_1} && -r ${file_2} ]]; then
        cmd="ncl 'file_in=\"${file_2}\"' "
        cmd+="'file_prev=\"${file_1}\"' " 
        cmd+="'file_out=\"${out_name}\"' wrfout_to_cf.ncl "
        echo ${cmd}; eval ${cmd}

        if [ ${RGRD} = TRUE ]; then
          # regrids to lat / lon from native grid with CDO
          cmd="cdo -f nc4 sellonlatbox,${lon1},${lon2},${lat1},${lat2} "
          cmd+="-remapbil,global_${gres} "
          cmd+="-selname,precip,precip_bkt,IVT,IVTU,IVTV,IWV "
          cmd+="${out_name} ${out_name}_tmp"
          echo ${cmd}; eval ${cmd}

          # Adds forecast_reference_time back in from first output
          cmd="ncks -A -v forecast_reference_time ${out_name} ${out_name}_tmp"
          echo ${cmd}; eval ${cmd}

          # removes temporary data with regridded cf compliant outputs
          cmd="mv ${out_name}_tmp ${out_name}"
          echo ${cmd}; eval ${cmd}
        fi
      else
        cmd="${file_1} or ${file_2} not readable or does not exist, "
        cmd+="skipping forecast initialization ${loopstr}, "
        cmd+="forecast hour ${lead_hr}."
        echo ${cmd}
      fi
    done
  fi
done

echo "Script completed at `date +%Y-%m-%d_%H_%M_%S`."
echo "Verify outputs at out_root ${OUT_CYC_DIR}."

#################################################################################
# end

exit 0
