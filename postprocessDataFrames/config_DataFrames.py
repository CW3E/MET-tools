##################################################################################
# Description
##################################################################################
# This configuration file is for settings related to parsing MET outputs into
# Python dataframes for the MET-tools workflow.
#
##################################################################################
# SOURCE GLOBAL PARAMETERS
##################################################################################
import os
INDT = os.environ['INDT']

##################################################################################
# DATAFRAME PARAMETERS
##################################################################################
# Case study directory structure
CSE = '2024010300_valid_date'

# MET-tool subdirectory name
MET_TOOL = 'GridStat'

# Prefix for MET product outputs
PRFX = 'grid_stat_QPF'

# root directory for ASCII outputs (singularity bind /in_root)
IN_ROOT = '/in_root/' + CSE

# root directory for processed pandas outputs (singularity bind /out_root)
OUT_ROOT = '/out_root/' + CSE

# define control flows to analyze for lineplots 
CTR_FLWS = [
            'NRT_ECMWF',
            'NRT_GFS',
            'ECMWF',
            'GEFS',
            'GFS',
           ]

# ensemble member indices, used for ISO date sub-directory nesting, set based on
# directory structure for MET outputs
MEM_IDS = ['']
MEM_IDS += ['mean']
for i_m in range(0,3):
    MEM_IDS += ['ens_' + str(i_m).zfill(2)]

# verification domains to process, used for ensemble member sub-directory nesting
GRDS = [
        '',
        'd01',
        'd02',
        'd03',
       ]

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2024010300'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
STOP_DT = '2024012400'

# increment between zero hours for forecast data (string HH)
CYC_INC = '24'

# Min forecast lead time to proces in hours (string HH)
ANL_MIN = '24'

# Max forecast lead time to plot in hours (string HH)
ANL_MAX = '120'

# incrment between verification valid times (string HH)
ANL_INC = '24'

# Compute precipitation accumulation, True or False
CMP_ACC=True

# Defines the min / max accumulation interval for precip (string HH)
ACC_MIN='24'
ACC_MAX='24'

# Defines the increment between min / max to compute accumulation intervals (string HH)
ACC_INC='24'
