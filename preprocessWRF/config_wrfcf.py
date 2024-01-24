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
import ipdb

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

    valid_dt = dt.combine(pd.to_datetime(valid_dt).date(), dt.min.time())
    start_dt = dt.fromisoformat(start_dt)
    fcst_time = ( (valid_dt - start_dt).total_seconds() / 3600 )
    ds_out = xr.Dataset(
            data_vars=dict(
                precip=(['time', 'south_north', 'west_east'], precip.values),
                forecast_reference_time=(['time'], np.array([fcst_time])),
                ),
            coords=dict(
                time=(['time'], np.array([fcst_time])),
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
        }

    ds_out.time.attrs = {
        'long_name': 'Time',
        'standard_name': 'time',
        'description': 'Valid date time of data',
        'units': 'hours since ' + start_dt.strftime('%Y-%m-%d %H:%M:%S'),
        }

    ds_out.forecast_reference_time.attrs = {
        'long_name': 'Forecast Reference Time',
        'standard_name': 'forecast_reference_time',
        'valid_time': valid_dt.strftime('%Y%m%d_%H%M%S'),
        'init_time': start_dt.strftime('%Y%m%d_%H%M%S'),
        'fcst_time': fcst_time,
        'description': 'Simulation / accumulation initial time',
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
    # KEEP DEBUGGING HERE TO DETERMINE APPROPRIATE STEPS TO GET ACCUMULATION
    curr_dt = cftime.num2pydate(ds_curr.time.values, ds_curr.time.units)[0]
    prev_dt = cftime.num2pydate(ds_prev.time.values, ds_curr.time.units)[0]

    acc_inc = int((curr_dt - prev_dt).total_seconds() / 3600)
    acc_str = str(acc_inc)
    curr_hr = int(curr_dt.total_seconds() / 3600)
    prev_hr = curr_hr - acc_inc
    fill_val = 1e20
    bnds = xr.Dataset(data_vars={'time_bnds': (['time', 'nbnds'],
        np.reshape(np.array([prev_hr, curr_hr]), [1,2]))})
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
