##################################################################################
# Description
##################################################################################
#
##################################################################################
# Imports
##################################################################################
import sys

##################################################################################

class ctr_flw:
    def __init__(self, name, grds=None, mem_ids=None):
        if not type(name) == str or len(name) == 0:
            print('ERROR: control flow name is not a string or is of zero' +\
                  ' length.')
            sys.exit(1)
        else:
            self.name = name

        if grds:
            if not type(grds) == list or len(grds) == 0 :
                print('ERROR: domain list "grds" is not a list or it is' +\
                      ' empty, it should be defined as a list of string' +\
                      ' names of sub-domains to process. String name can be' +\
                      ' empty if unused.')
            elif not all([isinstance(val, str) for val in grds]):
                print('ERROR: not all values of "grds" list are strings, it' +\
                      ' should be defined as a list of string names of' +\
                      ' sub-domains to process. String name can be empty if' +\
                      ' unused.')
                sys.exit(1)
            else:
                self.grds = grds

        if mem_ids:
            if not type(mem_ids) == list or len(mem_ids) == 0 :
                print('ERROR: member list "mem_ids" is not a list or it is' +\
                      ' empty, it should be defined as a list of string' +\
                      ' names of sub-domains to process. String name can be' +\
                      ' empty if unused.')
            elif not all([isinstance(val, str) for val in mem_ids]):
                print('ERROR: not all values of "mem_ids" list are strings,' +\
                      ' it should be defined as a list of string names of' +\
                      ' sub-domains to process. String name can be empty if' +\
                      ' unused.')
                sys.exit(1)
            else:
                self.mem_ids = mem_ids

QPE_TITLE = 'Stage-IV' # QPE source, for plot title

# MET stat file type - should be non-leveled data
TYPE = 'cnt'

# MET stat column names to be made to heat plots / labels
STATS = ['RMSE', 'PR_CORR']

# define control flows to analyze for lineplots 
CTR_FLWS = [
            'NRT_ECMWF',
            'NRT_GFS',
            'ECMWF',
            'GEFS',
            'GFS',
           ]

# Land mask for verification
MSK = 'CA_All'

DMN_TITLE = 'California' # title to plot name of landmask/domain

##################################################################################
# PlOT RENDERING PARAMETERS
##################################################################################
# List of indices for the underscore-separated components of control flow name
# to use in the plot legend
LAB_IDX = [0, 1]

# Include ensemble index in legend label True or False
ENS_LAB = False

# Include model grid in legend label True or False
GRD_LAB = True

# Plot title generated from above parameters
TITLE='24hr Accumulated Precipitation\n' + 'Valid: ' +\
        VALID_DT[8:] + 'Z ' + VALID_DT[4:6] + '/' + VALID_DT[6:8] + '/' + VALID_DT[:4]

# Plot subtitles
DMN_SUBTITLE = 'Domain: ' + DMN_TITLE
QPE_SUBTITLE = 'QPE Source: ' + QPE_TITLE

# path of saved figure
OUT_PATH = OUT_ROOT + '/' + VALID_DT + '_' + MSK + '_' + STATS[0] + '_' +\
           STATS[1] + fig_lab + '_lineplot.png'

##################################################################################
