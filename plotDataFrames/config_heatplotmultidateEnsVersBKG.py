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

QPE_SOURCE = 'Stage-IV'

# MET stat file type - should be non-leveled data
TYPE = 'cnt'

# MET stat column names to be made to heat plots / labels
STAT = 'RMSE'

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

# starting valid date for verification (string YYYYMMDDHH)
ANL_STRT = '2022122400'

# end valid date for verification (string YYYYMMDDHH)
ANL_STOP = '2022122800'

# increment between verification valid dates (string HH)
ANL_INC = '24'

# Max forecast lead hours
MAX_LD = '120'

# increment between zero hours for forecast data (string HH)
CYC_INC = '24'

# Land mask for verification
MSK = 'CA_All'

DMN_TITLE = 'California'

##################################################################################
# PlOT RENDERING PARAMETERS
##################################################################################
# List of indices for the underscore-separated components of control flow name
# to use in the plot title
ANL_LAB_IDX = [0, 2]
REF_LAB_IDX = [0]

# Include ensemble index in plot title True or False
ANL_ENS_LAB = False
REF_ENS_LAB = False

# Include model grid in plot title True or False
ANL_GRD_LAB = True
REF_GRD_LAB = False

# Plot title generated from above parameters
if STAT == 'RMSE':
    stat_title = 'Root-Mean-Squared Error (mm)'
elif STAT == 'PR_CORR':
    stat_title = 'Pearson Correlation Coefficient'
else:
    stat_title = ''

TITLE = stat_title

split_string = ANL_CFG.split('_')
split_len = len(split_string)
idx_len = len(ANL_LAB_IDX)
line_lab = ''
lab_len = min(idx_len, split_len)

if lab_len == 2:
    TITLE += '\nWest-WRF/' + split_string[1]

elif lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        i_li = ANL_LAB_IDX[-i_ll]
        TITLE += split_string[i_li] + '_'

    i_li = ANL_LAB_IDX[-1]
    TITLE += split_string[i_li]

else:
    TITLE += split_string[0]

if len(ANL_MEM) > 0:
    anl_ens = ANL_MEM
else:
    anl_ens = ''

if ANL_GRD == 'd01':
    anl_grd = '9km'
elif ANL_GRD == 'd02':
    anl_grd = '3km'
elif ANL_GRD == 'd03':
    anl_grd = '1km'
    anl_ens = '_' + ANL_MEM
else:
    anl_ens = ''

if len(ANL_GRD) > 0:
    anl_grd = '_' + ANL_GRD

else:
    anl_grd = ''

if ANL_ENS_LAB:
    TITLE += ' ' + anl_ens

if ANL_GRD_LAB:
    TITLE += ' ' + anl_grd

TITLE += ' Relative Difference From '
    TITLE += anl_ens

if ANL_GRD_LAB:
    TITLE += anl_grd

TITLE += ' relative difference from '

split_string = REF_CFG.split('_')
split_len = len(split_string)
idx_len = len(REF_LAB_IDX)
line_lab = ''
lab_len = min(idx_len, split_len)

if lab_len ==2:
    TITLE += '\nWest-WRF/' + split_string[1]

elif lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        i_li = REF_LAB_IDX[-i_ll]
        TITLE += split_string[i_li] + '_'

    i_li = REF_LAB_IDX[-1]
    TITLE += split_string[i_li]

else:
    TITLE += split_string[0]

if len(REF_MEM) > 0:
    ref_ens = REF_MEM
else:
    ref_ens = ''

if REF_GRD == 'd01':
    ref_grd = '9km'
elif REF_GRD == 'd02':
    ref_grd = '3km'
elif REF_GRD == 'd03':
    ref_grd = '1km'
else:
    ref_grd = ''

if REF_ENS_LAB:
    TITLE += ' ' + ref_ens

if REF_GRD_LAB:
    TITLE += ' ' + ref_grd

DMN_SUBTITLE = 'Domain: ' + DMN_TITLE
QPE_SUBTITLE = 'QPE Source: ' + QPE_SOURCE

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
#COLOR_MAP = sns.diverging_palette(220, 20, as_cmap=True)

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

OUT_PATH = OUT_ROOT + '/' + ANL_STRT + '-to-' + ANL_STOP + '_FCST-' + MAX_LD +\
           '_' + MSK + '_' + STAT + '_' + ANL_CFG + '_' + anl_grd + anl_ens +\
           '_relative_difference_' + REF_CFG + '_' + ref_grd + ref_ens +\
           fig_lab + '_heatplot.png'

##################################################################################
