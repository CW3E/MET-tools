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
# PLOTTING PARAMETERS
##################################################################################
# MET stat file type - should be leveled data
TYPE = 'nbrcnt'

# MET stat column names to be made to heat plots / labels
STATS = ['FSS', 'AFSS']

# Case study directory structure for input data
CSE = 'DeepDive/2022122800_valid_date'

# figure case study nesting
FIG_CSE = ''

# figure label to be included in autosaved path
FIG_LAB = 'ENS_V_BKG'

# MET-tool subdirectory name
MET_TOOL = 'GridStat'

# Prefix for MET product outputs
PRFX = 'grid_stat_QPF_24hr'

# Land mask for verification
MSK = 'CA_All'

##################################################################################
# I/O PARAMETERS
##################################################################################
# root directory of figure outputs
OUT_ROOT = '/out_root/' + CSE + '/figures' + FIG_CSE

# fig saved automatically to OUT_PATH
if len(FIG_LAB) > 0:
    fig_lab = '_' + FIG_LAB
else:
    fig_lab = ''

# define control flows to analyze for lineplots 
CTR_FLWS = [
            'WRF',
            'MPAS',
            'GFS',
            'GEFS',
            'ECMWF',
           ]

# Legend label, indices of underscore components of control flow name to use
LAB_IDX = [0]

# ensemble member indices to plot
MEM_IDS = ['']
MEM_IDS += ['mean']

#for i_m in range(0,6):
#    MEM_IDS += ['ens_' + str(i_m).zfill(2)]

# include ensemble index in legend label True or False
ENS_LAB = False

# verification domains to plot
GRDS = [
        '',
        'd01',
        'd02',
       ]

# threshold value for leveled data plot
LEV = '>=100.0'

# include model grid in legend label True or False
GRD_LAB = True

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
STRT_DT = '2022122300'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
STOP_DT = '2022122700'

# increment between zero hours for forecast data (string HH)
CYC_INC = '24'

# Verification valid date
VALID_DT = '2022122800'

# plot title
TITLE='24hr accumulated precip at ' + VALID_DT[:4] + '-' + VALID_DT[4:6] + '-' +\
        VALID_DT[6:8] + '_' + VALID_DT[8:]

# plot sub-title title
SUBTITLE='Verification region -'
lnd_msk_split = MSK.split('_')
for split in lnd_msk_split:
    SUBTITLE += ' ' + split

SUBTITLE += ', Threshold ' + LEV + ' mm'

OUT_PATH = OUT_ROOT + '/' + VALID_DT + '_' + MSK + '_' + STATS[0] + '_' +\
           STATS[1] + '_lev_' + LEV + fig_lab + '_lineplot.png'

# root directory of pickled dataframe binaries
IN_ROOT = '/in_root/' + CSE
