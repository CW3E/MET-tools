##################################################################################
# Description
##################################################################################
# This module defines standalone methods for converting fields from wrfout history
# files parsed as xarray datastructures into cf-compliant datastructures for
# saving as NetCDF. These methods are meant to take raw datasets read in from
# raw wrfout files as xarrays and return datasets that can be merged for a final
# product in a wrapping script.
#
# This is based on NCL script wrfout_to_cf.ncl of Mark Seefeldt and others:
#
#    http://foehn.colorado.edu/wrfout_to_cf/
#
##################################################################################
# Imports
##################################################################################
from utilities import *

##################################################################################
# Utility definitions
##################################################################################
# regridding values for CDO
# NOTE: need to revise to regrid directly to verification grid
GRES='global_0.08'
LAT1=5.
LAT2=65.
LON1=162.
LON2=272.

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

def unstagger(var, stagger_dim):
    """
    Function copied from WRF-python to unstagger variables.

    This function destaggers the variable by taking the average of the
    values located on either side of the grid box.

    Args:

        var (:class:`xarray.DataArray` or :class:`numpy.ndarray`): A variable
            on a staggered grid.

        stagger_dim (:obj:`int`): The dimension index to destagger.
            Negative values can be used to choose dimensions referenced
            from the right hand side (-1 is the rightmost dimension).

    Returns:
        :class:`numpy.ndarray` object with no metadata.
    """

    var_shape = var.shape
    num_dims = var.ndim
    stagger_dim_size = var_shape[stagger_dim]
    
    full_slice = slice(None)
    slice1 = slice(0, stagger_dim_size - 1, 1)
    slice2 = slice(1, stagger_dim_size, 1)
    
    # default to full slices
    dim_ranges_1 = [full_slice] * num_dims
    dim_ranges_2 = [full_slice] * num_dims
    
    # for the stagger dim, insert the appropriate slice range
    dim_ranges_1[stagger_dim] = slice1
    dim_ranges_2[stagger_dim] = slice2
    
    result = 0.5*(var[tuple(dim_ranges_1)] + var[tuple(dim_ranges_2)])

    return result

def unstagger_uv(u, v):
    """
    Function to calculate unstaggered u and v wind components.
    """

    # Extracts attributes to repopulate later
    u_attrs = u.attrs
    v_attrs = v.attrs

    unstag_u = unstagger(u, -1)
    unstag_v = unstagger(v, -2)

    # Fixes metadata
    unstag_u = unstag_u.swap_dims({'west_east_stag':'west_east'})
    unstag_v = unstag_v.swap_dims({'south_north_stag':'south_north'})

    unstag_u.attrs = u_attrs
    del unstag_u.attrs['stagger']

    unstag_v.attrs = v_attrs
    del unstag_v.attrs['stagger']

    return unstag_u, unstag_v

def gen_attrs(ds_in, ds_out, init_offset=0):
    """
    Function to set global xarray data attributes.
    """
    
    # Time vars
    valid_dt = ds_in.XTIME.values[0]
    start_dt = ds_in.START_DATE

    # we write out start / valid times in iso / unix for MET attributes
    unix_dt = dt(1970, 1, 1)
    valid_dt = pd.to_datetime(valid_dt)
    valid_is = valid_dt.strftime('%Y%m%d_%H%M%S')
    valid_nx = int((valid_dt - unix_dt).total_seconds())

    start_dt = dt.fromisoformat(start_dt) - td(hours=init_offset)
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

    # Global DS attributes
    ds_out.attrs = {
            'Conventions':'CF-1.6', 
            'notes':'Created with MET-Tools', 
            'institution':'CW3E - Scripps Institution of Oceanography',
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
        }
    
    ds_out.lon.attrs = {
        'long_name': 'Longitude',
        'standard_name': 'longitude',
        'units': 'degrees_east',
        'missing_value': fill_val,
        }
    
    ds_out.south_north.attrs = {
        'long_name': 'y coordinate of projection',
        'standard_name': 'projection_y_coordinate',
        'axis': 'Y',
        'units': 'none',
        }
    
    ds_out.west_east.attrs = {
        'long_name': 'x coordinate of projection',
        'standard_name': 'projection_x_coordinate',
        'axis': 'X',
        'units': 'none',
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

def assign_attrs(ds_in, ds_out, init_offset=0):
    """
    Function to assign attributes to new data variables.
    """

    # Sets up global WRF dataset attributes
    ds_out, repeat_attrs, accu_sec = gen_attrs(ds_in, ds_out, init_offset)

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

def cf_precip(ds_in, init_offset=0):
    """Computes total precip from the dataset in and returns a dataset out.

    Total precip is computed from rainc + rainnc, with attributes copied from
    file, with new description and standard / long name added as attributes.
    Returns dataset with dimensions and coordinates from the original.

    For simulations that are run from a restart, the init time will differ from
    the original initialization.  There is an optional parameter used to
    offset the init time by the restart interval.
    """

    # unpack grid- / convective-scale precip
    precip_g = ds_in.RAINNC
    precip_c = ds_in.RAINC
    precip = precip_g + precip_c

    ds_out = xr.Dataset(
            data_vars=dict(
                precip=(['time', 'south_north', 'west_east'], precip.values),
                ),
            coords=dict(
                time=(['time'], np.array([0])),
                lat=(['south_north', 'west_east'],
                    np.squeeze(precip.XLAT.values)),
                lon=(['south_north', 'west_east'],
                    np.squeeze(precip.XLONG.values)),
                south_north=('south_north', precip.south_north.values),
                west_east=('west_east', precip.west_east.values),
                ),
            )

    # Assigns attributes
    ds_out = assign_attrs(ds_in, ds_out, init_offset)

    return ds_out

def cf_ivt(ds_in, init_offset=0):
    """
    Function to calculate IVT and IVW and put into cf-compliant xarray dataset.
    """

    # Calculate pressure in Pa at the layer interfaces, replacing surface / top
    p_eta = (ds_in.P + ds_in.PB) * 100
    p_surf = ds_in.PSFC
    p_top = ds_in.P_TOP
    pres = (p_eta + np.roll(p_eta, 1, axis=1))*0.5
    pres[:, 0, :, :] = p_surf
    pres[:, -1, :, :] = p_top

    # Calc IVT from surface to 100hPa, extract water vapor mixing ratio [kg/kg]
    # convert to specific humidity filling with nan at null levs
    qv = ds_in.QVAPOR
    q = qv / ( qv + 1.0 )
    q = np.where(pres >= 10000.0, q, np.nan)

    # Vertical Pa differences between layer interfaces
    d_pres = pres[:, :-1, :, :] - pres[:, 1:, :, :]

    # calculate the integral with average for trapeziodal rule
    avg_q = 0.5 * (q[:, :-1, :, :] + q[:, 1:, :, :])
    IWV = np.nansum((avg_q * d_pres) / 9.81, axis=1)

    # generate u/v components of the unstaggered wind [m/s]
    # calculate the integral with average for trapeziodal rule
    u, v = unstagger_uv(ds_in.U, ds_in.V)
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
                IWV=(['time', 'south_north', 'west_east'], IWV),
                IVT=(['time', 'south_north', 'west_east'], IVT),
                IVTU=(['time', 'south_north', 'west_east'], IVTU),
                IVTV=(['time', 'south_north', 'west_east'], IVTV)
                ),
            coords = dict(
                time = (['time'], np.array([0])),
                lat = (['south_north', 'west_east'],
                    np.squeeze(ds_in.XLAT.values)),
                lon = (['south_north', 'west_east'],
                    np.squeeze(ds_in.XLONG.values)),
                south_north = ('south_north', ds_in.south_north.values),
                west_east = ('west_east', ds_in.west_east.values),
                ),
            )

    # Assigns attributes
    ds_out = assign_attrs(ds_in, ds_out, init_offset)

    return ds_out

##################################################################################
