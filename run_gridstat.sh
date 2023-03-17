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
# READ WORKFLOW PARAMETERS
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

# define the verification field
if [ ! ${VRF_FLD} ]; then
  echo "ERROR: verification field \${VRF_FLD} is not defined."
  exit 1
fi

# Landmask for verification region file name with extension
if [ ! ${MSK} ]; then
  echo "ERROR: landmask \${MSK} is not defined."
  exit 1
fi

# define the interpolation method and related parameters
if [ ! ${INT_MTHD} ]; then
  echo "ERROR: regridding interpolation method \${INT_MTHD} is not defined."
  exit 1
fi

if [ ! ${INT_WDTH} ]; then 
  echo "ERROR: interpolation neighborhood width \${INT_WDTH} is not defined."
  exit 1
fi

# neighborhood width for neighborhood methods
if [ ! ${NBRHD_WDTH} ]; then
  echo "ERROR: neighborhood statistics width ${NBRHD_WDTH} is not defined."
  exit 1
fi

# number of bootstrap resamplings, set 0 for off
if [ ! ${BTSTRP} ]; then
  echo "ERROR: bootstrap resampling number \${BTSRP} is not defined."
  echo "Set \${BTSTRP} to a positive integer or to 0 to turn off."
  exit 1
fi

# rank correlation computation flag, TRUE or FALSE
if [ ! ${RNK_CRR} ]; then
  msg="ERROR: \${RNK_CRR} must be set to 'TRUE' or 'FALSE' if computing "
  msg+=" rank statistics."
  echo ${msg}
  exit 1
fi

# compute accumulation from cf file, TRUE or FALSE
if [ ! ${CMP_ACC} ]; then
  msg="ERROR: \${CMP_ACC} must be set to 'TRUE' or 'FALSE' if computing "
  msg+="accumulation from source input file."
  exit 1
fi

if [ -z ${PRFX+x} ]; then
  echo "ERROR: gridstat output \${PRFX} is unset, set to empty string if not used."
  exit 1
fi

if [ -z ${IN_DT_SUBDIR+x} ]; then
  echo "ERROR: cycle subdirectory for input data \${IN_DT_SUBDIR} is unset,"
  echo " set to empty string if not used."
  exit 1
fi

if [ -z ${OUT_DT_SUBDIR+x} ]; then
  echo "ERROR: cycle subdirectory for input data \${OUT_DT_SUBDIR} is unset,"
  echo " set to empty string if not used."
  exit 1
fi

# check for input data root
if [ ! -d ${IN_CYC_DIR} ]; then
  echo "ERROR: input data root directory, ${IN_CYC_DIR}, does not exist."
  exit 1
fi

# create output directory if does not exist
cmd="mkdir -p ${OUT_CYC_DIR}"
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

# read in mask file name and separate name from extension
IFS="." read -ra split_string <<< ${MSK}
msk_nme=${split_string[0]}
msk_ext=${split_string[1]}

if [ ! -r "${MSK_ROOT}/${msk_nme}.${msk_ext}"  ]; then
  msg="ERROR: verification region landmask, ${MSK_ROOT}/${msk_nme}.${msk_ext}, "
  msg+="does not exist or is not readable."
  echo ${msg}
  exit 1
fi

if [ ! ${CAT_THR} ]; then
  echo "ERROR: thresholds \${CAT_THR} is not defined."
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# change to scripts directory
cmd="cd ${USR_HME}"
echo ${cmd}; eval ${cmd}

# change to scripts directory
cmd="cd ${USR_HME}"
echo ${cmd}; eval ${cmd}

# define the number of dates to loop
fcst_hrs=$(( (`date +%s -d "${end_dt}"` - `date +%s -d "${strt_dt}"`) / 3600 ))

for (( cyc_hr = 0; cyc_hr <= ${fcst_hrs}; cyc_hr += ${CYC_INT} )); do
  # directory string for forecast analysis initialization time
  dirstr=`date +%Y%m%d%H -d "${strt_dt} ${cyc_hr} hours"`

  # cycle date directory of cf-compliant input files
  in_dir=${IN_CYC_DIR}/${dirstr}${IN_DT_SUBDIR}

  # set and clean working directory based on looped forecast start date
  work_root=${OUT_CYC_DIR}/${dirstr}${OUT_DT_SUBDIR}
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
        msg="pcp_combine input file ${in_dir}/wrfcf_${GRD}_${anl_strt}_to_${anl_end}.nc is not "
        msg+="readable or does not exist, skipping pcp_combine for "
        msg+="forecast initialization ${dirstr}, forecast hour ${lead_hr}." 
        echo ${msg}
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
        if [ ! -r ${work_root}/${msk_nme}_mask_regridded_with_StageIV.nc ]; then
          cmd="singularity exec instance://met1 gen_vx_mask -v 10 \
          /DATA_ROOT/${obs_f_in} \
          -type poly \
          /MSK_ROOT/${msk_nme}.${msk_ext} \
          /work_root/${msk_nme}_mask_regridded_with_StageIV.nc"
          echo ${cmd}
          eval ${cmd}
        fi

        # update GridStatConfigTemplate archiving file in working directory unchanged on inner loop
        if [ ! -r ${work_root}/${prfx}GridStatConfig ]; then
          cat ${USR_HME}/GridStatConfigTemplate \
            | sed "s/INT_MTHD/method = ${INT_MTHD}/" \
            | sed "s/INT_WDTH/width = ${INT_WDTH}/" \
            | sed "s/RNK_CRR/rank_corr_flag      = ${RNK_CRR}/" \
            | sed "s/VRF_FLD/name       = \"${VRF_FLD}_${ACC_INT}hr\"/" \
            | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
            | sed "s/PLY_MSK/poly = [ \"\/work_root\/${msk_nme}_mask_regridded_with_StageIV.nc\" ]/" \
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
      cmd="gridstat input file ${work_root}/${prfx}${for_f_in} is not readable " 
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

msg= "Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at OUT_CYC_DIR ${OUT_CYC_DIR}"
echo ${msg}

#################################################################################
# end

exit 0
