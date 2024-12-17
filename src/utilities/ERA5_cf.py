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
##################################################################################
# Imports
##################################################################################
from utilities import *

##################################################################################

#def gen_coord_attrs(ds_in, ds_out):

#def assign_attrs(ds_in, ds_out):

def split_grib_on_dates(f_in, f_out_dir, f_out_basename):
    data = xr.open_dataset(f_in, engine='cfgrib')
    times = data.time.values
    date_times = pd.to_datetime(times).to_pydatetime()
    for i_t, time in enumerate(times):
        date_time = date_times[i_t].strftime('%Y-%m-%d_%H_%M_%S')
        date_data = data.sel({'time': time})
        f_out = f_out_dir + '/' + f_out_basename + '_' + date_time + '.nc'
        print('Writing out sub-dataset valid on ' + date_time + ' to file:')
        print(INDT + f_out)
        date_data.to_netcdf(path=f_out)
    print('Completed splitting all dates in file:')
    print(INDT + f_in)
    print('to directory:')
    print(INDT + f_out_dir)

    return None

def cf_ivt(ds_in):
    """
    Function to calculate IVT and IWV and put into cf-compliant xarray dataset.
    """

    # Calc IVT from surface to 100hPa, extract water vapor mixing ratio [kg/kg],
    # convert to specific humidity filling with nan at null levs
    pres = ds_in['isobaricInhPa'] * 100
    q = ds_in['q']
    q = np.where(pres >= 10000.0, q, np.nan)
   
    # Vertical Pa differences between layer interfaces
    d_pres = pres[:-1] - pres[1:]

    # calculate the integral with average for trapeziodal rule
    avg_q = 0.5 * (q[:-1, :, :] + q[1:, :, :])
    IWV = np.nansum((avg_q * d_pres) / 9.81, axis=0)

    # calculate the u/v components of the *staggered* wind [m/s] to
    # calculate the integral with the average for trapeziodal rule
    u = ds_in['u']
    v = ds_in['v']
    avg_u = 0.5 * (u[:-1, :, :] + u[1:, :, :])
    avg_v = 0.5 * (v[:-1, :, :] + v[1:, :, :])

    # Calculates u and v components of IVT
    IVTU = np.nansum((avg_q * d_pres * avg_u) / 9.81, axis=1)
    IVTV = np.nansum((avg_q * d_pres * avg_v) / 9.81, axis=1)

    # Combines components into IVT magnitude
    IVT = np.sqrt(IVTU**2 + IVTV**2)

    # Prepares output ds
    ds_out = xr.Dataset(
            data_vars = dict(
                IWV=(['time', 'lat', 'lon'], IWV),
                IVT=(['time', 'lat', 'lon'], IVT),
                IVTU=(['time', 'lat', 'lon'], IVTU),
                IVTV=(['time', 'lat', 'lon'], IVTV),
                ),
            coords = dict(
                time = (['time'], np.array([0])),
                lat = ('lat', ds_in.latitude.values),
                lon = ('lon', ds_in.longitude.values),
                ),
            )

    # Assigns attributes
    ds_out = assign_attrs(ds_in, ds_out, f_time)

    return ds_out

##################################################################################
