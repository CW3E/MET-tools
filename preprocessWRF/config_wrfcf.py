##################################################################################
# Description
##################################################################################
# This configuration file is for settings related to parsing MET outputs into
# Python dataframes for the MET-tools workflow.
#
##################################################################################
# SOURCE GLOBAL PARAMETERS
##################################################################################
import os
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime as dt
import cftime

##################################################################################
# Utility Methods
##################################################################################

def cf_precip(ds_in):
    """Computes total precip from the dataset in and returns a dataset out.

    Total precip is computed from rainc + rainnc, with attributes copied from
    file, with new description and standard / long name added as attributes.
    Returns dataset with dimensions and coordinates from the original.
    """

    # unpack grid- / convective-scale precip
    precip_g = ds_in.RAINNC
    precip_c = ds_in.RAINC
    valid_dt = precip_g.XTIME.values[0]
    start_dt = ds_in.START_DATE

    precip = precip_g + precip_c

    # we write out start / valid times in iso / unix for MET attributes
    unix_dt = dt(1970, 1, 1)
    valid_dt = dt.combine(pd.to_datetime(valid_dt).date(), dt.min.time())
    valid_is = valid_dt.strftime('%Y%m%d_%H%M%S')
    valid_nx = int((valid_dt - unix_dt).total_seconds())

    start_dt = dt.fromisoformat(start_dt)
    start_is = start_dt.strftime('%Y%m%d_%H%M%S')
    start_nx = int((start_dt - unix_dt).total_seconds())

    # accumulations are computed from simulation inialization time
    accu_sec = valid_nx - start_nx

    ds_out = xr.Dataset(
            data_vars=dict(
                precip=(['time', 'south_north', 'west_east'], precip.values),
                ),
            coords=dict(
                time=(['time'], np.array([valid_nx])),
                lat=(['south_north', 'west_east'],
                    np.squeeze(precip.XLAT.values)),
                lon=(['south_north', 'west_east'],
                    np.squeeze(precip.XLONG.values)),
                south_north=('south_north', precip.south_north.values),
                west_east=('west_east', precip.west_east.values),
                ),
            )

    fill_val = 1e20
    ds_out.fillna(fill_val)

    ds_out.precip.attrs = {
        'description': 'Sum of grid- / convective-scale precipitation',
        'standard_name': 'total_precipitation_amount',
        'long_name': 'Accumulated Total Precipitation Over Simulation',
        'units': 'mm',
        'missing_value': fill_val,
        'valid_time': valid_is,
        'valid_time_ut': valid_nx,
        'init_time': start_is,
        'init_time_ut': start_nx,
        'accum_time_sec': accu_sec,
        }

    ds_out.time.attrs = {
        'long_name': 'Time',
        'standard_name': 'time',
        'description': 'Time',
        'units': 'seconds since 1970-01-01T00:00:00',
        'calendar': 'standard',
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

    return ds_out

def cf_precip_bkt(ds_curr, ds_prev):
    """Computes accumulated precip between two model times from time series.

    Inputs are precip data arrays at
    """
    ds_out = ds_curr.rename_vars({'precip': 'precip_bkt'})
    ds_out.precip_bkt.values = ds_curr.precip.values - ds_prev.precip.values
    curr_hr = ds_curr.time.values[0]
    prev_hr = ds_prev.time.values[0]

    acc_inc = int(curr_hr - prev_hr)
    acc_str = str(acc_inc)
    fill_val = 1e20
    bnds = xr.Dataset(data_vars={'time_bnds': (['time', 'nbnds'],
        np.reshape(np.array([prev_hr, curr_hr]), [1,2]))})

    ds_out = xr.Dataset.merge(ds_out, bnds)
    ds_out.precip_bkt.attrs = {
            'standard_name': 'precipitation_amount_' + acc_str + '_hours',
            'long_name': 'Accumulated Precipitation Over Past ' +\
                    acc_str + ' Hours',
            'units': 'mm',
            'accum_intvl': acc_str + ' hours',
            'missing_value': fill_val,
            'cell_methods': 'time: sum',
           }

    ds_out.time.attrs['bounds'] = 'time_bnds'

    return ds_out

##################################################################################
