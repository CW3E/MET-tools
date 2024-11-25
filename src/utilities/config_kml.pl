#!/usr/bin/perl
##################################################################################
# Description
##################################################################################
# This configuration file is for the conversion of a KML file to a MET
# formatted text file polygon. This script is adapted from original source code
# provided by Matthew Simpson. 
#
# TBD: Currently a Perl script. Once/if converted to a Shell script, many of
# these pathways can be sourced from config_workflow.sh. 
##################################################################################
# KML to MET Polygon Parameters
##################################################################################

# Root directory for MET-tools git clone
$USR_HOME = '/expanse/nfs/cw3e/cwp168/MET-tools'; # TBD: not needed if converted to shell

# Root directory for landmasks, lat-lon files, kml files, and reference grids 
$MSK_ROOT = "$USR_HOME/settings/mask-root"; # TBD

# Path to lat-lon text files for mask generation
$MSK_LTLN = "$MSK_ROOT/lat-lon"; # TBD

# Verification region name
$VRF_RGN = 'OR_CA'; # should be of the form 'Mask_Name'

# Path to KML input file
$KML_IN = "$MSK_ROOT/kml_files/$VRF_RGN.kml";
