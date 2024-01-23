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
import ipdb

USR_HME = os.environ['USR_HME']
VRF_ROOT = os.environ['VRF_ROOT']
INDT = os.environ['INDT']

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
    for attr in precip_g.attrs:
        if attr == 'description':
            precip.attrs[attr] = 'Sum of grid- / convective-scale precipitation'

        else:
            precip.attrs[attr] = precip_g.attrs[attr] 

    precip.attrs['standard_name'] = 'total_precipitation_amount'
    precip.attrs['long_name'] = 'Accumulated Total Precipitation Over Simulation'

    valid_dt = dt.combine(pd.to_datetime(valid_dt).date(), dt.min.time())
    start_dt = dt.fromisoformat(start_dt)

    ds_out = xr.Dataset(
            data_vars=dict(
                precip=(precip.dims, precip.values),
                forecast_reference_time=(precip.dims[0], np.array([start_dt],
                    dtype='datetime64[ns]'))
                ),
            coords=dict(
                lon=(precip.dims[1:], np.squeeze(precip.XLONG.values)),
                lat=(precip.dims[1:], np.squeeze(precip.XLAT.values)),
                time=precip.XTIME.values,
                ),
            )

    ds_out.precip.attrs = precip.attrs
    ds_out.forecast_reference_time.attrs = {
         'long_name': 'Forecast Reference Time',
         'standard_name': 'forecast_reference_time',
         'valid_time': valid_dt.strftime('%Y%m%d_%H%M%S'),
         'init_time': start_dt.strftime('%Y%m%d_%H%M%S'),
         'fcst_time': ( (valid_dt - start_dt).total_seconds() / 3600 ),
         'description': 'Simulation / accumulation initial time',
        }

    return ds_out

def cf_precip_bkt(ds_curr, ds_prev):
    """Computes accumulated precip between two model times from time series.

    Inputs are precip data arrays at
    """

    precip_bkt = (ds_curr.precip - ds_prev.precip).to_dataset(name='precip_bkt')
    precip_bkt = precip_bkt.assign_coords({'time': ds_curr.time.values[0]})
    curr_dt = dt.combine(pd.to_datetime(ds_curr.time.values[0]).date(),
            dt.min.time())
    prev_dt = dt.combine(pd.to_datetime(ds_prev.time.values[0]).date(),
            dt.min.time())

    acc_inc = str((curr_dt - prev_dt).total_seconds() / 3600)
    ref_time = ds_curr.forecast_reference_time.to_dataset()
    ds_out = xr.Dataset.merge(precip_bkt, ref_time)
    ds_out.precip_bkt.attrs = {
            'standard_name': 'precipitation_amount_' + acc_inc + '_hours',
            'long_name': 'Accumulated Precipitation Over Past ' +\
                    acc_inc + ' Hours',
            'units': 'mm',
            'accum_intvl': acc_inc + ' hours',
           }

    return ds_out

##################################################################################
