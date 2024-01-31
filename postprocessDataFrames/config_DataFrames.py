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
USR_HME = os.environ['USR_HME']
VRF_ROOT = os.environ['VRF_ROOT']
INDT = os.environ['INDT']

##################################################################################
# DATAFRAME PARAMETERS
##################################################################################
# Case study directory structure
CSE = 'DeepDive/2022122800_valid_date'

# MET-tool subdirectory name
MET_TOOL = 'GridStat'

# Prefix for MET product outputs
PRFX = 'grid_stat_QPF'

# root directory for ASCII outputs
IN_ROOT = VRF_ROOT + '/' + CSE

# root directory for processed pandas outputs
OUT_ROOT = VRF_ROOT + '/' + CSE

# define control flows to analyze for lineplots 
CTR_FLWS = [
            'WRF',
            'MPAS',
            'GFS',
            'GEFS',
            'ECMWF',
           ]

# ensemble member indices, used for ISO date sub-directory nesting, set based on
# directory structure for MET outputs
MEM_IDS = ['']
MEM_IDS += ['mean']
for i_m in range(0,6):
    MEM_IDS += ['ens_' + str(i_m).zfill(2)]

# verification domains to process, used for ensemble member sub-directory nesting
GRDS = [
        '',
        'd01',
        'd02',
       ]

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2022122300'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
STOP_DT = '2022122700'

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
