# GridStat Tools

## Workflow for generating precipitation diagnostics
This template analysis is designed around the 2022-2023 DeepDive analysis, batch
processing West-WRF NRT data over a range of valid dates and forecast lead times
as an example use-case. The goal of this tutorial README is to guide how one
would work through these scripts as a workflow in order to produce forecast
skill verification statistics with StageIV data as ground truth.  This workflow
is run sequentially in order to pre-process West-WRF NRT data for ingestion into
MET, then post-processing the MET Grid-Stat outputs into
[Pandas](https://pandas.pydata.org/) data frames for plotting in the ipython conda
environment.

### Converting wrfout history files to cf-compliant files

Included in this workflow is the NCL scrip wrfout_to_cf.ncl.  This is a modified
version of the original wrfout_to_cf specifically for West-WRF output that
includes added variables of ivt and precipitation. You will set output variables
to TRUE within this code to convert them into cf-compliant netcdf files. The
cf-compliant files are neccessary (at this time) to import into MET, but will
become obsolete in future iterations.

The modified wrfout_to_cf.ncl script ingests two `wrfout_d0?` files at different
valid times in order to compute the accumulation period over a desired interval.
Two files are needed because the, e.g., 24-hr accumulation of precipitation is
calculated by subtracting the simulation accumulation variables for rain at
t=valid time and t=valid_time-24_hours.

### Running gridstat on cf-compliant wrfout

### Running gridstat on pre-processed background data (GFS / ECMWF)

### Processing gridstat outputs

### Plotting from pickled data frames
