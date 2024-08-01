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

QPE_SOURCE = 'Stage-IV' # source, for plot title

# MET stat file type - should be non-leveled data
TYPE = 'nbrcnt'

# MET stat column names to be made to heat plots / labels
STAT = 'FSS'

# define control flows to analyze for lineplots 
CTR_FLW = 'NRT_GFS'

# ensemble member indices to plot
MEM = 'mean'

# verification domains to plot - defined as empty string if not needed
GRD = 'd02'

# valid date for verification (string YYYYMMDDHH)
VLD_DT = '2024011400'

# increment between zero hours for forecast data (string HH)
CYC_INC = '24'

# Max forecast lead hours
MAX_LD = '120'

# Land mask for verification
MSK = 'CA_All'
DMN_TITLE = 'California' # title for domain/landmask for plot

##################################################################################
# PlOT RENDERING PARAMETERS
##################################################################################
# List of indices for the underscore-separated components of control flow name
# to use in the plot title
LAB_IDX = [0, 1]

# Include ensemble index in plot title True or False
ENS_LAB = False

# Include model grid in plot title True or False
GRD_LAB = True

# Plot title generated from above parameters
if STAT == 'FSS':
    stat_title = 'Fraction Skill Score'
elif STAT == 'AFSS':
    stat_title = 'Asymptotic Fractions Skill Score'
else:
    stat_title = STAT

TITLE = stat_title + ' - '

split_string = CTR_FLW.split('_')
split_len = len(split_string)
idx_len = len(LAB_IDX)
line_lab = ''
lab_len = min(idx_len, split_len)

if lab_len == 2:
    TITLE += 'West-WRF/' + split_string[1]

elif lab_len > 1:
    for i_ll in range(lab_len, 1, -1):
        i_li = LAB_IDX[-i_ll]
        TITLE += split_string[i_li] + '_'

    i_li = LAB_IDX[-1]
    TITLE += split_string[i_li]

else:
    TITLE += split_string[0]

if len(MEM) > 0:
    ens = MEM
else:
    ens = ''

if GRD == 'd01':
    grd = '9km'
elif GRD == 'd02':
    grd = '3km'
elif GRD == 'd03':
    grd = '1km'
else:
    grd = ''

if ENS_LAB:
    TITLE += ' ' + ens

if GRD_LAB:
    TITLE += ' ' + grd

# plot subtitles
DMN_SUBTITLE = 'Domain: ' + DMN_TITLE
QPE_SUBTITLE = 'QPE Source: ' + QPE_SOURCE
VDT_SUBTITLE = 'Valid: ' + VLD_DT[8:10] + 'Z ' + VLD_DT[4:6] +\
        '/' + VLD_DT[6:8] + '/' + VLD_DT[:4]


# Bool switch for choosing color bar scale
DYN_SCL = False

# If DYN_SCL is True:
#    set the heat map scale dynamically based on inner 100 - ALPHA range of data
ALPHA = 1

# If DYN_SCL is False:
#    set the heat map scale dynamically based on MIN_SCALE / MAX_SCALE below
MIN_SCALE = 0
MAX_SCALE = 1

# define color map to be used for heat plot color bar
COLOR_MAP = sns.color_palette('flare', as_cmap=True)

##################################################################################
# I/O PARAMETERS
##################################################################################
# Case study directory structure for input data
CSE = '2024010300_valid_date'

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
           '_' + MSK + '_' + STAT + '_' + CTR_FLW + '_' + GRD + fig_lab +\
	       '_all-level_heatplot_REVISED.png'

##################################################################################
