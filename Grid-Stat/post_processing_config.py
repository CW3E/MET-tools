##################################################################################
# Description
##################################################################################
# This configuration file is for the post-processing section of the MET-tools
# workflow. These environmental variables are defined for the python scripts in
# the MET-tools directory. 
#
##################################################################################
# GLOBAL PARAMETERS TO BE SET BY THE USER
##################################################################################

# define control flow to analyze for heatmaps 
CTR_FLW = 'NRT_gfs'

# define control flows to analyze for lineplots 
CTR_FLWS = [
            'NRT_gfs',
            'NRT_ecmwf',
            'GFS',
            'ECMWF',
           ]

# Define a list of indices for underscore-separated components of control flow
# names to include in fig legend. Note: a non-empty prefix value below will
# always be included in the legend label, and control flows with fewer components
# than indices above will only include those label components that exist
LAB_IDX = [0, 1]

# verification domain for the forecast data for heatmaps
GRD = 'd01'

# verification domains for the forecast data for lineplots
GRDS = [
        'd01',
        'd02',
        'd03',
        '',
       ]

# starting date and zero hour of forecast cycles (string YYYYMMDDHH)
# defined for the purposes of post-processing ASCII and binary files
STRT_DT = '2022121400'

# final date and zero hour of data of forecast cycles (string YYYYMMDDHH)
# defined for the purposes of post-processing ASCII and binary files
END_DT = '2023011800'

# first valid time for verification (string YYYYMMDDHH)
# defined for plotting of heatmaps
ANL_STRT = '2022123000'

# final valid time (string YYYYMMDDHH)
# defined for plotting of heatmaps
ANL_END = '2023010200'

# valid date for the verification
# defined for the plotting of lineplots
VALID_DT = '2022122900'

# define the case-wise sub-directory
CSE = 'jlconti'

# fig label for output file organization, included in figure file name
FIG_LAB = 'case_study'

# fig case directory, includes leading '/', leave as empty string if not needed
FIG_CSE = '/Case_Study/Bay_Area'

# landmask for verification region -- needs to be set in gridstat options
LND_MSK = 'San_Francisco_Bay'

# precipitation threshold level to plot the FSS/AFSS metric
LEV = '>=50.0'

##################################################################################
# GLOBAL PARAMETERS THAT MAY NEED TO CHANGE
##################################################################################

# define if legend label includes grid
GRD_LAB = True

# define optional gridstat prefix for heatmaps, include empty string to ignore
PRFX = ''

# define optional list of stats files prefixes for lineplots, include empty string to ignore
PRFXS = [
        '',
        ]

# Max forecast lead time to plot in hours
MAX_LD = '240'

# number of hours between zero hours for forecast data (string HH)
CYC_INT = '24'

# cycle interval verification valid times (string HH)
ANL_INT = '24'

# use dynamic color bar scale depending on data percentiles, True / False
# Use this as True by default unless specifying a specific color bar scale and
# scheme in the below
DYN_SCL = True

# these values will only be used if the DYN_SCL above is set to False
MIN_SCALE = 0.0
MAX_SCALE = 1.0

##################################################################################
# GLOBAL PARAMETERS THAT PROBABLY WON'T NEED TO CHANGE
################################################################################## 

