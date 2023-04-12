# Grid-Stat Tools

## Workflow for generating precipitation diagnostics
This template analysis is designed around the 2022-2023 DeepDive analysis, batch
processing West-WRF NRT data over a range of valid dates and forecast lead times
as an example use-case. The goal of this tutorial README is to guide how one
would work through these scripts as a workflow in order to produce forecast
skill verification statistics with StageIV data as ground truth.  This workflow
is run sequentially in order to pre-process West-WRF NRT data for ingestion into
MET, then post-processing the MET Grid-Stat ASCII text file outputs into
[Pandas](https://pandas.pydata.org/) data frames for plotting and analysis in
the [ipython conda environment](https://github.com/CW3E/MET-tools#conda-environments).

### Converting wrfout history files to cf-compliant files

Included in this workflow is the NCL script wrfout_to_cf.ncl. This is a modified
version of the original wrfout_to_cf specifically for West-WRF output that
includes added variables of IVT and precipitation. One must set output variables
to TRUE within this code to convert them into cf-compliant netcdf files. The
conversion of raw wrfout history files to cf-compliant NetCDF files is neccessary
(at this time) for compatibility with MET. However, this step will eventually
become obsolete in future WRF versions.

The modified wrfout_to_cf.ncl script ingests two `wrfout_d0?` files at different
valid times in order to compute the accumulation period over a desired interval.
Two files are needed because the, e.g., 24-hr accumulation of precipitation is
calculated by subtracting the simulation accumulation variables for rain at
t=valid time and t=valid_time-24_hours.

The wrfout_to_cf.ncl script is called on a loop in the execution of the
run_wrfout_cf.sh script included in this directory. This script requires the
following configuration parameters to be defined:

 * CTR_FLW       -- the name of the control flow, e.g., "NRT_gfs".
 * GRD           -- the grid to be analyzed, e.g., d01 indicating the domain of the native WRF grid.
 * STRT_DT       -- start date time of first forecast zero hour to be analyzed in YYYYMMDDHH format.
 * END_DT        -- end date time of last forecast zero hour to be analyzed in YYYYMMDDHH format.
 * ANL_MIN       -- first forecast hour to be analyzed for each forecast initial time
 * ANL_MAX       -- last forecast hour to be analyzed for each forecast initial time
 * ANL_INT       -- interval of forecast analyses to be performed between ANL_MIN and ANL_MAX, HH format.
 * ACC_INT       -- the accumulation interval to compute precipitation over.
 * IN_CYC_DIR    -- the root directory of ISO style directories for input files organizing forecast initial valid times.
 * OUT_CYC_DIR   -- the root directory of ISO style directories for output files organizing forecast initial valid times.
 * RGRD          -- TRUE or FALSE, whether to regrid the native WRF domain to a generic MET compatible grid.

In addition to the above required arguments, optional arguments can be supplied as follows:
 
 * IN_DT_SUBDIR  -- provides the sub-path from ISO style directories to wrfout files including leading "/", e.g, "/wrfout". This can be left as a blank string if not needed.
 * OUT_DT_SUBDIR -- provides the sub-path from ISO style directories to output cf-compliant files including leading "/", e.g, "/${GRD}". This can be left as a blank string if not needed.

### Running gridstat on cf-compliant wrfout

### Running gridstat on pre-processed background data (GFS / ECMWF)

### Processing gridstat outputs

### Plotting from pickled data frames
