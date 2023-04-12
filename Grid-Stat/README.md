# Workflow for generating precipitation diagnostics in Grid-Stat
This template analysis is designed around the 2022-2023 DeepDive analysis, batch
processing West-WRF NRT data over a range of valid dates and forecast lead times
as an example use-case. The goal of this tutorial README is to guide how one
would work through these scripts as a workflow in order to produce forecast
skill verification statistics with StageIV data as ground truth.  This workflow
is run sequentially in order to pre-process West-WRF NRT data for ingestion into
MET, then post-processing the MET Grid-Stat ASCII text file outputs into
[Pandas](https://pandas.pydata.org/) data frames for plotting and analysis in
the [ipython conda environment](https://github.com/CW3E/MET-tools#conda-environments).

## Converting wrfout history files to cf-compliant files

Included in this workflow is the NCL script wrfout_to_cf.ncl. This is a modified
version of the original wrfout_to_cf specifically for West-WRF output that
includes added variables of IVT and precipitation. One must set output variables
to TRUE within this code to convert them into cf-compliant netcdf files. The
conversion of raw wrfout history files to cf-compliant NetCDF files is neccessary
(at this time) for compatibility with MET. However, this step will eventually
become obsolete in future WRF versions.

The modified wrfout_to_cf.ncl script ingests two `wrfout_d0?` files at different
valid times in order to compute the accumulation period over a desired interval.
Two files are needed because the, e.g., 24-hour accumulation of precipitation is
calculated by subtracting the simulation accumulation variables for rain at
t=valid time and t=valid_time-24_hours.

The wrfout_to_cf.ncl script is called on a loop in the execution of the
run_wrfout_cf.sh script included in this directory. The run_wrfout_cf.sh script
will run through a range of valid date times for zero hours and a range of forecast
hours for each valid zero hour to produce cf-compliant accumulation files. This
assumes that wrfout history files are organized according to ISO style directories
corresponding to forecast zero hours, each of the format YYYYMMDDHH. This script
requires the following configuration parameters to be defined:

 * CTR_FLW       &ndash; the name of the control flow, e.g., "NRT_gfs".
 * GRD           &ndash; the grid to be analyzed, e.g., d01 indicating the domain of the native WRF grid.
 * STRT_DT       &ndash; start date time of first forecast zero hour to be analyzed in YYYYMMDDHH format.
 * END_DT        &ndash; end date time of last forecast zero hour to be analyzed in YYYYMMDDHH format.
 * ANL_MIN       &ndash; first forecast hour to be analyzed for each forecast initial time
 * ANL_MAX       &ndash; last forecast hour to be analyzed for each forecast initial time
 * ANL_INT       &ndash; interval of forecast analyses to be performed between ANL_MIN and ANL_MAX, HH format.
 * ACC_INT       &ndash; the accumulation interval to compute precipitation over.
 * IN_CYC_DIR    &ndash; the root directory of ISO style directories for input files organizing forecast initial valid times.
 * OUT_CYC_DIR   &ndash; the root directory of ISO style directories for output files organizing forecast initial valid times.
 * RGRD          &ndash; TRUE or FALSE, whether to regrid the native WRF domain to a generic MET compatible grid.

In addition to the above required arguments, optional arguments can be supplied as follows:
 
 * IN_DT_SUBDIR  &ndash; provides the sub-path from ISO style directories to wrfout files including leading "/", e.g, "/wrfout". This can be left as a blank string if not needed.
 * OUT_DT_SUBDIR &ndash; provides the sub-path from ISO style directories to output cf-compliant files including leading "/", e.g, "/${GRD}". This can be left as a blank string if not needed.

The run_wrfout_cf.sh script is designed to be run with the batch_wrfout_cf.sh
script supplying the above arguments, as defined over a mapping of different
combinations of control flows and grids to process. For example, the settings
in the template for the batch_wrfout_cf.sh,
```{bash}
# array of control flow names to be processed
CTR_FLWS=(
          "NRT_gfs"
          "NRT_ecmwf"
         )

# model grid / domain to be processed
GRDS=( "d01" "d02" "d03" )

# define first and last date time for forecast initialization (YYYYMMDDHH)
export STRT_DT=2022121400
export END_DT=2023011800

# define the interval between forecast initializations (HH)
export CYC_INT=24

# define min / max forecast hours for forecast outputs to be processed
export ANL_MIN=24
export ANL_MAX=240

# define the interval at which to process forecast outputs (HH)
export ANL_INT=24

# define the accumulation interval for verification valid times
export ACC_INT=24
```
defines an analysis of the 24-hour precipitation accumulation for NRT_gfs
and NRT_ecmwf forecasts in domains d01, d02 and d03 for all forecast zero
hours in the range from 2022-12-14_00 to 2023-01-18_00 with initial times
at 00-Z and forecast horizons rangeing from 1 up to 10 days. This entire
analysis will be run by submitting batch_wrfout_cf.sh to the scheduler,
where each configuration corresponds to a sub-task of a SLURM job array.
In particular, there is one configuration defined for each control flow
and grid combination, meaning that the batch_wrfout_cf.sh should have
a job array defined as
```
#SBATCH --array=0-5
```
to run each sub-analysis over the date range and forecast horizons.

## Running gridstat on cf-compliant wrfout

## Running gridstat on pre-processed background data (GFS / ECMWF)

## Processing gridstat outputs

## Plotting from pickled data frames
