#!/bin/bash
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --mem=120G
#SBATCH -t 01:30:00
#SBATCH --job-name="wrfcf"
#SBATCH --export=ALL
#SBATCH --account=cwp106
#################################################################################
# Description
#################################################################################
# This driver script is designed as a companion to the WRF preprocessing script
# wrfout_to_cf.ncl to ready WRF outputs for MET. This script is based on original
# source code provided by Rachel Weihs, Caroline Papadopoulos and Daniel
# Steinhoff.  This is re-written to homogenize project structure and to include
# flexibility with batch processing ranges of data from multiple workflows.
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
# SET GLOBAL PARAMETERS 
#################################################################################
# uncoment to make verbose for debugging
#set -x

# initiate bash and source bashrc to initialize environement
conda init bash
source /home/cgrudzien/.bashrc

# set local environment for ncl and related dependencies
conda activate netcdf

# root directory for MET-tools git clone
USR_HME=/cw3e/mead/projects/cwp106/scratch/cgrudzien/MET-tools

# root directory for cycle time (YYYYMMDDHH) directories of wrf outputs
IN_ROOT=/cw3e/mead/projects/cwp106/scratch/GSI-WRF-Cycling-Template/data/simulation_io

# Subdirectory for wrfoutputs in cycle time directories
# includes leading '/', set to empty string if not needed
DATE_SUBDIR=/wrfprd/ens_00

# directory for MET analysis outputs
OUT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/cycling_sensitivity_testing

# define control flow to analyze 
CTR_FLW=deterministic_forecast_lag00_b0.00_v06_h0900

# define the case study for sub-directory nesting
CSE=VD

# define first and last date time for forecast initialization (YYYYMMDDHH)
STRT_DT=2019021100
END_DT=2019021400

# define the interval between forecast initializations (HH)
CYC_INT=24

# define min / max forecast hours for forecast outputs to be processed
ANL_MIN=24
ANL_MAX=96

# define the interval at which to process forecast outputs (HH)
ANL_INT=24

# define the accumulation interval for verification valid times
ACC_INT=24

# verification domain for the forecast data (e.g., d01)
GRD=d02

# set to regrid to lat / long for MET compatibility when handling grid errors
# must be equal to TRUE or FALSE
RGRD=FALSE

#################################################################################
# Process data
#################################################################################
# define derived data paths
cse=${CSE}/${CTR_FLW}

# check for input data root
in_root="${IN_ROOT}/${cse}"
if [ ! -d ${in_root} ]; then
  echo "ERROR: input data root directory ${in_root} does not exist."
  exit 1
fi

# create output directory if does not exist
out_root=${OUT_ROOT}/${cse}/MET_analysis
cmd="mkdir -p ${out_root}"
echo ${cmd}; eval ${cmd}

# change to scripts directory
cmd="cd ${USR_HME}"
echo ${cmd}; eval ${cmd}

# Convert STRT_DT from 'YYYYMMDDHH' format to strt_dt Unix date format
if [ ${#STRT_DT} -ne 10 ]; then
  echo "ERROR: \${STRT_DT} is not in YYYYMMDDHH  format."
  exit 1
else
  strt_dt="${STRT_DT:0:8} ${STRT_DT:8:2}"
  strt_dt=`date -d "${strt_dt}"`
fi

# Convert END_DT from 'YYYYMMDDHH' format to end_dt Unix date format 
if [ ${#END_DT} -ne 10 ]; then
  echo "ERROR: \${END_DT} is not in YYYYMMDDHH  format."
  exit 1
else
  end_dt="${END_DT:0:8} ${END_DT:8:2}"
  end_dt=`date -d "${end_dt}"`
fi

if [ ${RGRD} = TRUE ]; then
  # standard coordinates that can be used to regrid westwrf
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

# define the number of dates to loop
fcst_hrs=$(( (`date +%s -d "${end_dt}"` - `date +%s -d "${strt_dt}"`) / 3600 ))

for (( cyc_hr = 0; cyc_hr <= ${fcst_hrs}; cyc_hr += ${CYC_INT} )); do
  # directory string for forecast analysis initialization time
  dirstr=`date +%Y%m%d%H -d "${strt_dt} ${cyc_hr} hours"`

  # set input paths
  input_path="${in_root}/${dirstr}${DATE_SUBDIR}"
  if [ ! -d ${input_path} ]; then
    echo "WARNING: data input path ${input_path} does not exist."
    echo "Skipping analysis for ${dirstr}."
  else
    echo "Processing forecasts in ${input_path} directory."
  
    # loop lead hours for forecast valid time for each initialization time
    for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INT} )); do
      # define valid times for accumulation    
      (( anl_end_hr = lead_hr + cyc_hr ))
      (( anl_strt_hr = anl_end_hr - ACC_INT ))
      anl_end=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_end_hr} hours"`
      anl_strt=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_strt_hr} hours"`

      # set input file names
      file_1="${input_path}/wrfout_${GRD}_${anl_strt}"
      file_2="${input_path}/wrfout_${GRD}_${anl_end}"
      
      # set output path
      output_path="${out_root}/${dirstr}/${GRD}"
      cmd="mkdir -p ${output_path}"
      echo ${cmd}; eval ${cmd}
      
      # set output file name
      output_file="wrfcf_${GRD}_${anl_strt}_to_${anl_end}.nc"
      out_name="${output_path}/${output_file}"
      
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
echo "Verify outputs at out_root ${out_root}."

#################################################################################
# end

exit 0
