##################################################################################
# Description
##################################################################################
# This script is designed to generate line plots in Matplotlib from MET ASCII
# output files, converted to dataframes with the companion postprocessing routines.
# This plotting scheme is designed to plot non-threshold data as lines in the
# vertical axis and the number of lead hours to the valid time for verification
# from the forecast initialization in the horizontal axis.
#
# Parameters for the script are to be supplied from a configuration file, with
# name supplied as a command line argument.
#
##################################################################################
# License Statement:
##################################################################################
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
##################################################################################
# Imports
##################################################################################
import matplotlib
from datetime import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import pickle
import os
import sys

##################################################################################
# Define the line plotting class
##################################################################################

class line_plot:
    # Define environment variables in the class
    INDT = os.environ['INDT']
    VRF_ROOT = os.environ['VRF_ROOT']
    IF_SING = os.environ['IF_SING']

    # Define pre-set plotting parameters for specific stats
    stat_labs = {
                 'RMSE': 'Root-Mean\nSquared Error (mm)',
                 'PR_CORR': 'Pearson\nCorrelation',
                 'FSS': 'Fractional\nSkill Score',
                 'AFSS': 'Asymptotic Fractional\nSkill Score',
                 'GSS': 'Gilbert\nSkill Score',
                 'CSI': 'Critical\nSuccess Index',
                }

    # Define the currently supported attributes for line plots
    MET_TOOLS = [
                 'GridStat',
                ]
    PRFXS = [
             'grid_stat_QPF_24hr',
            ]

    def __init__(self, dictionary):
        for key, val in dictionary.items():
            setattr(self, key, val)

    def format_cyc(self):
        if not self.STRT_DT.isdigit() or len(self.STRT_DT) != 10:
            print('ERROR: STRT_DT\n' + self.STRT_DT +\
                    '\n is not in YYYYMMDDHH format.')
            sys.exit(1)
        else:
            iso = self.STRT_DT[:4] + '-' + self.STRT_DT[4:6] + '-' +\
                    self.STRT_DT[6:8] + '_' + self.STRT_DT[8:]
            strt_dt = dt.fromisoformat(iso)
        
        if not self.STOP_DT.isdigit() or len(self.STOP_DT) != 10:
            print('ERROR: STOP_DT\n' + self.STOP_DT +\
                    '\n is not in YYYYMMDDHH format.')
            sys.exit(1)
        else:
            iso = self.STOP_DT[:4] + '-' + self.STOP_DT[4:6] +\
                    '-' + self.STOP_DT[6:8] + '_' + self.STOP_DT[8:]
            stop_dt = dt.fromisoformat(iso)
        
        if not self.CYC_INC.isdigit():
            print('ERROR: CYC_INC\n' + self.CYC_INC + '\n is not in HH format.')
            sys.exit(1)
        else:
            cyc_inc = self.CYC_INC + 'H'
        
        if not self.VALID_DT.isdigit() or len(self.VALID_DT) != 10:
            print('ERROR: VALID_DT, ' + self.VALID_DT + ', is not in YYYYMMDDHH format.')
            sys.exit(1)
        else:
            iso = self.VALID_DT[:4] + '-' + self.VALID_DT[4:6] + '-' +\
                    self.VALID_DT[6:8] + '_' + self.VALID_DT[8:]
            valid_dt = dt.fromisoformat(iso)

        return strt_dt, stop_dt, cyc_inc, valid_dt
 
    def validate_io(self):
        if not self.MET_TOOL in MET_TOOLS:
            print('ERROR: ' + self.MET_TOOL + ' is not a supported tool currently.')
            print('Supported tools include:')
            for tool in self.MET_TOOLS:
                print(INDT + tool)
            sys.exit(1)
        else:
            met_tool = self.MET_TOOL

        if not self.PRFX in PRFXS:
            print('ERROR: ' + self.PRFX + ' is not a supported analysis currently.')
            print('Supported analyses include:')
            for prfx in self.PRFXS:
                print(INDT + prfx)
            sys.exit(1)
        else:
            prfx = self.PRFX

        if not type(self.CSE) == str or len(self.CSE) == 0:
            print('ERROR: case study name attribute "CSE" is not a string' +\
                  ' or is length zero. This must be defined as the root of' +\
                  ' the case study / configuration directory structure for' +\
                  ' verification IO.')
            sys.exit(1)
        else:
            cse = self.CSE

        if not type(self.FIG_CSE) == str:
            print('ERROR: figure output sub-directory name FIG_CSE is not' +\
                  ' a string. Define equal to an empty string if not used.')
            sys.exit(1)

        else:
            fig_cse = self.FIG_CSE

        if self.IF_SING == 'TRUE':
            in_root = '/in_root/' + self.CSE
            out_root = '/out_root/' + self.CSE + '/figures/' + self.FIG_CSE
            os.system('mkdir -p ' + out_root)
            if not os.path.isdir(in_root):
                print('ERROR: input data case directory does not exist.')
                sys.exit(1)
            elif not os.path.isdir(out_root):
                print('ERROR: output figure write directory does not exist.')
        elif self.IF_SING == 'FALSE':
            in_root = VRF_ROOT + '/' + self.CSE
            out_root = VRF_ROOT + '/' + self.CSE + '/figures/' + self.FIG_CSE
            os.system('mkdir -p ' + out_root)
            if not os.path.isdir(in_root):
                print('ERROR: input data case directory does not exist.')
                sys.exit(1)
            elif not os.path.isdir(out_root):
                print('ERROR: output figure write directory does not exist.')
        else:
            print('ERROR: IF_SING must be set to "TRUE" or "FALSE" to' +\
                  ' determine if IO paths are system paths or singularity' +\
                  ' bind paths.')
            sys.exit(1)

        return met_tool, prfx, cse, in_root, out_root

    def gen_lines_labs(self):
        lines_labs = {}
        for ctr_flw in self.CTR_FLWS:
            if hasattr(ctr_flw, 'grds'):
                grds = ctr_flw.grds
            else:
                grds = ['']

            if hasattr(ctr_flw, 'mem_ids'):
                mem_ids = ctr_flw.mem_ids
            else:
                mem_ids = ['']

            for grd in grds:
                for mem in mem_ids:
                    # create label based on configuration
                    split_string = ctr_flw.name.split('_')
                    split_len = len(split_string)
                    idx_len = len(self.LAB_IDX)
                    line_lab = ''
                    lab_len = min(idx_len, split_len)
                    if split_len == 1:
                        line_lab += split_string[0]
        
                    elif idx_len == 1:
                        i_li = LAB_IDX[0]
                        try:
                            line_lab += split_string[i_li]
                        except:
                            msg = 'WARNING: label index ' + str(i_li) +\
                                  ' is out out of bounds for ' + ctr_flw +\
                                  ' underscore components.'
        
                            print(msg)
                            print('Using the full control flow name for' +\
                                  ' plot label.')
                            line_lab += ctr_flw
        
                    else:
                        for i_ll in range(0, lab_len):
                            i_li = LAB_IDX[i_ll]
                            try:
                                line_lab += split_string[i_li] + '_'
                            except:
                                pass
                        
                        line_lab = line_lab[:-1]
            
                    if self.ENS_LAB:
                        if len(mem) > 0:
                            line_lab += '_' + mem
            
                    if self.GRD_LAB:
                        if len(grd) > 0:
                            line_lab += '_' + grd
        
                    key = ctr_flw + ens + grd

                    lines_labs[key] = {
                                       'flw_nme': ctr_flw.name,
                                       'label': line_lab,
                                       'grd': grd,
                                       'idx': mem,
                                      }

        return lines_labs

    def gen_data_range(self):
        # generate the date range and forecast leads for the analysis, parse binary files
        # for relevant fields
        plt_data = {}

        # check for cycling fields and format for workflow
        strt_dt, stop_dt, cyc_inc, valid_dt = self.format_cyc()
        fcst_zhs = pd.date_range(start=strt_dt, end=stop_dt,
                freq=cyc_inc).to_pydatetime()

        # check for valid IO parameters for plotting
        met_tool, prfx, cse, in_root, out_root = self.validate_io()

        # generate all lines to be plotted
        lines_labs = self.gen_lines_labs()
        
        fcst_leads = []
        for key, lines in lines_labs:
            # define derived data paths 
            flw_nme = lines['flw_nme']
            label = lines['label']
            grd = lines['grd']
            idx = lines['idx']

            data_root = in_root + '/' + flw_nme + '/' + met_tool
            for fcst_zh in fcst_zhs:
                # define the input name
                zh_str = fcst_zh.strftime('%Y%m%d%H')
                in_path = data_root + '/' + zh_str + '/' + idx + '/' + grd +\
                        '/' + prfx + '.bin'
                try:
                    with open(in_path, 'rb') as f:
                        data = pickle.load(f)
                        data = data[self.STAT_TYPE]
                except:
                    print('WARNING: input data ' + in_path + ' statistics ' +\
                           self.STAT_TYPE + ' does not exist, skipping this' +\
                           ' configuration.')
                    continue
        
                # load the values to be plotted along with landmask and lead
                vals = [
                        'VX_MASK',
                        'FCST_LEAD',
                        'FCST_VALID_END',
                       ]
    
                if hasattr(self, 'LEV'):
                    vals += ['FCST_THRESH']
        
                # include the statistics and optionally confidence intervals
                vals += self.STAT_KEYS
                if hasattr(self, 'CI'):
                    for i_ns in range(2):
                        stat = self.STAT_KEYS[i_ns]
                        stat_CI = stat + '_' + self.CI
                        if stat_CI + 'L' in data:
                            vals.append(stat_CI + 'L')
                            vals.append(stat_CI + 'U')
            
                # cut down df to specified valid date / region / relevant stats
                stat_data = data[vals]
                stat_data = stat_data.loc[(stat_data['VX_MASK'] == self.MSK)]
                stat_data = stat_data.loc[(stat_data['FCST_VALID_END'] ==
                                           valid_dt.strftime('%Y%m%d_%H%M%S'))]
                if hasattr(self, 'LEV') 
                    stat_data = \
                    stat_data.loc[(stat_data['FCST_THRESH'] == self.LEV)]

                # check if there is data for this configuration and these fields
                if not stat_data.empty:
                    leads = sorted(list(set(stat_data['FCST_LEAD'].values)),
                                   key=lambda x:(len(x), x))
            
                    if key in plt_data.keys():
                        # if there is existing data, concatenate dataframes
                        plt_data[key]['data'] = pd.concat([plt_data[key]['data'],
                            stat_data], axis=0)
                    else:
                        # if this is a first instance, create fields
                        plt_data[key] = {'data': stat_data, 'label': line_lab}
        
                    # obtain leads of data 
                    fcst_leads += leads

                else:
                    print('ERROR: no data exists in:\n' + INDT + in_path)
                    print('corresponding to plotting configuration.')
        
        # find all unique values for forecast leads, sorted for plotting, less than max lead
        fcst_leads = sorted(list(set(fcst_leads)), key=lambda x:(len(x), x))
    
        return plt_data, fcst_leads

    def gen_fig(self):
        # generate the plot data
        plt_data, fcst_leads = self.gen_data_range()

        # create a figure
        fig = plt.figure(figsize=(16,9.6))
        
        # Set the axes
        ax0 = fig.add_axes([.08, .07, .42, .70])
        ax1 = fig.add_axes([.5, .07, .42, .70])
        
        num_leads = len(fcst_leads)
        line_list = []
        line_labs = []
        ax0_l = []
        ax1_l = []
        
        # loop configurations, load trimmed data from plt_data dictionary
        for key, line in plt_data:
            data = line['data']
            line_lab = line['label']
            
            # infer existence of confidence interval data
            cnf_lvs = []
            for i_ns in range(2):
                stat = self.STAT_KEYS[i_ns]
                try:
                    stat_CI = stat + '_' + self.CI
                    if stat_CI + 'L' in data and\
                        not (data[stat_CI + 'L'].isnull().values.any()):
                            cnf_lvs.append(True)
            
                except:
                    cnf_lvs.append(False)
            
                exec('ax = ax%s'%i_ns)
                if cnf_lvs[i_ns]:
                    tmp = np.full([num_leads, 3], np.nan)
            
                    for i_nl in range(num_leads):
                        val = data.loc[(data['FCST_LEAD'] == fcst_leads[i_nl])]
                        if not val.empty:
                            tmp[i_nl, 0] = val[self.STAT_KEYS[i_ns]]
                            tmp[i_nl, 1] = val[self.STAT_KEYS[i_ns] +\
                                    '_' + self.CI + 'L']
                            tmp[i_nl, 2] = val[self.STAT_KEYS[i_ns] +\
                                    '_' + self.CI + 'U']
                    
                    l0 = ax.fill_between(range(num_leads), tmp[:, 1], tmp[:, 2], alpha=0.5)
                    l1, = ax.plot(range(num_leads), tmp[:, 0], linewidth=2)
                    exec('ax%s_l.append([l1,l0])'%i_ns)
                    l = l1
            
                else:
                    tmp = np.full(num_leads, np.nan)
                
                    for i_nl in range(num_leads):
                        val = data.loc[(data['FCST_LEAD'] == fcst_leads[i_nl])]
                        if not val.empty:
                            tmp[i_nl] = val[self.STAT_KEYS[i_ns]]
                    
                    l, = ax.plot(range(num_leads), tmp[:], linewidth=2)
                    exec('ax%s_l.append([l])'%i_ns)
            
            # add the line type to the legend
            line_list.append(l)
            line_labs.append(line_lab)
        
        # set colors and markers
        line_count = len(line_list)
        line_colors = sns.color_palette('husl', line_count)
        for i_lc in range(line_count):
            for i_ns in range(2):
                exec('axl = ax%s_l[i_lc]'%i_ns)
                for i_na in range(len(axl)):
                    l = axl[i_na]
                    l.set_color(line_colors[i_lc])
                    if i_na == 0:
                      l.set_marker((i_lc + 2, 0, 0))
                      l.set_markersize(15)
        
        # generate tic labels based on hour values
        for i_nl in range(num_leads):
            fcst_leads[i_nl] = fcst_leads[i_nl][:-4]
        
        ax0.set_xticks(range(num_leads))
        ax0.set_xticklabels(fcst_leads)
        ax1.set_xticks(range(num_leads))
        ax1.set_xticklabels(fcst_leads)
        
        # tick parameters
        ax1.tick_params(
                labelsize=18
                )
        
        ax0.tick_params(
                labelsize=18
                )
        
        ax0.tick_params(
                labelsize=18,
                bottom=True,
                labelbottom=True,
                right=False,
                labelright=False,
                )
        
        ax.yaxis.tick_right()
        plot0_yticks = ax0.get_yticks()
        ax0.set_yticks(plot0_yticks, ax0.get_yticklabels(), va='bottom')
        tick_labs = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        ax1.set_yticks(np.linspace(0.5, 1, 6), tick_labs, va='bottom')
        ax1.set_ylim([0.45, 1.05])
        
        y_min, y_max = ax0.get_ylim()
        tick_spacing = (plot0_yticks[1] - plot0_yticks[0]) / 2
        ax0.set_ylim([y_min - tick_spacing, y_max + tick_spacing])
        
        ax0.grid(which = 'major', axis = 'y')
        ax1.grid(which = 'major', axis = 'y')
        
        labels = []
        labels = [None] * len(self.STAT_KEYS)
        for i in range(len(self.STAT_KEYS)):
            if self.STAT_KEYS[i] == 'RMSE':
                labels[i] = 'Root-Mean\nSquared Error (mm)'
            elif self.STAT_KEYS[i] == 'PR_CORR':
                labels[i] = 'Pearson\nCorrelation'
            else:
                labels[i] = ''
        
        lab2='Forecast lead hrs'
        
        plt.figtext(.5, .95, TITLE, horizontalalignment='center',
                    verticalalignment='center', fontsize=22)
        
        plt.figtext(.15, .90, DMN_SUBTITLE, horizontalalignment='center',
                    verticalalignment='center', fontsize=18)
        
        plt.figtext(.8375, .90, QPE_SUBTITLE, horizontalalignment='center',
                    verticalalignment='center', fontsize=18)
        
        plt.figtext(.025, .43, labels[0], horizontalalignment='center', rotation=90,
                    verticalalignment='center', fontsize=20)
        
        plt.figtext(.975, .43, labels[1], horizontalalignment='center', rotation=270,
                    verticalalignment='center', fontsize=20)
        
        plt.figtext(.5, .02, lab2, horizontalalignment='center',
                    verticalalignment='center', fontsize=20)
        
        if line_count <= 3:
            ncols = line_count
        else:
            rmdr_3 = line_count % 3
            rmdr_4 = line_count % 4
            if rmdr_3 < rmdr_4:
                ncols = 3
            else:
                ncols = 4
        
        fig.legend(line_list, line_labs, fontsize=18, ncol=ncols, loc='center',
                   bbox_to_anchor=[0.5, 0.83])

# save figure and display
os.system('mkdir -p ' + out_root)
plt.savefig(OUT_PATH)
plt.show()

##################################################################################
# end
