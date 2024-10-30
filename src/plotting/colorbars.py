##################################################################################
# Description
##################################################################################
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
from matplotlib.colors import BoundaryNorm, ListedColormap
import math
from functools import partial

##################################################################################
# Load workflow constants and Utility Methods
##################################################################################

@define
class colorbars:
    pass

@define
class explicit_discrete(colorbars):
    THRESHOLDS:list = field(
            validator=validators.deep_iterable(
                member_validator=validators.instance_of(float),
                iterable_validator=validators.instance_of(list),
                )
            )
    COLORS:ListedColormap = field(
            validator=validators.instance_of(ListedColormap),
            converter=lambda x: ListedColormap(x),
            )
    LABELS:list = field(
            validator=validators.deep_iterable(
                member_validator=validators.instance_of(str),
                iterable_validator=validators.instance_of(list),
                )
            )
    def get_norm(self):
        return BoundaryNorm(self.THRESHOLDS, ncolors=self.COLORS)

    def get_colormap(self):
        return self.COLORS

    def get_ticks_labels(self):
        return self.THRESHOLDS, self.LABELS

@define
class implicit_discrete(colorbars):
    NCOL:int = field(
        validator=validators.instance_of(int),
        converter= lambda x: int(x),
        )
    MIN:float = field(
        validator=validators.optional(
            validators.instance_of(float),
            )
        )
    MAX:float = field(
        validator=validators.optional(
            validators.instance_of(float),
            )
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
            raise RuntimeError('PALLETE must be a function of a single' +\
                    ' integer argument for the number of color bins.')

    def set_min_max(self, data):
        if self.ALPHA is None:
            raise AttributeError('ALPHA must be set to define the inner' +\
                    ' 100 - ALPHA range to define the min / max from datat.')

        scale = data[~np.isnan(data)]
        max_scl, min_scl = np.percentile(scale,
                [100 - self.ALPHA / 2, self.ALPHA / 2])

        self.MIN = min_scl
        self.MAX = max_scl

    def get_norm(self):
        if self.MIN is None:
            raise AttributeError('Minimum value of color bar not set,' +\
                    ' define explicitly or use inner 100 - ALPHA range.')

        if self.MAX is None:
            raise AttributeError('Minimum value of color bar not set,' +\
                    ' define explicitly or use inner 100 - ALPHA range.')

        norm = np.linspace(self.MIN, self.MAX, int(self.NCOL + 1))
        step_size = norm[1] - norm[0]
        step_order = math.floor(math.log(step_size, 10))
        round_order = abs(min(0, step_order))
        norm = np.around(norm, decimals=round_order)
        return BoundaryNorm(norm, ncolors=self.NCOL)

    def get_ticks_labels(self):
        if self.MIN is None:
            raise AttributeError('Minimum value of color bar not set,' +\
                    ' define explicitly or use inner 100 - ALPHA range.')

        if self.MAX is None:
            raise AttributeError('Minimum value of color bar not set,' +\
                    ' define explicitly or use inner 100 - ALPHA range.')

        ticks = np.linspace(self.MIN, self.MAX, int(self.NCOL + 1))
        step_size = ticks[1] - ticks[0]
        step_order = math.floor(math.log(step_size, 10))
        round_order = abs(min(0, step_order))
        ticks = np.around(ticks, decimals=round_order)
        labels = np.array(ticks, dtype=str)
        return ticks, labels

    def get_colormap(self):
        return ListedColormap(self.PALLETE(self.NCOL))

##################################################################################
# Dictionaries for colorbar defs
##################################################################################
EXPLICIT_DISCRETE_MAPS = {
        'relative_diff': {
            'THRESHOLDS': [-100., -50., -25., -15., -0.1,
                0.1, 15., 25., 50., 100.],
            'COLORS': [
                '#762a83',
                '#9970ab',
                '#c2a5cf',
                '#e7d4e8',
                '#f7f7f7',
                '#d9f0d3',
                '#a6dba0',
                '#5aae61',
                '#1b7837',
                ],
            'LABELS': ['-100%', '-50%', '-25%', '-15%',
                '-0.1%', '0.1%', '15%', '25%', '50%', '100%'],
            }
        # NOTE: FINISH OFF DEFINITION
        'normalized': {
            'THRESHOLDS': [0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75,
                           0.8, 0.85, 0.9, 0.95, 1.0]
            'COLORS': [
                ],
            'LABELS': ['.45', '.50', '.55', '.60', '.65', '.70',
                       '.75', '.80', '.85', '.90', '.95', '1.0'
            }
        }

IMPLICIT_DISCRETE_MAPS = {
        'dynamic_green_white': {
            'ALPHA': 5.0,
            'PALLETE': partial(sns.cubehelix_palette, start=.75, rot=1.50,
                reverse=False, dark=0.25),
            'NCOL': 10,
            'MIN': None,
            'MAX': None,
            },
        }

##################################################################################
