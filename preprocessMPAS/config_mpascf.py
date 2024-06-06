##################################################################################
# Description
##################################################################################
# This configuration file is for settings related to parsing MET outputs into
# Python dataframes for the MET-tools workflow.
#
##################################################################################
# Imports
##################################################################################
import os
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime as dt

##################################################################################
# Utility Methods
##################################################################################

def cf_precip(ds_in, f_time=None):
    """Computes total precip from the dataset in and returns a dataset out.

    Total precip is computed from rainc + rainnc, with attributes copied from
    file, with new description and standard / long name added as attributes.
    Returns dataset with dimensions and coordinates from the original.
    """

    # unpack grid- / convective-scale precip
    precip_g = ds_in.rainnc
    precip_c = ds_in.rainc
    if f_time == None:
        valid_dt = ds_in.xtime.values[0]
        start_dt = ds_in.config_start_time

    else:
        ds_time = xr.open_dataset(f_time)
        valid_dt = ds_time.xtime.values[0]
        start_dt = ds_time.config_start_time

    precip = precip_g + precip_c

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

    # infer grid dimensions
    nlat = len(ds_in.latitude.values)
    nlon = len(ds_in.longitude.values)

    ds_out = xr.Dataset(
            data_vars=dict(
                precip=(['time', 'lat', 'lon'], np.reshape(precip.values,
                    [1, nlat, nlon])
                    ),
                forecast_reference_time=(['time'], np.array([start_nx])),
                ),
            coords=dict(
                time=(['time'], np.array([valid_nx])),
                lat=('lat', ds_in.latitude.values),
                lon=('lon', ds_in.longitude.values),
                ),
            )

    fill_val = 1e20
    ds_out.fillna(fill_val)

    ds_out.attrs = {'Conventions': 'CF-1.6'}

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
        'axis': 'T',
        }

    ds_out.lat.attrs = {
        'long_name': 'latitude',
        'standard_name': 'latitude',
        'units': 'degrees_north',
        'missing_value': fill_val,
        'axis': 'Y',
        }

    ds_out.lon.attrs = {
        'long_name': 'longitude',
        'standard_name': 'longitude',
        'units': 'degrees_east',
        'missing_value': fill_val,
        'axis': 'X',
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

    return ds_out

def cf_precip_bkt(ds_curr, ds_prev):
    """Computes accumulated precip between two model times from time series.

    Inputs are precip data arrays at
    """
    ds_out = ds_curr.rename_vars({'precip': 'precip_bkt'})
    ds_out.precip_bkt.values = ds_curr.precip.values - ds_prev.precip.values
    curr_nx = ds_curr.precip.valid_time_ut
    curr_is = ds_curr.precip.valid_time
    curr_ac = ds_curr.precip.accum_time_sec
    prev_nx = ds_prev.precip.valid_time_ut
    prev_is = ds_prev.precip.valid_time
    prev_ac = ds_prev.precip.accum_time_sec
    accu_sec = curr_ac - prev_ac

    acc_str = str(int((curr_nx - prev_nx) / 3600 ))
    fill_val = 1e20
    ds_out.precip_bkt.attrs = {
        'standard_name': 'precipitation_amount_' + acc_str + '_hours',
        'long_name': 'Accumulated Precipitation Over Past ' +\
                acc_str + ' Hours',
        'units': 'mm',
        'missing_value': fill_val,
        'valid_time': curr_is,
        'valid_time_ut': curr_nx,
        'init_time': prev_is,
        'init_time_ut': prev_nx,
        'accum_time_sec': accu_sec,
        }

    return ds_out

##################################################################################
