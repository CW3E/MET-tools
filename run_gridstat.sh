#!/bin/bash
#SBATCH --partition=shared
#SBATCH --nodes=1
#SBATCH --mem=120G
#SBATCH -t 02:30:00
#SBATCH --job-name="gridstat"
#SBATCH --export=ALL
#SBATCH --account=cwp106
#SBATCH --mail-user cgrudzien@ucsd.edu
#################################################################################
# Description
#################################################################################
# This driver script is based on original source code provided by Rachel Weihs
# and Caroline Papadopoulos.  This is re-written to homogenize project structure
# and to include flexibility with batch processing date ranges of data.
#
# The purpose of this script is to compute grid statistics using MET
# after pre-procssing WRF forecast data and StageIV precip data for
# validating the forecast peformance. Note, bootstrapped confidence intervals
# and rank correlation statitistics are costly to compute and significantly
# increase run time.  For rapid diagnostics these options should be turned off.
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

# control flow to be processed
CTR_FLW=ECMWF

# verification domain for the forecast data
GRD=0.25

# define the case-wise sub-directory
CSE=DD

# root directory for MET-tools git clone
USR_HME=/cw3e/mead/projects/cwp106/scratch/cgrudzien/MET-tools

# root directory for cycle time (YYYYMMDDHH) directories of cf-compliant files
IN_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/DATA

# Fixed path that preceeds cycle time directories in ${IN_ROOT}
# includes leading '/', set to empty string if not needed
DATE_ROOT=/Precip

# Subdirectory for wrfoutputs in cycle time directories
# includes leading '/', set to empty string if not needed
DATE_SUBDIR=""

# root directory for cycle time (YYYYMMDDHH) directories of gridstat outputs
OUT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/interpolation_sensitivity

# root directory for verification data
DATA_ROOT=/cw3e/mead/projects/cnt102/METMODE_PreProcessing/data/StageIV

# root directory for MET software
SOFT_ROOT=/cw3e/mead/projects/cwp106/scratch/cgrudzien/SOFT_ROOT/MET_CODE
MET_SNG=${SOFT_ROOT}/met-10.0.1.simg

## landmask settings for verification region
# File name / figure label
#MSK=CALatLonPoints
MSK=CA_Climate_Zone_16_Sierra

# File extension
MSK_EXT=.poly

# Root directory for landmask
#MSK_ROOT=${SOFT_ROOT}/polygons/region
MSK_ROOT=${SOFT_ROOT}/polygons/CA_Climate_Zone

# define first and last date time for forecast initialization (YYYYMMDDHH)
STRT_DT=2022122900
END_DT=2022123100

# define the interval between forecast initializations (HH)
CYC_INT=24

# define min / max forecast hours for forecast outputs to be processed
ANL_MIN=24
ANL_MAX=240

# define the interval at which to process forecast outputs (HH)
ANL_INT=24

# define the accumulation interval for verification valid times
ACC_INT=24

# define the verification field
VRF_FLD=QPF

# specify thresholds levels for verification
CAT_THR="[ >0.0, >=10.0, >=25.4, >=50.8, >=101.6 ]"

# define the interpolation method and related parameters
INT_SHPE=SQUARE
INT_MTHD=DW_MEAN
INT_WDTH=3

# neighborhood width for neighborhood methods
NBRHD_WDTH=9

# number of bootstrap resamplings, set 0 for off
BTSTRP=0

# rank correlation computation flag, TRUE or FALSE
RNK_CRR=FALSE

# compute accumulation from cf file, TRUE or FALSE
CMP_ACC=FALSE

# optionally define an output prefix based on settings, leave as a blank string
# to have no prefix on gridstat outputs
PRFX="${INT_MTHD}_${INT_WDTH}"

#################################################################################
# Process data
#################################################################################
# define derived paths
cse="${CSE}/${CTR_FLW}"

# check for input data root
in_root="${IN_ROOT}/${cse}${DATE_ROOT}"
if [ ! -d ${in_root} ]; then
  echo "ERROR: input data root directory, ${in_root}, does not exist."
  exit 1
fi

# create output directory if does not exist
out_root=${OUT_ROOT}/${cse}/MET_analysis
cmd="mkdir -p ${out_root}"
echo ${cmd}; eval ${cmd}

# check for software and data deps.
if [ ! -d ${DATA_ROOT} ]; then
  echo "ERROR: StageIV data directory, ${DATA_ROOT}, does not exist."
  exit 1
fi

if [ ! -x ${MET_SNG} ]; then
  echo "MET singularity image, ${MET_SNG}, does not exist or is not executable."
  exit 1
fi

if [ ! -r "${MSK_ROOT}/${MSK}${MSK_EXT}"  ]; then
  msg="ERROR: verification region landmask, ${MSK_ROOT}/${MSK}${MSK_EXT}, "
  msg+="does not exist or is not readable."
  echo ${msg}
  exit 1
fi

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

if [ ${#PRFX} -gt 0 ]; then
  # for a non-empty prefix, append an underscore for compound names
  prfx="${PRFX}_"
else
  prfx=""
fi

# change to scripts directory
cmd="cd ${USR_HME}"
echo ${cmd}; eval ${cmd}

# define the number of dates to loop
fcst_hrs=$(( (`date +%s -d "${end_dt}"` - `date +%s -d "${strt_dt}"`) / 3600 ))

for (( cyc_hr = 0; cyc_hr <= ${fcst_hrs}; cyc_hr += ${CYC_INT} )); do
  # directory string for forecast analysis initialization time
  dirstr=`date +%Y%m%d%H -d "${strt_dt} ${cyc_hr} hours"`

  # cycle date directory of cf-compliant input files
  in_dir=${in_root}/${dirstr}${DATE_SUBDIR}

  # set and clean working directory based on looped forecast start date
  work_root=${out_root}/${dirstr}/${GRD}
  mkdir -p ${work_root}
  rm -f ${work_root}/grid_stat_${PRFX}*.txt
  rm -f ${work_root}/grid_stat_${PRFX}*.stat
  rm -f ${work_root}/grid_stat_${PRFX}*.nc
  rm -f ${work_root}/${prfx}GridStatConfig

  # loop lead hours for forecast valid time for each initialization time
  for (( lead_hr = ${ANL_MIN}; lead_hr <= ${ANL_MAX}; lead_hr += ${ANL_INT} )); do
    # define valid times for accumulation    
    (( anl_end_hr = lead_hr + cyc_hr ))
    (( anl_strt_hr = anl_end_hr - ACC_INT ))
    anl_end=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_end_hr} hours"`
    anl_strt=`date +%Y-%m-%d_%H_%M_%S -d "${strt_dt} ${anl_strt_hr} hours"`

    validyear=${anl_end:0:4}
    validmon=${anl_end:5:2}
    validday=${anl_end:8:2}
    validhr=${anl_end:11:2}
    
    # forecast file name based on forecast initialization and lead
    pdd_hr=`printf %03d $(( 10#${lead_hr} ))`
    for_f_in=${CTR_FLW}_${ACC_INT}${VRF_FLD}_${dirstr}_F${pdd_hr}.nc

    # obs file defined in terms of valid time
    obs_f_in=StageIV_QPE_${validyear}${validmon}${validday}${validhr}.nc

    # Set up singularity container with directory privileges
    cmd="singularity instance start -B ${work_root}:/work_root:rw,"
    cmd+="${DATA_ROOT}:/DATA_ROOT:ro,${MSK_ROOT}:/MSK_ROOT:ro,"
    cmd+="${in_dir}:/in_dir:ro,${USR_HME}:/USR_HME:ro"
    cmd+=" ${MET_SNG} met1"
    echo ${cmd}; eval ${cmd}

    if [[ ${CMP_ACC} = "TRUE" ]]; then
      # check for input file based on output from run_wrfout_cf.sh
      if [ -r ${in_dir}/wrfcf_${GRD}_${anl_strt}_to_${anl_end}.nc ]; then
        # Set accumulation initialization string
        inityear=${dirstr:0:4}
        initmon=${dirstr:4:2}
        initday=${dirstr:6:2}
        inithr=${dirstr:8:2}

        # Combine precip to accumulation period 
        cmd="singularity exec instance://met1 pcp_combine \
        -sum ${inityear}${initmon}${initday}_${inithr}0000 ${ACC_INT} \
        ${validyear}${validmon}${validday}_${validhr}0000 ${ACC_INT} \
        /work_root/${prfx}${for_f_in} \
        -field 'name=\"precip_bkt\";  level=\"(*,*,*)\";' -name \"${VRF_FLD}_${ACC_INT}hr\" \
        -pcpdir /in_dir \
        -pcprx \"wrfcf_${GRD}_${anl_strt}_to_${anl_end}.nc\" "
        echo ${cmd}; eval ${cmd}
      else
        cmd="pcp_combine input file ${in_dir}/wrfcf_${GRD}_${anl_strt}_to_${anl_end}.nc is not "
        cmd+="readable or does not exist, skipping pcp_combine for "
        cmd+="forecast initialization ${dirstr}, forecast hour ${lead_hr}." 
        echo ${cmd}
      fi
    else
      # copy the preprocessed data to the working directory from the data root
      in_path="${in_dir}/${for_f_in}"
      if [ -r ${in_path} ]; then
        cmd="cp -L ${in_path} ${work_root}/${prfx}${for_f_in}"
        echo ${cmd}; eval ${cmd}
      else
        echo "Source file ${in_path} not found."
      fi
    fi
    
    if [ -r ${work_root}/${prfx}${for_f_in} ]; then
      if [ -r ${DATA_ROOT}/${obs_f_in} ]; then
        # masks are recreated depending on the existence of files from previous loops
        # NOTE: need to determine under what conditions would this file need to update
        if [ ! -r ${work_root}/${MSK}_mask_regridded_with_StageIV.nc ]; then
          cmd="singularity exec instance://met1 gen_vx_mask -v 10 \
          /DATA_ROOT/${obs_f_in} \
          -type poly \
          /MSK_ROOT/${MSK}${MSK_EXT} \
          /work_root/${MSK}_mask_regridded_with_StageIV.nc"
          echo ${cmd}
          eval ${cmd}
        fi

        # update GridStatConfigTemplate archiving file in working directory unchanged on inner loop
        if [ ! -r ${work_root}/${prfx}GridStatConfig ]; then
          cat ${USR_HME}/GridStatConfigTemplate \
            | sed "s/INT_MTHD/method = ${INT_MTHD}/" \
            | sed "s/INT_WDTH/width = ${INT_WDTH}/" \
            | sed "s/INT_SHPE/shape      = ${INT_SHPE}/" \
            | sed "s/RNK_CRR/rank_corr_flag      = ${RNK_CRR}/" \
            | sed "s/VRF_FLD/name       = \"${VRF_FLD}_${ACC_INT}hr\"/" \
            | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
            | sed "s/PLY_MSK/poly = [ \"\/work_root\/${MSK}_mask_regridded_with_StageIV.nc\" ]/" \
            | sed "s/BTSTRP/n_rep    = ${BTSTRP}/" \
            | sed "s/NBRHD_WDTH/width = [ ${NBRHD_WDTH} ]/" \
            | sed "s/PRFX/output_prefix    = \"${PRFX}\"/" \
            > ${work_root}/${prfx}GridStatConfig
        fi

        # Run gridstat
        cmd="singularity exec instance://met1 grid_stat -v 10 \
        /work_root/${prfx}${for_f_in} \
        /DATA_ROOT/${obs_f_in} \
        /work_root/${prfx}GridStatConfig \
        -outdir /work_root"
        echo ${cmd}; eval ${cmd}
        
      else
        cmd="Observation verification file ${DATA_ROOT}/${obs_f_in} is not "
        cmd+=" readable or does not exist, skipping grid_stat for forecast "
        cmd+="initialization ${dirstr}, forecast hour ${lead_hr}." 
        echo ${cmd}
      fi

    else
      cmd="gridstat input file ${out_root}/${prfx}${for_f_in} is not readable " 
      cmd+=" or does not exist, skipping grid_stat for forecast initialization "
      cmd+="${dirstr}, forecast hour ${lead_hr}." 
      echo ${cmd}
    fi

    # End MET Process and singularity stop
    cmd="singularity instance stop met1"
    echo ${cmd}; eval ${cmd}

    # clean up working directory
    cmd="rm -f ${work_root}/${prfx}${for_f_in}"
    echo ${cmd}; eval ${cmd}
  done
done

echo "Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify outputs at out_root ${out_root}"

#################################################################################
# end

exit 0
