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

##################################################################################
