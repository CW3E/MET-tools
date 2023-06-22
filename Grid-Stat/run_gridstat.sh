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
printf "Loading configuration parameters:\n"
for cmd in "$@"; do
  printf "${cmd}\n"; eval ${cmd}
done

#################################################################################
# make checks for workflow parameters
# these parameters are shared with run_wrfout_cf.sh

# define the working scripts directory
if [ ! ${USR_HME} ]; then
  printf "ERROR: MET-tools clone directory \${USR_HME} is not defined.\n"
  exit 1
elif [ ! -d ${USR_HME} ]; then
  printf "ERROR: MET-tools clone directory\n ${USR_HME}\n does not exist.\n"
  exit 1
else
  script_dir=${USR_HME}/Grid-Stat
  if [ ! -d ${script_dir} ]; then
    printf "ERROR: Grid-Stat script directory\n ${script_dir}\n does not exist.\n"
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
  printf ${msg}
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

# Convert END_DT from 'YYYYMMDDHH' format to end_dt Unix date format 
if [ ${#END_DT} -ne 10 ]; then
  printf "ERROR: \${END_DT} is not in YYYYMMDDHH format.\n"
  exit 1
else
  end_dt="${END_DT:0:8} ${END_DT:8:2}"
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
  msg="ERROR: cycle gridstat output root directory\n ${OUT_CYC_DIR}\n "
  msg+="is not defined."
  exit 1
else
  cmd="mkdir -p ${OUT_CYC_DIR}"
  printf "${cmd}\n"; eval ${cmd}
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

#################################################################################
# these parameters are gridstat specific

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
if [ ! -r ${MSKS} ]; then
  printf "ERROR: landmask list file \${MSKS} does not exist or is not readable.\n"
  exit 1
fi

# Root directory for landmasks
if [ ! ${MSK_IN} ]; then
  printf "ERROR: landmask directory \${MSK_IN} is not defined.\n"
  exit 1
fi

# loop lines of the mask list, set temporary exit status before searching for masks
estat=0

while read msk; do
  fpath=${MSK_IN}/${msk}_mask_regridded_with_StageIV.nc
  if [ -r "${fpath}" ]; then
    printf "Found\n ${fpath}_mask_regridded_with_StageIV.nc\n landmask.\n"
  else
    msg="ERROR: verification region landmask\n ${fpath}\n"
    msg+=" does not exist or is not readable.\n"
    printf ${msg}

    # create exit status flag to kill program, after checking all files in list
    estat=1
  fi
done <${MSKS}

if [ ${estat} -eq 1 ]; then
  msg="ERROR: Exiting due to missing landmasks, please see the above error "
  msg+="messages and verify the location for these files. These files can be "
  msg+="generated from lat-lon text files using the run_vxmask.sh utility script."
  exit 1
fi

# define the interpolation method and related parameters
if [ ! ${INT_MTHD} ]; then
  printf "ERROR: regridding interpolation method \${INT_MTHD} is not defined.\n"
  exit 1
fi

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
if [ ! ${BTSTRP} ]; then
  printf "ERROR: bootstrap resampling number \${BTSRP} is not defined.\n"
  printf "Set \${BTSTRP} to a positive integer or to 0 to turn off.\n"
  exit 1
fi

# rank correlation computation flag, TRUE or FALSE
if [[ ${RNK_CRR} != "TRUE" && ${RNK_CRR} != "FALSE" ]]; then
  msg="ERROR: \${RNK_CRR} must be set to 'TRUE' or 'FALSE' to decide "
  msg+="if computing rank statistics.\n"
  printf ${msg}
  exit 1
fi

# compute accumulation from cf file, TRUE or FALSE
if [[ ${CMP_ACC} != "TRUE" && ${CMP_ACC} != "FALSE" ]]; then
  msg="ERROR: \${CMP_ACC} must be set to 'TRUE' or 'FALSE' to decide if "
  msg+="computing accumulation from source input file."
  exit 1
fi

if [ -z ${PRFX+x} ]; then
  msg="ERROR: gridstat output \${PRFX} is unset, set to empty string if not used.\n"
  printf ${msg}
  exit 1
elif [ ${#PRFX} -gt 0 ]; then
  # for a non-empty prefix, append an underscore for compound names
  prfx="${PRFX}_"
else
  prfx=""
fi

# check for software and data deps.
if [ ! -d ${DATA_ROOT} ]; then
  printf "ERROR: StageIV data directory\n ${DATA_ROOT}\n does not exist.\n"
  exit 1
fi

if [ ! -x ${MET_SNG} ]; then
  msg="MET singularity image\n ${MET_SNG}\n does not exist or is not executable.\n"
  printf ${msg}
  exit 1
fi

#################################################################################
# Process data
#################################################################################
# change to scripts directory
cmd="cd ${script_dir}"
printf "${cmd}\n"; eval ${cmd}

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
  rm -f ${work_root}/PLY_MSK.txt

  # loop lines of the mask list, generate PLY_MSK.txt for GridStatConfig insert
  msk_count=`wc -l < ${MSKS}`
  line_count=1
  while read msk; do
    if [ ${line_count} -lt ${msk_count} ]; then
      ply_msk="\"/MSK_IN/${msk}_mask_regridded_with_StageIV.nc\",\n"
      printf ${ply_msk} >> ${work_root}/PLY_MSK.txt
    else
      ply_msk="\"/MSK_IN/${msk}_mask_regridded_with_StageIV.nc\""
      printf ${ply_msk} >> ${work_root}/PLY_MSK.txt
    fi
    (( line_count += 1 ))
  done <${MSKS}

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

    # Set up singularity container with specific directory privileges
    cmd="singularity instance start -B ${work_root}:/work_root:rw,"
    cmd+="${DATA_ROOT}:/DATA_ROOT:ro,${MSK_IN}:/MSK_IN:ro,"
    cmd+="${in_dir}:/in_dir:ro,${script_dir}:/script_dir:ro "
    cmd+="${MET_SNG} met1"
    printf "${cmd}\n"; eval ${cmd}

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
        -field 'name=\"precip_bkt\"; level=\"(*,*,*)\";' -name \"${VRF_FLD}_${ACC_INT}hr\" \
        -pcpdir /in_dir \
        -pcprx \"wrfcf_${GRD}_${anl_strt}_to_${anl_end}.nc\" "
        printf "${cmd}\n"; eval ${cmd}
      else
        msg="pcp_combine input file\n "
        msg+="${in_dir}/wrfcf_${GRD}_${anl_strt}_to_${anl_end}.nc\n is not "
        msg+="readable or does not exist, skipping pcp_combine for "
        msg+="forecast initialization ${dirstr}, forecast hour ${lead_hr}.\n"
        printf ${msg}
      fi
    else
      # copy the preprocessed data to the working directory from the data root
      in_path="${in_dir}/${for_f_in}"
      if [ -r ${in_path} ]; then
        cmd="cp -L ${in_path} ${work_root}/${prfx}${for_f_in}"
        printf "${cmd}\n"; eval ${cmd}
      else
        printf "Source file\n ${in_path}\n not found.\n"
      fi
    fi
    
    if [ -r ${work_root}/${prfx}${for_f_in} ]; then
      if [ -r ${DATA_ROOT}/${obs_f_in} ]; then
        # update GridStatConfigTemplate archiving file in working directory
        # this remains unchanged on inner loop
        if [ ! -r ${work_root}/${prfx}GridStatConfig ]; then
          cat ${script_dir}/GridStatConfigTemplate \
            | sed "s/INT_MTHD/method = ${INT_MTHD}/" \
            | sed "s/INT_WDTH/width = ${INT_WDTH}/" \
            | sed "s/RNK_CRR/rank_corr_flag      = ${RNK_CRR}/" \
            | sed "s/VRF_FLD/name       = \"${VRF_FLD}_${ACC_INT}hr\"/" \
            | sed "s/CAT_THR/cat_thresh = ${CAT_THR}/" \
            | sed "/PLY_MSK/r ${work_root}/PLY_MSK.txt" \
            | sed "/PLY_MSK/d " \
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
        printf "${cmd}\n"; eval ${cmd}
        
      else
        msg="Observation verification file\n ${DATA_ROOT}/${obs_f_in}\n is not "
        msg+=" readable or does not exist, skipping grid_stat for forecast "
        msg+="initialization ${dirstr}, forecast hour ${lead_hr}.\n"
        printf ${msg}
      fi

    else
      msg="gridstat input file\n ${work_root}/${prfx}${for_f_in}\n is not readable " 
      msg+=" or does not exist, skipping grid_stat for forecast initialization "
      msg+="${dirstr}, forecast hour ${lead_hr}.\n"
      printf ${msg}
    fi

    # End MET Process and singularity stop
    cmd="singularity instance stop met1"
    printf "${cmd}\n"; eval ${cmd}

    # clean up working directory from accumulation time
    cmd="rm -f ${work_root}/${prfx}${for_f_in}"
    printf "${cmd}\n"; eval ${cmd}
  done

  # clean up working directory from forecast start time
  cmd="rm -f ${work_root}/*regridded_with_StageIV.nc"
  printf "${cmd}\n"; eval ${cmd}

  cmd="rm -f ${work_root}/PLY_MSK.txt"
  printf "${cmd}\n"; eval ${cmd}
done

msg="Script completed at `date +%Y-%m-%d_%H_%M_%S`, verify "
msg+="outputs at OUT_CYC_DIR:\n ${OUT_CYC_DIR}"
printf ${msg}

#################################################################################
# end

exit 0
