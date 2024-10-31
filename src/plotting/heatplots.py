##################################################################################
# Description
##################################################################################
# This script is designed to generate heat plots in Matplotlib from MET ASCII
# output files, converted to dataframes with the companion postprocessing routines.
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
from colorbars import *
import ipdb

##################################################################################
# Load workflow constants and Utility Methods
##################################################################################
def check_fcst_lds(instance, attribute, value):
    fcst_range = instance.MAX_LD - instance.MIN_LD
    if fcst_range < 0:
        raise ValueError('MAX_LD is less than MIN_LD.')
    if (fcst_range % int(value)):
        raise ValueError('Hours between the minimum and maximum forecast lead' +\
                ' must be dvisible by the lead incremnt.')

def check_dt_fmt(instance, attribute, value):
    dt_sample = dt(2024, 1, 1, 0)
    try:
        dt_sample.strftime(value)
    except:
        raise ValueError('Value is not a valid date time format code.')

def check_grd_key(instance, attribute, value):
    if not value in instance.CTR_FLW.GRDS:
        raise ValueError('ERROR: ' + value + ' is not a subdomain' +\
                ' of ' + instance.CTR_FLW.NAME)

def check_mem_key(instance, attribute, value):
    if not value in instance.CTR_FLW.MEM_IDS:
        raise ValueError('ERROR: ' + value + ' is not a member' +\
                ' of ' + instance.CTR_FLW.NAME)

##################################################################################
# Plots lead time vertically versus valid date horizontally

@define
class multidate_multilead(plot):
    CTR_FLW:control_flow = field(
            validator=validators.instance_of(control_flow),
            )
    VRF_STRT:str = field(
            converter=convert_dt,
            )
    VRF_STOP:str = field(
            converter=convert_dt,
            )
    DT_INC:str = field(
            validator=validators.matches_re('^[0-9]+h$'),
            converter=lambda x : x + 'h',
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
                validators.instance_of(str),
                check_dt_fmt,
                ],
            )
    COLORBAR:colorbars = field(
            validator=validators.instance_of(colorbars)
            )

    def gen_cycs(self):
        return pd.date_range(start=self.VRF_STRT, end=self.VRF_STOP,
                             freq=self.DT_INC).to_pydatetime()

    def gen_fcst_dts_labs(self):
        # generate valid date range
        anl_dts = self.gen_cycs()
        num_dts = len(anl_dts)

        # generate storage for keys and labels
        date_keys = []
        date_labs = []
        fcst_zhs = []

        for i_nd in range(num_dts):
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
            fcst_dts = pd.date_range(start=fcst_strt, end=fcst_stop,
                    freq=str(self.LD_INC) + 'h').to_pydatetime()
            for fcst_dt in fcst_dts:
                fcst_zhs.append(fcst_dt)

        fcst_zhs = sorted(set(fcst_zhs))

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

        return fcst_lds[::-1], tick_labs[::-1]

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
        num_dts = len(date_keys)
        tmp = np.full([num_lds, num_dts], np.nan)

        for i_nd in range(num_dts):
            for i_nl in range(num_lds):
                try:
                    # try to load data for the date / lead combination
                    val = data.loc[(data['FCST_LEAD'] == fcst_lds[i_nl]) &\
                            (data['FCST_VALID_END'] == date_keys[i_nd])]

                    if not val.empty:
                        tmp[i_nl, i_nd] = val[self.STAT_KEY].iloc[0]

                except:
                    continue

        colorbar = self.COLORBAR
        if hasattr(colorbar, 'ALPHA'):
            colorbar.set_min_max(tmp)

        cb_colormap = colorbar.get_colormap()
        cb_colormap.set_bad('darkgrey')
        cb_norm = colorbar.get_norm()

        sns.heatmap(tmp[:,:], linewidth=0.5, ax=ax1, cbar_ax=ax0,
                    cmap=cb_colormap, norm=cb_norm)

        # define display parameters
        cb_ticks, cb_labels = colorbar.get_ticks_labels()
        ax0.set_yticks(cb_ticks, cb_labels, rotation=270, va='top')
        ax1.set_xticklabels(date_labs, rotation=45, ha='right')
        ax1.set_yticklabels(ld_labs)

        # tick parameters
        ax0.tick_params(
                right=True,
                labelsize=16,
                )

        ax1.tick_params(
                labelsize=16,
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
                self.VRF_STRT.strftime('%Y%m%d%H') + '-to-'+\
                self.VRF_STOP.strftime('%Y%m%d%H') + '_FCST-'+\
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

##################################################################################
# Plots forecast threshold vertically versus forecast lead hour horizontally
# for a fixed valid date

@define
class multilevel_multilead(plot):
    CTR_FLW:control_flow = field(
            validator=validators.instance_of(control_flow),
            )
    STRT_DT:str = field(
            converter=convert_dt,
            )
    STOP_DT:str = field(
            converter=convert_dt,
            )
    DT_INC:str = field(
            validator=validators.matches_re('^[0-9]+h$'),
            converter=lambda x : x + 'h',
            )
    VALID_DT:str = field(
            validator=validators.instance_of(dt),
            converter=convert_dt,
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
    COLORBAR:colorbars = field(
            validator=validators.instance_of(colorbars)
            )

    def gen_cycs(self):
        return pd.date_range(start=self.STRT_DT, end=self.STOP_DT,
                             freq=self.DT_INC).to_pydatetime()

    def gen_fcst_lds_labs(self):
        fcst_zhs = self.gen_cycs()
        fcst_lds = []
        tick_labs = []
        for zh in fcst_zhs:
            lead = (self.VALID_DT - zh).total_seconds()
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

        return fcst_lds[::-1], tick_labs[::-1]

    def gen_plot_text(self):
        title = MET_TOOLS[self.MET_TOOL][self.STAT_KEY]['label']
        title += ' - ' + VRF_REFS[self.VRF_REF]['fields'][self.VRF_FLD]['label']
        title += '\n' + self.CTR_FLW.PLT_LAB

        if self.MEM_LAB:
            if self.MEM_KEY:
                title += ' ' + self.MEM_KEY

        if self.GRD_LAB:
            if self.GRD_KEY:
                title += ' ' + self.GRD_KEY

        dmn_title = 'Domain: ' + self.MSK.replace('_', ' ')
        obs_title = 'Obs Source: ' + self.VRF_REF
        vdt_title = 'Valid: ' + self.VALID_DT.strftime('%HZ %d/%m/%Y')

        return title, dmn_title, obs_title, vdt_title

    def gen_data_range(self):
        # generate the date range and forecast leads for the analysis, parse binary files
        # for relevant fields
        plt_data = {}

        # generate sequence of forecast zero hours for sourcing data
        fcst_zhs = self.gen_cycs()

        # generate sequence of forecast leads for data
        fcst_lds, ld_labs = self.gen_fcst_lds_labs()

        # generate storage for the forecast thresholds
        fcst_lvs = []

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
                    'FCST_THRESH',
                    stat_name,
                   ]

            # cut down df to specified valid dates /leads / region / stat
            stat_data = data[vals]
            stat_data = stat_data.loc[(stat_data['VX_MASK'] == self.MSK)]
            stat_data = stat_data.loc[(stat_data['FCST_VALID_END'] ==
                self.VALID_DT.strftime('%Y%m%d_%H%M%S'))]

            # check if there is data for this configuration and these fields
            if not stat_data.empty:
                # obtain the sorted thresholds
                lvs = sorted(list(set(stat_data['FCST_THRESH'].values)),
                        key=lambda x:(len(x.split('.')[0]), x), reverse=True)
                fcst_lvs += lvs

                if plt_data:
                    # if there is existing data, merge dataframes
                    plt_data['data'] = \
                             pd.concat([plt_data['data'], stat_data], axis=0)
                else:
                    # if this is a first instance, create fields
                    plt_data['data'] = stat_data
                    plt_data['fcst_lds'] = fcst_lds
                    plt_data['ld_labs'] = ld_labs

            else:
                print('WARNING: no data exists in:\n' + INDT + in_path)
                print('corresponding to plotting configuration.')

        # Unique levels are inferred from the data over all forecast start dates
        fcst_lvs = sorted(list(set(fcst_lvs)),
                key=lambda x:(len(x.split('.')[0]), x), reverse=True)

        plt_data['fcst_lvs'] = fcst_lvs

        return plt_data

    def gen_fig(self):
        # generate the plot data
        plt_data = self.gen_data_range()
        data = plt_data['data']
        fcst_lds = plt_data['fcst_lds']
        ld_labs = plt_data['ld_labs']
        fcst_lvs = plt_data['fcst_lvs']

        # Create a figure
        fig = plt.figure(figsize=(12,9.6))

        # Set the axes
        ax0 = fig.add_axes([.92, .18, .03, .72])
        ax1 = fig.add_axes([.07, .18, .84, .72])

        # create array storage for stats
        num_lds = len(fcst_lds)
        num_lvs = len(fcst_lvs)
        tmp = np.full([num_lvs, num_lds], np.nan)

        ipdb.set_trace()
        for i_nv in range(num_lvs):
            for i_nd in range(num_lds):
                try:
                    # try to load data for the date / lead combination
                    val = data.loc[(data['FCST_LEAD'] == fcst_lds[i_nd]) &\
                            (data['FCST_THRESH'] == fcst_lvs[i_nv])]

                    if not val.empty:
                        tmp[i_nv, i_nd] = val[self.STAT_KEY].iloc[0]

                except:
                    continue

        colorbar = self.COLORBAR
        if hasattr(colorbar, 'ALPHA'):
            colorbar.set_min_max(tmp)

        ipdb.set_trace()
        cb_colormap = colorbar.get_colormap()
        cb_colormap.set_bad('darkgrey')
        cb_norm = colorbar.get_norm()

        sns.heatmap(tmp[:,:], linewidth=0.5, ax=ax1, cbar_ax=ax0,
                    cmap=cb_colormap, norm=cb_norm)

        # define display parameters
        ipdb.set_trace()
        cb_ticks, cb_labels = colorbar.get_ticks_labels()
        ax0.set_yticks(cb_ticks, cb_labels, rotation=270, va='top')
        ax1.set_xticklabels(ld_labs, rotation=45, ha='right')
        ax1.set_yticklabels(fcst_lvs)

        # tick parameters
        ax0.tick_params(
                right=True,
                labelsize=16,
                )

        ax1.tick_params(
                labelsize=16,
                )

        lab1='Forecast Lead Hrs'
        lab2='Accumulation threshold - mm'

        plt.figtext(.5, .02, lab1, horizontalalignment='center',
                    verticalalignment='center', fontsize=20)

        plt.figtext(.02, .5, lab2, horizontalalignment='center',
                    verticalalignment='center', fontsize=20, rotation=90)

        title, dmn_title, obs_title, vdt_title = self.gen_plot_text()
        plt.title(title, x = 0.5, y = 1.03, fontsize = 20)
        plt.title(dmn_title, fontsize = 16, loc = 'left')
        plt.title(obs_title, fontsize = 16, loc = 'right')

        in_root, out_root = self.gen_io_paths()
        out_path = out_root + '/' + self.VALID_DT.strftime('%Y%m%d%H') + '_' +\
                self.MSK  + '_' + self.STAT_KEY + '_' + self.CTR_FLW.NAME

        if self.MEM_KEY:
            out_path += '_' + self.MEM_KEY

        if self.GRD_KEY:
            out_path += '_' + self.GRD_KEY

        if self.FIG_LAB:
            out_path += '_' + self.FIG_LAB

        out_path += '_all-level_heatplot.png'

        # save figure and display
        plt.savefig(out_path)
        if self.IF_SHOW:
            plt.show()

##################################################################################
