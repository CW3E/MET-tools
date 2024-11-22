#!/usr/bin/perl
system(clear);
#################################################################################
# Description
#################################################################################
# The purpose of this script is to read in a KML formatted file and convert 
# geographic data to a MET software-combatible polygon text file. This script
# also generates the MaskList text file with a list of the landmasks generated 
# for the custom verification region. This script is based on the original 
# source code provided by Matthew Simpson.
#
#
#################################################################################
# License Statement:
#################################################################################
# This software is Copyright © 2024 The Regents of the University of California.
# All Rights Reserved. Permission to copy, modify, and distribute this software
# and its documentation for educational, research and non-profit purposes,
# without fee, and without a written agreement is hereby granted, provided that
# the above copyright notice, this paragraph and the following three paragraphs
# appear in all copies. Permission to make commercial use of this software may
# be obtained by contacting:
#
#     Office of Innovation and Commercialization
#     9500 Gilman Drive, Mail Code 0910
#     University of California
#     La Jolla, CA 92093-0910
#     innovation@ucsd.edu
#
# This software program and documentation are copyrighted by The Regents of the
# University of California. The software program and documentation are supplied
# "as is", without any accompanying services from The Regents. The Regents does
# not warrant that the operation of the program will be uninterrupted or
# error-free. The end-user understands that the program was developed for
# research purposes and is advised not to rely exclusively on the program for
# any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF CALIFORNIA BE LIABLE TO ANY PARTY FOR
# DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING
# LOST PROFITS, ARISING OUT OF THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION,
# EVEN IF THE UNIVERSITY OF CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE. THE UNIVERSITY OF CALIFORNIA SPECIFICALLY DISCLAIMS ANY
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE SOFTWARE PROVIDED
# HEREUNDER IS ON AN “AS IS” BASIS, AND THE UNIVERSITY OF CALIFORNIA HAS NO
# OBLIGATIONS TO PROVIDE MAINTENANCE, SUPPORT, UPDATES, ENHANCEMENTS, OR
# MODIFICATIONS.
#
#
#################################################################################
# SOURCE PARAMETERS
#################################################################################

do './config_kml.pl';

#################################################################################
# CHECK WORKFLOW PARAMETERS
#################################################################################

if (! defined $USR_HOME) {die "ERROR: USR_HOME is not defined! $!"};
if (! defined $MSK_ROOT) {die "ERROR: MSK_ROOT is not defined! $!"};
if (! defined $MSK_LTLN) {die "ERROR: MSK_LTLN is not defined! $!"};
if (! defined $VRF_RGN) {die "ERROR: VRF_RGN is not defined! $!"};
if (! defined $KML_IN) {die "ERROR: KML_IN is not defined! $!"};

#################################################################################
# GENERATE MET POLYGON FILE(S)
#################################################################################

# Open KML file to read  
  open(FILE,'<',$KML_IN) or die "Cannot open '$KML_IN': $!";

# Loop through data lines of KML file
  while ($line=<FILE>) {
      chomp($line);
      $line =~ s/^\s*(.*?)\s*$/$1/;

    # Geographic data read
      if($line eq '<coordinates>') {
	  $N++;
	  if(length($N) == 1) {$N="0$N"}
	  print "PROCESSING POLYGON #$N\n";
	  
	# Open MET formatted text output file
	  if ($N == 1) {
		  $F_OUT = "$MSK_LTLN/$VRF_RGN.txt";
		  print MASKLST "$VRF_RGN\n";
	  } else {
		  $F_OUT = "$MSK_LTLN/$VRF_RGN-$N.txt";
		  print MASKLST "$VRF_RGN-$N\n";
	  }

	  open(OUT,'>',$F_OUT) or die "Cannot open '$F_OUT': $!";

	# Print MET file header line
	  print OUT "$VRF_RGN\n";

	  $line=<FILE>;
          chomp($line);
          $line =~ s/^\s*(.*?)\s*$/$1/;	  
	  (@vars) = split (" ", $line);
	  print "   + $#vars vertices\n";

	# Loop through each polygon vertex coordinate pair 
	  foreach (@vars) {
              ($lon,$lat,$null) = split (",", $_);
              printf OUT "%-9.5f %-10.5f\n", $lat, $lon; }	  
      }  
  }

  close(FILE);
  
#################################################################################
# END PROGRAM
#################################################################################

  print "FINISHED\n\n";
  exit;
   
