##################################################################################
# Description
##################################################################################
# This script is designed to generate line plots in Matplotlib from MET ASCII
# output files, converted to dataframes with companion postprocessing routines.
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
##################################################################################
# Imports
##################################################################################
from plotting import *

##################################################################################
# Load workflow constants and Utility Methods
##################################################################################
# Confidence interval type leading code (Normal or Bootstrap)
CIS = ['NC', 'BC']

##################################################################################
# Define the line plotting class
##################################################################################
@define
class dual_line_plot(plot):
    CTR_FLWS:list = field(
            validator=validators.deep_iterable(
                member_validator=validators.instance_of(control_flow),
                iterable_validator=validators.instance_of(list),
                )
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
    STAT_KEYS:list = field(
            validator=[
                validators.deep_iterable(
                    member_validator=[
                        validators.instance_of(str),
                        check_stat_key,
                        ],
                    iterable_validator=validators.instance_of(list),
                ),
                validators.min_len(2),
                validators.max_len(2),
                ]
            )
    CI:str = field(
            validator=validators.optional([
                validators.instance_of(str),
                validators.in_(CIS),
                ])
            )
    VRT_RNG_0
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
        title=VRF_REFS[self.VRF_REF]['fields'][self.VRF_FLD]['label']
        if self.LEV:
            title += ' - Threshold: ' + self.LEV + 'mm'

        title +='\n' +\
                'Valid: ' + self.VALID_DT.strftime('%HZ %d/%m/%Y')
        dmn_title = 'Domain: ' + self.MSK.replace('_', ' ')
        obs_title = 'Obs Source: ' + self.VRF_REF
        panel_labels = []
        for i_s in range(2):
            panel_labels.append(\
                    MET_TOOLS[self.MET_TOOL][self.STAT_KEYS[i_s]]['label'])

        return title, dmn_title, obs_title, panel_labels

    def gen_lines_labs(self):
        lines_labs = {}
        for ctr_flw in self.CTR_FLWS:
            if ctr_flw.MEM_IDS:
                mem_ids = ctr_flw.MEM_IDS
            else:
                mem_ids = ['']

            if ctr_flw.GRDS:
                grds = ctr_flw.GRDS
            else:
                grds = ['']

            for grd in grds:
                for mem in mem_ids:
                    line_lab = ctr_flw.PLT_LAB
                    if self.MEM_LAB:
                        if len(mem) > 0:
                            line_lab += ' ' + mem

                    if self.GRD_LAB:
                        if len(grd) > 0:
                            line_lab += ' ' + grd

                    key = ctr_flw.NAME
                    if ctr_flw.MEM_IDS:
                        key += '_' + mem

                    if ctr_flw.GRDS:
                        key += '_' + grd

                    lines_labs[key] = {
                                       'flw_nme': ctr_flw.NAME,
                                       'label': line_lab,
                                       'grd': grd,
                                       'idx': mem,
                                      }

        return lines_labs

    def gen_data_range(self):
        # define storage for plotting data
        plt_data = {}

        # generate sequence of forecast zero hours for sourcing data
        fcst_zhs = self.gen_cycs()

        # check for valid IO parameters for plotting
        in_root, out_root = self.gen_io_paths()

        # generate all lines to be plotted
        lines_labs = self.gen_lines_labs()

        for line_key, line in lines_labs.items():
            # define derived data paths
            flw_nme = line['flw_nme']
            label = line['label']
            grd = line['grd']
            idx = line['idx']

            data_root = in_root + '/' + flw_nme + '/' + self.MET_TOOL + '/' +\
                    self.VRF_REF

            for fcst_zh in fcst_zhs:
                # define the input name
                in_path = data_root + '/' + fcst_zh.strftime('%Y%m%d%H') +\
                        '/' + idx + '/' + grd + '/' + self.VRF_FLD + '.bin'

                for i_ns in range(2):
                    stat_name = self.STAT_KEYS[i_ns]
                    stat_type = MET_TOOLS[self.MET_TOOL][stat_name]['type']
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

                    # optionally include confidence intervals
                    CI = False
                    if self.CI:
                        stat_CI = stat_name + '_' + self.CI
                        if stat_CI + 'L' in data:
                            vals.append(stat_CI + 'L')
                            vals.append(stat_CI + 'U')
                            CI = True

                    # cut down df to specified valid date / region / relevant stats
                    stat_data = data[vals]
                    stat_data = stat_data.loc[(stat_data['VX_MASK'] == self.MSK)]
                    stat_data = stat_data.loc[(stat_data['FCST_VALID_END'] ==
                        self.VALID_DT.strftime('%Y%m%d_%H%M%S'))]
                    if self.LEV:
                        stat_data = \
                        stat_data.loc[(stat_data['FCST_THRESH'] == self.LEV)]

                    # check if there is data for this configuration and these fields
                    if not stat_data.empty:
                        stat_key = line_key + '_' + stat_name

                        if stat_key in plt_data.keys():
                            # if there is existing data, merge dataframes
                            plt_data[stat_key]['data'] = \
                                     pd.concat([plt_data[stat_key]['data'],
                                         stat_data], axis=0)
                        else:
                            # if this is a first instance, create fields
                            plt_data[stat_key] = {
                                    'data': stat_data,
                                    'label': label,
                                    'stat_name': stat_name,
                                    'CI': CI,
                                    }

                    else:
                        print('WARNING: no data exists in:\n' + INDT + in_path)
                        print('corresponding to plotting configuration.')

        return plt_data

    def gen_fig(self):
        # generate the plot data
        plt_data = self.gen_data_range()
        fcst_lds, x_tick_labs = self.gen_fcst_lds_labs()

        # create a figure
        fig = plt.figure(figsize=(16,9.6))

        # Set the axes
        ax0 = fig.add_axes([.08, .07, .42, .70])
        ax1 = fig.add_axes([.5, .07, .42, .70])
        ax_list = [ax0, ax1]
        ax_lines_list = [[], []]

        num_lds = len(fcst_lds)
        line_list = []
        line_labs = []

        # loop configurations, load trimmed data from plt_data dictionary
        for key, data in plt_data.items():
            plt_data = data['data']
            line_lab = data['label']
            stat_name = data['stat_name']
            CI = data['CI']

            # Set the figure panel to add the stat line
            if stat_name == self.STAT_KEYS[0]:
                i_ns = 0
            else:
                i_ns = 1

            ax = ax_list[i_ns]
            if CI:
                tmp = np.full([num_lds, 3], np.nan)
                for i_nl in range(num_lds):
                    val = plt_data.loc[(plt_data['FCST_LEAD'] ==\
                            fcst_lds[i_nl])]
                    if not val.empty:
                        tmp[i_nl, 0] = val[stat_name].iloc[0]
                        tmp[i_nl, 1] = val[stat_name + '_' +\
                                self.CI + 'L'].iloc[0]
                        tmp[i_nl, 2] = val[stat_name + '_' +\
                                self.CI + 'U'].iloc[0]

                l0 = ax.fill_between(range(num_lds), tmp[:, 1],
                        tmp[:, 2], alpha=0.5)
                l1, = ax.plot(range(num_lds), tmp[:, 0], linewidth=2)
                ax_lines_list[i_ns].append([l1,l0])
                l = l1

            else:
                tmp = np.full(num_lds, np.nan)

                for i_nl in range(num_lds):
                    val = plt_data.loc[(plt_data['FCST_LEAD'] ==\
                            fcst_lds[i_nl])]
                    val = val[stat_name]
                    if not val.empty:
                        tmp[i_nl] = val.iloc[0]

                l, = ax.plot(range(num_lds), tmp[:], linewidth=2)
                ax_lines_list[i_ns].append([l])

            if i_ns == 0:
                line_list.append(l)
                line_labs.append(line_lab)

        # set colors and markers
        line_count = len(line_list)
        line_colors = sns.color_palette('husl', line_count)
        for i_ns in range(2):
            line_ns = ax_lines_list[i_ns]
            for i_lc in range(line_count):
                line = line_ns[i_lc]
                for i_nl in range(len(line)):
                    l = line[i_nl]
                    l.set_color(line_colors[i_lc])
                    if i_nl == 0:
                      l.set_marker((i_lc + 2, 0, 0))
                      l.set_markersize(15)

        ax0.set_xticks(range(num_lds))
        ax0.set_xticklabels(x_tick_labs)
        ax1.set_xticks(range(num_lds))
        ax1.set_xticklabels(x_tick_labs)

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

        # NOTE: NEED TO DECIDE HOW TO SUPPLY A FIXED SCALE HERE
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

        lab2='Forecast lead hrs'

        title, dmn_title, obs_title, panel_labels = self.gen_plot_text()

        plt.figtext(.5, .95, title, horizontalalignment='center',
                    verticalalignment='center', fontsize=22)

        plt.figtext(.15, .90, dmn_title, horizontalalignment='center',
                    verticalalignment='center', fontsize=18)

        plt.figtext(.8375, .90, obs_title, horizontalalignment='center',
                    verticalalignment='center', fontsize=18)

        plt.figtext(.025, .43, panel_labels[0], horizontalalignment='center',
                    rotation=90, verticalalignment='center', fontsize=20)

        plt.figtext(.975, .43, panel_labels[1], horizontalalignment='center',
                    rotation=270, verticalalignment='center', fontsize=20)

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

        in_root, out_root = self.gen_io_paths()
        if self.FIG_LAB:
            fig_lab = '_' + self.FIG_LAB
        else:
            fig_lab = ''

        out_path = out_root + '/' + self.VALID_DT.strftime('%Y%m%d%H') + '_' +\
                self.MSK + '_' + self.STAT_KEYS[0] + '_' + self.STAT_KEYS[1]

        if self.LEV:
            out_path += '_lev'
            lev_split = re.split(r'\D+', self.LEV)
            for split in lev_split:
                if split:
                    out_path += '_' + split

        out_path += fig_lab + '_lineplot.png'

        # save figure and display
        plt.savefig(out_path)
        if self.IF_SHOW:
            plt.show()

##################################################################################
