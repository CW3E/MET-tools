##################################################################################
# Description
##################################################################################
# This configuration file is for settings related to parsing MET outputs into
# Python dataframes for the MET-tools workflow.
#
##################################################################################
# Imports
##################################################################################
from utilities import *

##################################################################################
# Utility Methods
##################################################################################

def global_attrs(ds_in):
    # Global DS attribute
    ds_in.attrs = {
            'Conventions':'CF-1.6', 
            'notes':'Created with MET-Tools', 
            'institution':'CW3E - Scripps Institution of Oceanography',
            }

    return ds_in

def gen_attrs(ds_in, ds_out, f_time):
    """
    Function to set global xarray data attributes.
    """

    if f_time == None:
        valid_dt = ds_in.xtime.values[0]
        start_dt = ds_in.config_start_time

    else:
        ds_time = xr.open_dataset(f_time)
        valid_dt = ds_time.xtime.values[0]
        start_dt = ds_time.config_start_time
        ds_time.close()

    # we write out start / valid times in iso / unix for MET attributes
    unix_dt = dt(1970, 1, 1)
    valid_dt = dt.fromisoformat(str(valid_dt).split("'")[1].strip())
    valid_is = valid_dt.strftime('%Y%m%d_%H%M%S')
    valid_nx = int((valid_dt - unix_dt).total_seconds())

    start_dt = dt.fromisoformat(start_dt)
    start_is = start_dt.strftime('%Y%m%d_%H%M%S')
    start_nx = int((start_dt - unix_dt).total_seconds())

    # accumulations are computed from simulation inialization time
    accu_sec = valid_nx - start_nx

    # Fixes time dim and adds forecast_reference_time var
    ds_out['time'] = np.array([valid_nx])
    ds_out['forecast_reference_time'] = \
            xr.DataArray(np.array([start_nx]), dims=['time'],
                    coords=dict(time=ds_out['time']))

    # Declares fill value
    fill_val = 1e20
    ds_out.fillna(fill_val)

    # For data vars, who share these attributes
    repeat_attrs = {
            'missing_value':fill_val, 
            'valid_time':valid_is, 
            'valid_time_ut':valid_nx, 
            'init_time':start_is, 
            'init_time_ut':start_nx,
            }

    # Global ds dimension and coordinate attributes
    ds_out.time.attrs = {
        'long_name': 'Time',
        'standard_name': 'time',
        'description': 'Time',
        'units': 'seconds since 1970-01-01T00:00:00',
        'calendar': 'standard',
        'axis': 'T',
        }
    
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
    
    ds_out.forecast_reference_time.attrs = {
        'long_name': 'Forecast Reference Time',
        'standard_name': 'forecast_reference_time',
        'valid_time': valid_dt.strftime('%Y%m%d_%H0000'),
        'init_time': start_dt.strftime('%Y%m%d_%H0000'),
        'fcst_time': int(accu_sec / 3600),
        'units': 'seconds since 1970-01-01T00:00:00',
        'description': 'Simulation initial time',
        }
    
    return ds_out, repeat_attrs, accu_sec

def assign_attrs(ds_in, ds_out, f_time=None):
    """
    Function to assign attributes to new data variables.
    """

    # Sets up global dataset attributes
    ds_out, repeat_attrs, accu_sec = gen_attrs(ds_in, ds_out, f_time)

    if 'precip' in ds_out.data_vars:
        ds_out.precip.attrs = {
                'description': 'Sum of grid- / convective-scale precipitation',
                'standard_name': 'total_precipitation_amount',
                'long_name': 'Accumulated Total Precipitation Over Simulation',
                'units': 'mm',
                'accum_time_sec': accu_sec,
                **repeat_attrs
                }

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

def cf_precip(ds_in, f_time=None):
    """Computes total precip from the dataset in and returns a dataset out.

    Total precip is computed from rainc + rainnc, with attributes copied from
    file, with new description and standard / long name added as attributes.
    Returns dataset with dimensions and coordinates from the original.
    """

    # unpack grid- / convective-scale precip
    precip_g = ds_in.rainnc
    precip_c = ds_in.rainc
    precip = precip_g + precip_c

    # infer grid dimensions
    nlat = len(ds_in.latitude.values)
    nlon = len(ds_in.longitude.values)

    ds_out = xr.Dataset(
            data_vars=dict(
                precip=(['time', 'lat', 'lon'],
                    np.reshape(precip.values, [1, nlat, nlon])
                    ),
                ),
            coords=dict(
                time=(['time'], np.array([0])),
                lat=('lat', ds_in.latitude.values),
                lon=('lon', ds_in.longitude.values),
                ),
            )

    # Assigns attributes
    ds_out = assign_attrs(ds_in, ds_out, f_time)

    return ds_out

def cf_ivt(ds_in, f_time=None):
    """
    Function to calculate IVT and IWV and put into cf-compliant xarray dataset.
    """

    # Calc IVT from surface to 100hPa, extract water vapor mixing ratio [kg/kg],
    # convert to specific humidity filling with nan at null levs
    pres = ds_in['pressure']
    qv = ds_in['qv']
    q = qv / ( qv + 1.0 )
    q = np.where(pres >= 10000.0, q, np.nan)
   
    # Vertical Pa differences between layer interfaces
    d_pres = pres[:, :-1, :, :] - pres[:, 1:, :, :]

    # calculate the integral with midpoint for trapeziodal rule
    avg_q = 0.5 * (q[:, :-1, :, :] + q[:, 1:, :, :])
    IWV = np.nansum((avg_q * d_pres) / 9.81, axis=1)

    # u/v components of the wind [m/s]
    # calculate the integral with midpoint for trapeziodal rule
    u = ds_in['uReconstructZonal']
    v = ds_in['uReconstructMeridional']
    avg_u = 0.5 * (u[:, :-1, :, :] + u[:, 1:, :, :])
    avg_v = 0.5 * (v[:, :-1, :, :] + v[:, 1:, :, :])

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
