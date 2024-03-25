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
CSE = '2023021818_cycle_start'

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
            "nghido_letkf_OIE60km_WarmStart_aro_01.02"
	"nghido_letkf_OIE60km_WarmStart_ctrl_01.01"
           ]

# ensemble member indices, used for ISO date sub-directory nesting, set based on
# directory structure for MET outputs
MEM_IDS = ['']
MEM_IDS += ['mean']

# verification domains to process, used for ensemble member sub-directory nesting
GRDS = [
        ''
       ]

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2023021900'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
STOP_DT = '2023022000'

# increment between zero hours for forecast data (string HH)
CYC_INC = '12'

# Min forecast lead time to proces in hours (string HH)
ANL_MIN = '24'

# Max forecast lead time to plot in hours (string HH)
ANL_MAX = '168'

# incrment between verification valid times (string HH)
ANL_INC = '24'

# Compute precipitation accumulation, True or False
CMP_ACC=True

# Defines the min / max accumulation interval for precip (string HH)
ACC_MIN='24'
ACC_MAX='24'

# Defines the increment between min / max to compute accumulation intervals (string HH)
ACC_INC='24'
