##################################################################################
# Description
##################################################################################
# This script is designed to generate heat plots in Matplotlib from MET ASCII
# output files, converted to dataframes with the companion postprocessing routines.
# This plotting scheme is designed to plot forecast lead in the vertical axis and
# the valid time for verification from the forecast initialization in the
# horizontal axis.
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
from plotting import *
import matplotlib
from datetime import datetime as dt
from datetime import timedelta as td
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap
import seaborn as sns
import numpy as np
import pandas as pd
import pickle
import os
import re
from attrs import define, field, validators
from functools import partial
import ipdb

##################################################################################
# Load workflow constants and Utility Methods 
##################################################################################

@define
class color_bars:
    pass

@define
class explicit_discrete(color_bars):
    THRESHOLDS:list = field(
            validator=validators.deep_iterable(
                member_validator=validators.instance_of(float),
                iterable_validator=validators.instance_of(list),
                )
            )
    COLORS:ListedColormap = field(
            validator=validators.instance_of(ListedColormap)
            )

    def get_norm():
        return BoundaryNorm(self.THRESHOLDS, ncolors=self.COLORS)

    def get_colormap():
        return ListedColormap(self.COLORS)

@define
class implicit_discrete(color_bars):
    NCOL:int = field(
        validator=validators.instance_of(int),
        )
    MIN:int = field(
        validator=validators.instance_of(int),
        )
    MAX:int = field(
        validator=validators.instance_of(int),
        )
    ALPHA:float = field(
            validator=validators.optional([
                validators.instance_of(float),
                validators.gt(0.0),
                validators.lt(100.0),
                ]),
            )
    PALLETE = field()
    @PALLETE.validator
    def test_call(self, attribute, value):
        try:
            value(10)
        except:
            raise RuntimeError('PALLETE must be a function of a single \
                    integer argument for the number of color bins.')

    def set_min_max(data):
        if not self.ALPHA:
            raise AttributeError('ALPHA must be set to define the inner \
                    100 - ALPHA range to define the min / max from datat.')

        scale = data[~np.isnan(data)]
        max_scl, min_scl = np.percentile(scale,
                [100 - self.ALPHA / 2, self.ALPHA / 2])

        self.MIN = min_scl
        self.MAX = max_scl
        
    def get_norm():
        if not self.MIN:
            raise AttributeError('Minimum value of color bar not set, \
                    define explicitly or use inner 100 - ALPHA range.')

        if not self.MAX:
            raise AttributeError('Minimum value of color bar not set, \
                    define explicitly or use inner 100 - ALPHA range.')

        norm = np.linspace(self.MIN, self.MAX, int(self.NCOL + 1))
        return BoundaryNorm(norm, ncolors=self.NCOL)

    def get_colormap():
        return self.PALLETE(self.NCOL)

##################################################################################
# Default color map options
##################################################################################
EXPLICIT_DISCRETE_MAPS = {
        'relative_diff': {
            'THRESHOLDS': [-100, -50, -25, -15, -0.1, 0.1, 15, 25, 50, 100],
            'COLORS': [
                '#762a83', # -50 to -100%
                '#9970ab', # -25 to -50%
                '#c2a5cf', # -15 to -25%
                '#e7d4e8', # -0.1 to -15%
                '#f7f7f7', # for zero values
                '#d9f0d3', # 0.1 to 15%
                '#a6dba0', # 15 to 25%
                '#5aae61', # 25 to 50%
                '#1b7837', # 50 to 100%
                ],
            'LABELS': ['-100%', '-50%', '-25%', '-15%',
                '-0.1%', '0.1%', '15%', '25%', '50%', '100%'],
            }
        }

IMPLICIT_DISCRETE_MAPS = {
        'dynamic_basic': {
            'ALPHA': 5.0,
            'PALLETE': partial(sns.cubehelix_palette,
            start=.75, rot=1.50, reverse=False, dark=0.25)
            }
        }

##################################################################################

def check_fcst_lds(instance, attribute, value):
    fcst_range = instance.MAX_LD - instance.MIN_LD
    if fcst_range < 0:
        raise ValueError('MAX_LD is less than MIN_LD.')
    if (fcst_range % int(value)):
        raise ValueError('Hours between the minimum and maximum forecast lead\
                must be dvisible by the lead incremnt.')

def check_dt_fmt(instance, attribute, value):
    dt_sample = dt(2024, 1, 1, 0)
    try:
        dt_sample.strftime(value)
    except:
        raise ValueError('Value is not a valid date time format code.')

def check_grd_key(instance, attribute, value):
    if not value in instance.CTR_FLW['GRDS']:
        raise ValueError('ERROR: ' + value + ' is not a subdomain' +\
                ' of ' + instance.CTR_FLW.NAME)

def check_mem_key(instance, attribute, value):
    if not value in instance.CTR_FLW['GRDS']:
        raise ValueError('ERROR: ' + value + ' is not a member' +\
                ' of ' + instance.CTR_FLW.NAME)

class multidate_multilead(plot):
    CTR_FLW:control_flow = field(
            validator=validators.instance_of(control_flow),
            )
    STAT_KEY:str = field(
            validator=[
                validators.instance_of(str),
                check_stat_key,
                ],
            )
    GRD_KEY:str = field(
            validator=validators.optional([
                validators.instance_of(str),
                check_grd_key,
                ]),
            )
    MEM_KEY:str = field(
            validator=validators.optional([
                validators.instance_of(str),
                check_mem_key,
                ]),
            )
    MIN_LD:int = field(
            validator=[
                validators.instance_of(int),
                ],
            converter=lambda x : int(x),
            )
    MAX_LD:int = field(
            validator=[
                validators.instance_of(int),
                ],
            converter=lambda x : int(x),
            )
    LD_INC:int = field(
            validator=[
                validators.instance_of(int),
                check_fcst_lds,
                ],
            converter=lambda x : int(x),
            )
    DT_FMT:str = field(
            validator=[
                validators.instance_of(int),
                check_dt_fmt,
                ],
            )
    COLOR_BAR:color_bars = field(
            validator=validators.instance_of(color_bars)
            )

    def gen_fcst_dts_labs():
        # generate valid date range
        anl_dts = self.gen_cycs()
        num_dts = len(anl_dts)

        # generate storage for keys and labels
        date_keys = []
        date_labs = []
        fcst_zhs = []

        for i_nd in anl_dts:
            # generate the tick label
            anl_dt = anl_dts[i_nd]
            date_keys.append(anl_dt.strftime('%Y%m%d_%H%M%S'))

            if ( i_nd % 2 ) == 0 or num_dts < 10:
                # if 10 or more dates, only use every other as a label
                date_labs.append(anl_dt.strftime(self.DT_FMT))
            else:
                date_labs.append('')
        
            # generate start dates by min / max forecast length from valid dates
            fcst_strt = anl_dt - td(hours=self.MAX_LD)
            fcst_stop = anl_dt - td(hours=self.MIN_LD)
            fcst_zhs.append(pd.date_range(start=fcst_strt,
                end=fcst_stop, freq=str(self.LD_INC) + 'h'))

        fcst_zhs = list(set(fcst_zhs)).sort().to_pydatetime()

        return fcst_zhs, date_keys, date_labs

    def gen_fcst_lds_labs(self):
        ld = self.MIN_LD
        fcst_lds = []
        tick_labs = []
        while ld <= self.MAX_LD:
            lead = int(ld * 3600)
            seconds = str(int(lead % 60)).zfill(2)
            minutes = str(int(lead % 3600)).zfill(2)
            hours = str(int(lead / 3600 ))
            fcst_lds.append(hours + minutes + seconds)

            tick_label = hours 
            if not seconds == '00':
                tick_label += ':' + minutes + ':' + seconds
            elif not minutes == '00':
                tick_label += ':' + minutes

            tick_labs.append(tick_label)

            ld += self.LD_INC

        return fcst_lds, tick_labs

    def gen_plot_text(self):
        title = MET_TOOLS[self.MET_TOOL][self.STAT_KEY]['label'] 
        title += ' - ' + VRF_REFS[self.VRF_REF]['fields'][self.VRF_FLD]['label']
        if self.LEV:
            title += ' - Threshold: ' + self.LEV + 'mm'

        title += '\n' + self.CTR_FLW.PLT_LAB

        if self.MEM_LAB:
            if self.MEM_KEY:
                title += ' ' + self.MEM_KEY

        if self.GRD_LAB:
            if self.GRD_KEY:
                title += ' ' + self.GRD_KEY

        dmn_title = 'Domain: ' + self.MSK.replace('_', ' ')
        obs_title = 'Obs Source: ' + self.VRF_REF

        return title, dmn_title, obs_title
        
    def gen_data_range(self):
        # generate the date range and forecast leads for the analysis, parse binary files
        # for relevant fields
        plt_data = {}

        # generate sequence of forecast zero hours for sourcing data
        fcst_zhs, date_keys, date_labs = self.gen_fcst_dts_labs()

        # generate sequence of forecast leads for data
        fcst_lds, ld_labs = self.gen_fcst_lds_labs()
        
        # check for valid IO parameters for plotting
        in_root, out_root = self.gen_io_paths()

        flw_nme = self.CTR_FLW.NAME
        if self.MEM_KEY:
            idx = self.MEM_KEY
        else:
            idx = ''

        if self.GRD_KEY:
            grd = self.GRD_KEY
        else:
            grd = ''

        data_root = in_root + '/' + flw_nme + '/' + self.MET_TOOL + '/' +\
                self.VRF_REF
        
        stat_name = self.STAT_KEY
        stat_type = MET_TOOLS[self.MET_TOOL][stat_name]['type']

        for fcst_zh in fcst_zhs:
            # define the input name
            in_path = data_root + '/' + fcst_zh.strftime('%Y%m%d%H') +\
                    '/' + idx + '/' + grd + '/' + self.VRF_FLD + '.bin'
        
            try:
                with open(in_path, 'rb') as f:
                    data = pickle.load(f)
                    data = data[stat_type]
            except:
                print('WARNING: input data ' + in_path + ' statistics ' +\
                       stat_type + ' does not exist, skipping this' +\
                       ' configuration.')
                continue

            # load the values to be plotted along with landmask and lead
            vals = [
                    'VX_MASK',
                    'FCST_LEAD',
                    'FCST_VALID_END',
                    stat_name,
                   ]

            if self.LEV:
                vals += ['FCST_THRESH']

            # cut down df to specified valid dates /leads / region / stat
            stat_data = data[vals]
            stat_data = stat_data.loc[(stat_data['VX_MASK'] == self.MSK)]
            ipdb.set_trace()
            stat_data = stat_data.loc[(stat_data['FCST_VALID_END'].isin(date_keys))]
            stat_data = stat_data.loc[(stat_data['FCST_LEAD'].isin(fcst_lds))]
            if self.LEV:
                stat_data = \
                stat_data.loc[(stat_data['FCST_THRESH'] == self.LEV)]

            # check if there is data for this configuration and these fields
            if not stat_data.empty:
                if plt_data:
                    # if there is existing data, merge dataframes
                    plt_data['data'] = \
                             pd.concat([plt_data['data'], stat_data], axis=0)
                else:
                    # if this is a first instance, create fields
                    plt_data['data'] = stat_data
                    plt_data['date_keys'] = date_keys
                    plt_data['date_labs'] = date_labs
                    plt_data['fcst_lds'] = fcst_lds
                    plt_data['ld_labs'] = ld_labs

            else:
                print('WARNING: no data exists in:\n' + INDT + in_path)
                print('corresponding to plotting configuration.')

        return plt_data

    def gen_fig(self):
        # generate the plot data
        plt_data = self.gen_data_range()
        data = plt_data['data']
        date_keys = plt_data['date_keys']
        date_labs = plt_data['date_labs']
        fcst_lds = plt_data['fcst_lds']
        ld_labs = plt_data['ld_labs']

        # Create a figure
        fig = plt.figure(figsize=(12,9.6))
        
        # Set the axes
        ax0 = fig.add_axes([.92, .18, .03, .72])
        ax1 = fig.add_axes([.07, .18, .84, .72])
        
        # create array storage for stats
        num_lds = len(fcst_lds)
        num_dts = len(anl_dts)
        tmp = np.full([num_lds, num_dts], np.nan)

        ipdb.set_trace()
        for i_nd in range(num_dts):
            for i_nl in range(num_lds):
                try:
                    # try to load data for the date / lead combination
                    val = data.loc[(data['FCST_LEAD'] == fcst_lds[i_nl]) &\
                            (data['FCST_VALID_END'] == date_keys[i_nd])]
                    
                    if not val.empty:
                        tmp[i_nl, i_nd] = val[STAT]
        
                except:
                    continue

        ipdb.set_trace()
        color_bar = self.COLOR_BAR
        if hasattr(color_map, 'ALPHA'):
            color_map.set_min_max(tmp)
        
        sns.heatmap(tmp[:,:], linewidth=0.5, ax=ax1, cbar_ax=ax0,
                    cmap=color_bar.get_color_map(), norm=color_bar.get_norm())
        
        ##################################################################################
        # define display parameters
        ax0.set_yticklabels(ax0.get_yticklabels(), rotation=270, va='top')
        ax1.set_xticklabels(fcst_dts, rotation=45, ha='right')
        ax1.set_yticklabels(ld_labs)
        
        # tick parameters
        ax0.tick_params(
                labelsize=16
                )
        
        ax1.tick_params(
                labelsize=16
                )
        
        lab1='Verification Valid Date'
        lab2='Forecast Lead Hrs'
        plt.figtext(.5, .02, lab1, horizontalalignment='center',
                    verticalalignment='center', fontsize=20)
        
        plt.figtext(.02, .5, lab2, horizontalalignment='center',
                    verticalalignment='center', fontsize=20, rotation=90)
        
        title, dmn_title, obs_title = self.gen_plot_text()
        plt.title(title, x = 0.5, y = 1.03, fontsize = 20)
        plt.title(dmn_title, fontsize = 16, loc = 'left')
        plt.title(obs_title, fontsize = 16, loc = 'right')
        
        in_root, out_root = self.gen_io_paths()
        out_path = out_root + '/' +\
                self.STRT_DT.strftime('%Y%m%d%H') + '-to-'+\
                self.STOP_DT.strftime('%Y%m%d%H') + '_FCST-'+\
                str(self.MIN_LD) + 'hrs-' + str(self.MAX_LD) + 'hrs_'+\
                self.MSK + '_' + self.STAT_KEY + '_' 


        if self.LEV:
            out_path += '_lev'
            lev_split = re.split(r'\D+', self.LEV)
            for split in lev_split:
                if split:
                    out_path += '_' + split

        out_path += '_' + self.CTR_FLW.NAME

        if self.MEM_KEY:
            out_path += '_' + self.MEM_KEY

        if self.GRD_KEY:
            out_path += '_' + self.GRD_KEY

        if self.FIG_LAB:
            out_path += '_' + self.FIG_LAB

        out_path += '_heatplot.png'

        # save figure and display
        plt.savefig(out_path)
        if self.IF_SHOW:
            plt.show()
