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

def split_grib_on_dates(f_in, f_out_dir, f_out_basename):
    data = xr.open_dataset(f_in, engine='cfgrib')
    times = data.time.values
    date_times = pd.to_datetime(times).to_pydatetime()
    f_list = []
    os.system('mkdir -p ' + f_out_dir)
    
    for i_t, time in enumerate(times):
        date_time = date_times[i_t].strftime('%Y%m%d%H')
        date_data = data.sel({'time': time})
        f_out = f_out_dir + '/' + f_out_basename + '_' + date_time + '.nc'
        print('Writing out sub-dataset valid on ' + date_time + ' to file:')
        print(INDT + f_out)
        date_data.to_netcdf(path=f_out)
        f_list.append(f_out)

    print('Completed splitting all dates in file:')
    print(INDT + f_in)
    print('to directory:')
    print(INDT + f_out_dir)

    return f_list

def gen_coord_attrs(ds_in, ds_out):
    """
    Function to set global xarray data attributes.
    
    NOTE: TIME COORDS ARE NEGLECTED for consistency with CW3E StageIV prod
    """

    # Declares fill value
    fill_val = 1e20
    ds_out.fillna(fill_val)

    # For data vars, who share these attributes
    repeat_attrs = {
            'missing_value':fill_val, 
            }

    # Global ds dimension and coordinate attributes
    ds_out.lat.attrs = {
        'long_name': 'Latitude',
        'standard_name': 'latitude',
        'units': 'degrees_north',
        'missing_value': fill_val,
        'axis': 'Y',
        }
    
    ds_out.lon.attrs = {
        'long_name': 'Longitude',
        'standard_name': 'longitude',
        'units': 'degrees_east',
        'missing_value': fill_val,
        'axis':'X',
        }
    
    return ds_out, repeat_attrs

def assign_attrs(ds_in, ds_out):
    """
    Function to assign attributes to new data variables.
    """

    # Sets up global dataset attributes
    ds_out, repeat_attrs = gen_coord_attrs(ds_in, ds_out)

    if 'IWV' in ds_out.data_vars:
        ds_out.IWV.attrs = {
                'description':'Column-integrated water vapor',
                'standard_name':'integrated_water_vapor',
                'long_name':'Integrated Water Vapor',
                'units':'kg m-2',
                **repeat_attrs
                }

    if 'IVT' in ds_out.data_vars:
        ds_out.IVT.attrs = {
                'description':'Column-integrated vapor transport',
                'standard_name':'integrated_vapor_transport',
                'long_name':'Integrated Vapor Transport',
                'units':'kg m-1 s-1',
                **repeat_attrs
                }

    if 'IVTU' in ds_out.data_vars:
        ds_out.IVTU.attrs = {
                'description':'Column-integrated vapor transport u-component',
                'standard_name':'integrated_vapor_transport_u',
                'long_name':'Integrated Vapor Transport U-component',
                'units':'kg m-1 s-1',
                **repeat_attrs
                }

    if 'IVTV' in ds_out.data_vars:
        ds_out.IVTV.attrs = {
                'description':'Column-integrated vapor transport v-component',
                'standard_name':'integrated_vapor_transport_v',
                'long_name':'Integrated Vapor Transport V-component',
                'units':'kg m-1 s-1',
                **repeat_attrs
                }

    ds_out = global_attrs(ds_out)
    return ds_out

def cf_ivt(ds_in):
    """
    Function to calculate IVT and IWV and put into cf-compliant xarray dataset.
    """

    # Calc IVT from surface to 100hPa, extract water vapor mixing ratio [kg/kg],
    # convert to specific humidity filling with nan at null levs
    pres = ds_in['isobaricInhPa'] * 100
    idx = np.squeeze(np.argwhere(pres.values >= 10000.0))
    pres = pres[idx]
    q = ds_in['q']
    q = q[idx, :, :]
   
    # Vertical Pa differences between pressure layers
    d_pres = pres.values[:-1] - pres.values[1:]

    # calculate the integral with average for trapeziodal rule
    avg_q = 0.5 * (q.values[:-1, :, :] + q.values[1:, :, :])
    avg_q = avg_q.transpose([1, 2, 0])
    IWV = np.nansum((avg_q * d_pres) / 9.81, axis=-1)

    # extract the u/v components of the *staggered* wind [m/s] to
    # calculate the integral with the average for trapeziodal rule
    u = ds_in['u']
    v = ds_in['v']
    avg_u = 0.5 * (u.values[:-1, :, :] + u.values[1:, :, :])
    avg_u = avg_u.transpose([1, 2, 0])

    avg_v = 0.5 * (v.values[:-1, :, :] + v.values[1:, :, :])
    avg_v = avg_v.transpose([1, 2, 0])

    # Calculates u and v components of IVT
    IVTU = np.nansum((avg_q * d_pres * avg_u) / 9.81, axis=-1)
    IVTV = np.nansum((avg_q * d_pres * avg_v) / 9.81, axis=-1)

    # Combines components into IVT magnitude
    IVT = np.sqrt(IVTU**2 + IVTV**2)

    # Prepares output ds
    ds_out = xr.Dataset(
            data_vars = dict(
                IWV_00h=(['lat', 'lon'], IWV[:, :]),
                IVT_00h=(['lat', 'lon'], IVT[:, :]),
                IVTU_00h=(['lat', 'lon'], IVTU[:, :]),
                IVTV_00h=(['lat', 'lon'], IVTV[:, :]),
                ),
            coords = dict(
                time = (['time'], np.array([0])),
                lat = ('lat', ds_in.latitude.values),
                lon = ('lon', ds_in.longitude.values),
                ),
            )

    # Assigns attributes
    ds_out = assign_attrs(ds_in, ds_out)

    return ds_out

def average_ivt(f_list):
    # averages hourly IVT values into single file, valid at final time
    # inclusive of all files in list in temporal order
    n_hrs = len(f_list)
    valid_file = f_list[-1]
    split_path = valid_file.split('/')
    date = split_path[-1].split('_')[-1]
    path = ''
    for i_s in range(len(split_path) - 1 ):
        path += split_path[i_s] + '/'

    ds_valid = xr.open_dataset(valid_file).IVT_00h
    ivt_avg = ds_valid.values

    for i_f in range(n_hrs - 1):
        fname = f_list[i_f]
        ivt = xr.open_dataset(fname).IVT_00h.values
        ivt_avg += ivt

    ivt_avg = ivt_avg / n_hrs
    ds_out = global_attrs(xr.Dataset())
    # Declares fill value
    coords = ds_valid.coords
    fill_val = 1e20

    ds_out = ds_out.assign_coords({
        'lat': coords['lat'].values,
        'lon': coords['lon'].values,
        })
    ds_out, repeat_attrs = gen_coord_attrs(ds_valid, ds_out)

    # turn this into the number of hours between end points
    n_hrs = str(n_hrs - 1).zfill(2) 
    ds_out['IVT_' + n_hrs + 'h'] = (['lat', 'lon'], ivt_avg)
    ds_out['IVT_' + n_hrs + 'h'].attrs = {
            'description':'Column-integrated vapor transport averaged over time',
            'standard_name':'time_averaged_integrated_vapor_transport',
            'long_name':'Time averaged integrated Vapor Transport',
            'units':'kg m-1 s-1',
            'time_average': n_hrs + ' hours',
            **repeat_attrs,
            }

    f_out = path + 'ERA5_' + n_hrs + 'IVT_' + date
    ds_out.to_netcdf(path=f_out)

    return f_out

##################################################################################
