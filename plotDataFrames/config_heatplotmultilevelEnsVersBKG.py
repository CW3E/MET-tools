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
TYPE = 'nbrcnt'

# MET stat column names to be made to heat plots / labels
STAT = 'FSS'

# define configuration to analyze
ANL_CFG = 'WRF_9-3_WestCoast'

# define the refence configuration to produce the relative difference statistic
REF_CFG = 'GEFS'

# analyzed ensemble member indices to plot
ANL_MEM = 'mean'

# reference ensemble member indices to plot
REF_MEM = ''

# analyzed config verification domain - defined as empty string if not needed
ANL_GRD = 'd02'

# reference config verification domain - defined as empty string if not needed
REF_GRD = ''

# valid date for verification (string YYYYMMDDHH)
VLD_DT = '2022122800'

# increment between zero hours for forecast data (string HH)
CYC_INC = '24'

# Max forecast lead hours
MAX_LD = '120'

# Land mask for verification
MSK = 'CA_All'

##################################################################################
# PlOT RENDERING PARAMETERS
##################################################################################
# List of indices for the underscore-separated components of control flow name
# to use in the plot title
ANL_LAB_IDX = [0]
REF_LAB_IDX = [0]

# Include ensemble index in plot title True or False
ANL_ENS_LAB = False
REF_ENS_LAB = False

# Include model grid in plot title True or False
ANL_GRD_LAB = True
REF_GRD_LAB = False

# Plot title generated from above parameters
TITLE = STAT + ' - '
split_string = ANL_CFG.split('_')
split_len = len(split_string)
idx_len = len(ANL_LAB_IDX)
line_lab = ''
lab_len = min(idx_len, split_len)
if lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        i_li = ANL_LAB_IDX[-i_ll]
        TITLE += split_string[i_li] + '_'

    i_li = ANL_LAB_IDX[-1]
    TITLE += split_string[i_li]

else:
    TITLE += split_string[0]

if len(ANL_MEM) > 0:
    anl_ens = '_' + ANL_MEM
else:
    anl_ens = ''

if len(ANL_GRD) > 0:
    anl_grd = '_' + ANL_GRD

else:
    anl_grd = ''

if ANL_ENS_LAB:
    TITLE += anl_ens

if ANL_GRD_LAB:
    TITLE += anl_grd

TITLE += ' relative difference from '

split_string = REF_CFG.split('_')
split_len = len(split_string)
idx_len = len(REF_LAB_IDX)
line_lab = ''
lab_len = min(idx_len, split_len)
if lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        i_li = REF_LAB_IDX[-i_ll]
        TITLE += split_string[i_li] + '_'

    i_li = REF_LAB_IDX[-1]
    TITLE += split_string[i_li]

else:
    TITLE += split_string[0]

if len(REF_MEM) > 0:
    ref_ens = '_' + REF_MEM
else:
    ref_ens = ''

if len(REF_GRD) > 0:
    ref_grd = '_' + REF_GRD

else:
    ref_grd = ''

if REF_ENS_LAB:
    TITLE += ref_ens

if REF_GRD_LAB:
    TITLE += ref_grd

SUBTITLE = 'Valid date ' + VLD_DT[:4] + '-' + VLD_DT[4:6] +\
        '-' + VLD_DT[6:8] + '_' + VLD_DT[8:10]
lnd_msk_split = MSK.split('_')
SUBTITLE += ', Verification Region -'
for split in lnd_msk_split:
    SUBTITLE += ' ' + split

# Bool switch for choosing color bar scale
DYN_SCL = True

# If DYN_SCL is True:
#    set the heat map scale dynamically based on inner 100 - ALPHA range of data
ALPHA = 1

# If DYN_SCL is False:
#    set the heat map scale dynamically based on MIN_SCALE / MAX_SCALE below
MIN_SCALE = -1
MAX_SCALE = 1

# define color map to be used for heat plot color bar
COLOR_MAP = sns.diverging_palette(145, 300, s=60, as_cmap=True)
COLOR_MAP.set_bad('gray')

##################################################################################
# I/O PARAMETERS
##################################################################################
# Case study directory structure for input data
CSE = '2022122800_valid_date'

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

OUT_PATH = OUT_ROOT + '/' + VLD_DT + '_FCST-' + MAX_LD +\
           '_' + MSK + '_' + STAT + '_' + ANL_CFG + anl_grd + anl_ens + fig_lab +\
           '_relative_difference_' + REF_CFG + ref_grd + ref_ens +\
	       '_all-level_heatplot.png'

##################################################################################
