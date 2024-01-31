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
import os
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime as dt

##################################################################################
# Utility definitions
##################################################################################
# regridding values for CDO
GRES='global_0.08'
LAT1=5.
LAT2=65.
LON1=162.
LON2=272.

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
                forecast_reference_time=(['time'], np.array([start_nx])),
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
# Old NCL to be converted for further fields

#    ;  Note: process both IVT and IWV, even if only one is specified
#    if (out2dRadFlx@IVT .or. out2dRadFlx@IWV .or. out2dRadFlx@IVTU .or. out2dRadFlx@IVTV) then
#      ; -create the variable
#      IVT = new((/nTime,nS_N,nW_E/), float, "No_FillValue")    ;IVT
#      IWV = new((/nTime,nS_N,nW_E/), float, "No_FillValue")    ;IWV
#      IVTU = new((/nTime,nS_N,nW_E/), float, "No_FillValue")    ;IVTU
#      IVTV = new((/nTime,nS_N,nW_E/), float, "No_FillValue")    ;IVTV
#      IVT = 0.
#      IWV = 0.
#      IVTU = 0.
#      IVTV = 0.
#      ; -loop through the nTimes
#      do n = 0, nTime-1
#        ; -create the variables (does not include time dimension)
#        p_eta = new((/nEta,nS_N,nW_E/), float, "No_FillValue")
#        p_int = new((/nEta+1,nS_N,nW_E/), float, "No_FillValue")
#        p_surf = new((/nS_N,nW_E/), float, "No_FillValue")
#        d_pres = new((/nS_N,nW_E/), float, "No_FillValue")
#        r_v_eta = new((/nEta,nS_N,nW_E/), float)
#        u_gr = new((/nEta,nS_N,nW_E/), float)
#        v_gr = new((/nEta,nS_N,nW_E/), float)
#        ; -read in the values needed for calculations
#        p_eta = (/wrf_user_getvar(wrfout,"pressure",n)/)*100.
#        p_surf = (/wrfout->PSFC(n,:,:)/)
#        u_gr = (/wrf_user_getvar(wrfout,"ua",n)/)
#        v_gr = (/wrf_user_getvar(wrfout,"va",n)/)
#        p_tp_in = (/wrfout->P_TOP/)     ;pressure at top of model
#        ;in some files P_TOP has two dimensions, in some it has one dimension
#        if ((dimsizes(dimsizes(p_tp_in))) .eq. 2) then
#          p_tp = p_tp_in(0,0)
#        else
#          p_tp = p_tp_in(0)
#        end if
#        ;r_v_eta = (/wrfout->QVAPOR(n,:,:,:)/)
#        r_v_eta = (/(wrfout->QVAPOR(n,:,:,:)/(wrfout->QVAPOR(n,:,:,:)+1.))/)
#        ; -calculate the pressure at the intersection between eta levels
#        p_int(0,:,:) = p_surf
#        p_int(nEta,:,:) = p_tp
#        do k = 1, nEta-1
#          p_int(k,:,:) = (p_eta(k-1,:,:)+p_eta(k,:,:))*0.5
#        end do
#        ; -loop through the nEta
#        do k = 0, nEta-1
#          ; -calculate the difference in pressure between eta levels
#          d_pres = p_int(k,:,:) - p_int(k+1,:,:)
#          ; -calculate the IVT and IWV
#          IWV(n,:,:) = IWV(n,:,:) + (r_v_eta(k,:,:)*d_pres/9.81)
#          IVTU(n,:,:) = IVTU(n,:,:) + (r_v_eta(k,:,:)*d_pres*u_gr(k,:,:)/9.81)
#          IVTV(n,:,:) = IVTV(n,:,:) + (r_v_eta(k,:,:)*d_pres*v_gr(k,:,:)/9.81)
#        end do
#      IVT(n,:,:) = sqrt((IVTU(n,:,:)^2.)+(IVTV(n,:,:)^2.))
#      end do
#      ; -set the attributes
#      IVT@long_name = "Integrated Vapor Transport"
#        IVT@standard_name = "integrated_vapor_transport"
#        IVT@units = "kg m-1 s-1"
#        IVT@notes = "Column-integrated vapor transport"
#        assignVarAttCoord(IVT,time,0,0)      ;IVT
#      IWV@long_name = "Integrated Water Vapor"
#        IWV@standard_name = "integrated_water_vapor"
#        IWV@units = "kg m-2"
#        IWV@notes = "Column-integrated water vapor"
#        assignVarAttCoord(IWV,time,0,0)      ;IWV
#      IVTU@long_name = "Integrated Vapor Transport U-component"
#        IVTU@standard_name = "integrated_vapor_transport_u"
#        IVTU@units = "kg m-1 s-1"
#        IVTU@notes = "Column-integrated vapor transport u-component"
#        assignVarAttCoord(IVTU,time,0,0)      ;IVTU
#      IVTV@long_name = "Integrated Vapor Transport V-component"
#        IVTV@standard_name = "integrated_vapor_transport_v"
#        IVTV@units = "kg m-1 s-1"
#        IVTV@notes = "Column-integrated vapor transport v-component"
#        assignVarAttCoord(IVTV,time,0,0)      ;IVTV
#    end if
#  end if
#  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
#
#      if (isvar("IVT") .and. (out2dRadFlx@IVT)) then
#        wrfpost->IVT=IVT(limTime(0):limTime(1),limS_N(0):limS_N(1),  \
#                           limW_E(0):limW_E(1))
#      end if
#      if (isvar("IWV") .and. (out2dRadFlx@IWV)) then
#        wrfpost->IWV=IWV(limTime(0):limTime(1),limS_N(0):limS_N(1),  \
#                           limW_E(0):limW_E(1))
#      end if
#      if (isvar("IVTU") .and. (out2dRadFlx@IVTU)) then
#        wrfpost->IVTU=IVTU(limTime(0):limTime(1),limS_N(0):limS_N(1),  \
#                           limW_E(0):limW_E(1))
#      end if
#      if (isvar("IVTV") .and. (out2dRadFlx@IVTV)) then
#        wrfpost->IVTV=IVTV(limTime(0):limTime(1),limS_N(0):limS_N(1),  \
#                           limW_E(0):limW_E(1))
#      end if
