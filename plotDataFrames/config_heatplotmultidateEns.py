##################################################################################
# Description
##################################################################################
#
##################################################################################
# SOURCE GLOBAL PARAMETERS
##################################################################################
import os
import seaborn as sns
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

# MET stat file type - should be non-leveled data
TYPE = 'cnt'

# MET stat column names to be made to heat plots / labels
STAT = 'RMSE'

# define control flows to analyze for lineplots 
CTR_FLW = 'nghido_letkf_OIE60km_WarmStart_aro_01.02'

# ensemble member indices to plot
MEM = 'mean'

# verification domains to plot - defined as empty string if not needed
GRD = ''

# starting valid date for verification (string YYYYMMDDHH)
ANL_STRT = '2023022112'

# end valid date for verification (string YYYYMMDDHH)
ANL_STOP = '2023022412'

# increment between verification valid dates (string HH)
ANL_INC = '12'

# Max forecast lead hours
MAX_LD = '168'

# increment between zero hours for forecast data (string HH)
CYC_INC = '12'

# Land mask for verification
MSK = 'CA_All'

##################################################################################
# PlOT RENDERING PARAMETERS
##################################################################################
# List of indices for the underscore-separated components of control flow name
# to use in the plot title
LAB_IDX = [1, 2,3,4]

# Include ensemble index in plot title True or False
ENS_LAB = True

# Include model grid in plot title True or False
GRD_LAB = False

# Plot title generated from above parameters
TITLE = STAT + ' - '
split_string = CTR_FLW.split('_')
split_len = len(split_string)
idx_len = len(LAB_IDX)
line_lab = ''
lab_len = min(idx_len, split_len)
if lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        i_li = LAB_IDX[-i_ll]
        TITLE += split_string[i_li] + '_'

    i_li = LAB_IDX[-1]
    TITLE += split_string[i_li]

else:
    TITLE += split_string[0]

if len(MEM) > 0:
    ens = '_' + MEM
else:
    ens = ''

if len(GRD) > 0:
    grd = '_' + GRD

else:
    grd = ''

if ENS_LAB:
    TITLE += ens

if GRD_LAB:
    TITLE += grd

lnd_msk_split = MSK.split('_')
SUBTITLE = 'Verification Region -'
for split in lnd_msk_split:
    SUBTITLE += ' ' + split

# Bool switch for choosing color bar scale
DYN_SCL = True

# If DYN_SCL is True:
#    set the heat map scale dynamically based on inner 100 - ALPHA range of data
ALPHA = 1

# If DYN_SCL is False:
#    set the heat map scale dynamically based on MIN_SCALE / MAX_SCALE below
MIN_SCALE = 0
MAX_SCALE = 1

# define color map to be used for heat plot color bar
COLOR_MAP = sns.color_palette('viridis', as_cmap=True)

##################################################################################
# I/O PARAMETERS
##################################################################################
# Case study directory structure for input data
CSE = '2023021818_cycle_start'

# figure case study nesting
FIG_CSE = ''

# figure label to be included in autosaved path
FIG_LAB = 'ENS'

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

# fig saved automatically to OUT_PATH
if len(FIG_LAB) > 0:
    fig_lab = '_' + FIG_LAB
else:
    fig_lab = ''

OUT_PATH = OUT_ROOT + '/' + ANL_STRT + '-to-' + ANL_STOP + '_FCST-' + MAX_LD +\
           '_' + MSK + '_' + STAT + '_' + CTR_FLW + grd + fig_lab +\
	       '_heatplot.png'

##################################################################################
