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
VRF_ROOT = os.environ['VRF_ROOT']
IF_SING = os.environ['IF_SING']

##################################################################################
# WORKFLOW PARAMETERS
##################################################################################
# MET-tool subdirectory name
MET_TOOL = 'GridStat'

# Prefix for MET product outputs
PRFX = 'grid_stat_QPF_24hr'

# MET stat file type - should be leveled data
TYPE = 'nbrcnt'

# MET stat column names to be made to heat plots / labels
STATS = ['FSS', 'AFSS']

# threshold value for leveled data plot
LEV = '>=50.0'

# define control flows to analyze for lineplots 
CTR_FLWS = [
            'nghido_letkf_OIE60km_WarmStart_ctrl_01.01',
            'nghido_letkf_OIE60km_WarmStart_aro_01.02'
           ]

# ensemble member indices to plot, searches matching patterns
MEM_IDS = ['']
MEM_IDS += ['mean']

#for i_m in range(0,6):
#    MEM_IDS += ['ens_' + str(i_m).zfill(2)]

# verification domains to plot, searches matching patterns, supply empty string
# if not needed
GRDS = [
        ''
       ]

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2022122300'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
STOP_DT = '2022122700'

# increment between zero hours for forecast data (string HH)
CYC_INC = '24'

# Verification valid date
VALID_DT = '2022122800'

# Land mask for verification
MSK = 'CA_All'

##################################################################################
# PlOT RENDERING PARAMETERS
##################################################################################
# List of indices for the underscore-separated components of control flow name
# to use in the plot legend
LAB_IDX = [0, 2]

# Include ensemble index in legend label True or False
ENS_LAB = False

# Include model grid in legend label True or False
GRD_LAB = True

# Plot title generated from above parameters
TITLE='24hr accumulated precip at ' + VALID_DT[:4] + '-' + VALID_DT[4:6] + '-' +\
        VALID_DT[6:8] + '_' + VALID_DT[8:]

# Plot sub-title title generated from the land mask file name
SUBTITLE='Verification region -'
lnd_msk_split = MSK.split('_')
for split in lnd_msk_split:
    SUBTITLE += ' ' + split

SUBTITLE += ', Threshold ' + LEV + ' mm'

##################################################################################
# I/O PARAMETERS
##################################################################################
# Case study directory structure for input data
CSE = 'DeepDive/2022122800_valid_date'

# saved figure path case study subdirectory
FIG_CSE = ''

# figure label string to be included in auto-generated path name
FIG_LAB = 'ENS_V_BKG'

# fig saved automatically to OUT_PATH
if len(FIG_LAB) > 0:
    fig_lab = '_' + FIG_LAB
else:
    fig_lab = ''

# root directory of pickled dataframe binaries, switch for singularity vs conda
if IF_SING == 'TRUE':
    IN_ROOT = '/in_root/' + CSE
else:
    IN_ROOT = VRF_ROOT + '/' + CSE

# root directory of figure outputs, switch for singularity vs conda
if IF_SING == 'TRUE':
    OUT_ROOT = '/out_root/' + CSE + '/figures/' + FIG_CSE
else:
    OUT_ROOT = VRF_ROOT + '/' + CSE + '/figures/' + FIG_CSE

# path of saved figure
OUT_PATH = OUT_ROOT + '/' + VALID_DT + '_' + MSK + '_' + STATS[0] + '_' +\
           STATS[1] + '_lev_' + LEV + fig_lab + '_lineplot.png'

##################################################################################
