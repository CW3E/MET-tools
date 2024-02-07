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
CTR_FLW = 'MPAS'

# ensemble member indices to plot
MEM = 'mean'

# verification domains to plot - defined as empty string if not needed
GRD = ''

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2022122300'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
STOP_DT = '2022122700'

# increment between zero hours for forecast data (string HH)
CYC_INC = '24'

# Max forecast lead to include
MAX_LD = '120'

# Land mask for verification
MSK = 'CA_All'

##################################################################################
# PlOT RENDERING PARAMETERS
##################################################################################
# List of indices for the underscore-separated components of control flow name
# to use in the plot title
LAB_IDX = [0]

# Include ensemble index in plot title True or False
ENS_LAB = False

# Include model grid in plot title True or False
GRD_LAB = True

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

if len(GRD) > 0:
    grd = '_' + GRD

else:
    grd = ''

if GRD_LAB:
    TITLE += grd

lnd_msk_split = MSK.split('_')
TITLE += ', Verification Region -'
for split in lnd_msk_split:
    TITLE += ' ' + split

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
CSE = 'DeepDive/2022122800_valid_date'

# root directory of pickled dataframe binaries
IN_ROOT = '/in_root/' + CSE

# figure case study nesting
FIG_CSE = ''

# figure label to be included in autosaved path
FIG_LAB = 'ENS'

# root directory of figure outputs
OUT_ROOT = '/out_root/' + CSE + '/figures/' + FIG_CSE

# fig saved automatically to OUT_PATH
if len(FIG_LAB) > 0:
    fig_lab = '_' + FIG_LAB
else:
    fig_lab = ''

OUT_PATH = OUT_ROOT + '/' + STRT_DT + '-to-' + STOP_DT + '_FCST-' + MAX_LD + '_' +\
           MSK + '_' + STAT + '_' + CTR_FLW + grd + fig_lab +\
	       '_heatplot.png'

##################################################################################
