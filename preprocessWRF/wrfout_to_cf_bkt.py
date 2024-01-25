##################################################################################
# Description
##################################################################################
#
##################################################################################
# License Statement
##################################################################################
#
# Copyright 2023 CW3E, Contact Colin Grudzien cgrudzien@ucsd.edu
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.
# 
##################################################################################
# Imports
##################################################################################
import xarray as xr
import sys
from config_wrfcf import cf_precip, cf_precip_bkt

##################################################################################

# file name paths are taken as script arguments
f_curr = sys.argv[1]
f_prev = sys.argv[2]
f_save = sys.argv[3]

# load datasets in xarray
ds_curr = xr.open_dataset(f_curr)
ds_prev = xr.open_dataset(f_prev)

# extract cf precip
precip_curr = cf_precip(ds_curr)
precip_prev = cf_precip(ds_prev)

precip_bkt = cf_precip_bkt(precip_curr, precip_prev)

ds_out = xr.Dataset.merge(precip_curr, precip_bkt)
ds_out.time.attrs['bounds'] = 'time_bnds'
ds_out.to_netcdf(path=f_save)

#    if (out2dMet@precip_g .or. out2dMet@precip_c .or. out2dMet@precip) then
#      precip_g = (/wrfout->RAINNC/)                                ;precip_g
#        precip_g@long_name = "Accumulated Total Grid Scale Precipitation"
#        precip_g@standard_name = "large_scale_precipitation_amount"
#        precip_g@units = "mm"
#        assignVarAttCoord(precip_g,time,0,0)
#      precip_c = (/wrfout->RAINC/)                                 ;precip_c
#        precip_c@long_name = "Accumulated Total Cumulus Precipitation"
#        precip_c@standard_name = "convective_precipitation_amount"
#        precip_c@units = "mm"
#        assignVarAttCoord(precip_c,time,0,0)
#      precip = precip_g + precip_c                                ;precip
#        precip@long_name = "Accumulated Total Precipitation Over Simulation"
#        precip@standard_name = "total_precipitation_amount"
#        precip@units = "mm"
#        assignVarAttCoord(precip,time,0,0)
#    end if
#    if (out2dMet@precip_bkt) then
#      ; This is a user-defined bucket, where we read in other input files
#      precip_bkt = new((/nTime,nS_N,nW_E/), float, "No_FillValue")
#      if (fcst_time .eq. 0) then
#        precip_bkt = 0.
#        TimeDiff = 0
#      else
#        wrfout_prev = addfile(file_prev+".nc","r")
#        prev_time = wrfout_prev->Times
#        prev_time_c = wrf_times_c(prev_time, 1)
#        PrevRef = prev_time_c(0)
#        TimeDiff = tointeger(ValidRef - PrevRef)
#        pr_prev_g = (/wrfout_prev->RAINNC/)
#        pr_prev_c = (/wrfout_prev->RAINC/)
#        pr_curr_g = (/wrfout->RAINNC/)
#        pr_curr_c = (/wrfout->RAINC/)
#        precip_prev = pr_prev_g + pr_prev_c
#        precip_curr = pr_curr_g + pr_curr_c
#        precip_bkt = precip_curr - precip_prev
#     end if
#        precip_bkt@long_name = "Accumulated Precipitation Over Past "+tostring(TimeDiff)+" Hours"
#        precip_bkt@standard_name = "precipitation_amount_"+tostring(TimeDiff)+"_hours"
#        precip_bkt@units = "mm"
#        precip_bkt@accum_intvl = tostring(TimeDiff)+" hours"
#        assignVarAttCoord(precip_bkt,time,0,0)
#    end if
#
#      if (isvar("precip") .and. (out2dMet@precip)) then
#        wrfpost->precip=precip(limTime(0):limTime(1),limS_N(0):limS_N(1),  \
#                                   limW_E(0):limW_E(1))
#      if (isvar("precip_bkt")) then
#        wrfpost->precip_bkt=precip_bkt(limTime(0):limTime(1),limS_N(0):limS_N(1),  \
#                                   limW_E(0):limW_E(1))
#
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