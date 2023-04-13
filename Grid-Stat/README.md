# Workflow for generating precipitation diagnostics in Grid-Stat
This template analysis is designed around the 2022-2023 DeepDive analysis, for
batch processing West-WRF NRT data over a range of valid dates and forecast lead
times as an example use-case. The goal of this tutorial README is to guide how one
would work through these scripts as a workflow in order to produce forecast
skill verification statistics with StageIV data as ground truth.  This workflow
is run sequentially in order to pre-process West-WRF NRT data for ingestion into
MET, and then to post-process the MET Grid-Stat ASCII text file outputs into
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

The modified `wrfout_to_cf.ncl` script ingests two `wrfout_d0?` files at different
valid times in order to compute the accumulation period over a desired interval.
Two files are needed because the, e.g., 24-hour accumulation of precipitation is
calculated by subtracting the simulation accumulation variables for rain at
t=valid time and t=valid_time-24_hours.

The `wrfout_to_cf.ncl` script is called in a loop in the execution of the
`run_wrfout_cf.sh` script included in this directory. The run_wrfout_cf.sh script
will run through a range of valid date times for zero hours and a range of forecast
hours for each valid zero hour to produce cf-compliant accumulation files. This
assumes that wrfout history files are organized according to ISO style directories
corresponding to forecast zero hours, each of the format `YYYYMMDDHH`. This script
requires the following configuration parameters to be defined:

 * `${USR_HME}`       &ndash; the directory path for the MET-tools clone.
 * `${CTR_FLW}`       &ndash; the name of the control flow, e.g., "NRT_gfs".
 * `${GRD}`           &ndash; the grid to be analyzed, e.g., `d01` indicating the domain of the native WRF grid.
 * `${STRT_DT}`       &ndash; start date time of first forecast zero hour to be analyzed in `YYYYMMDDHH` format.
 * `${END_DT}`        &ndash; end date time of last forecast zero hour to be analyzed in `YYYYMMDDHH` format.
 * `${ANL_MIN}`       &ndash; first forecast hour to be analyzed for each forecast initial time.
 * `${ANL_MAX}`       &ndash; last forecast hour to be analyzed for each forecast initial time.
 * `${ANL_INT}`       &ndash; interval of forecast analyses to be performed between `${ANL_MIN}` and `${ANL_MAX}`, `HH` format.
 * `${ACC_INT}`       &ndash; the accumulation interval to compute precipitation over in hours (values other than 24 pending testing).
 * `${IN_CYC_DIR}`    &ndash; the root directory of ISO style directories for input files organizing forecast initial valid times.
 * `${OUT_CYC_DIR}`   &ndash; the root directory of ISO style directories for output files organizing forecast initial valid times.
 * `${RGRD}`          &ndash; TRUE or FALSE, whether to regrid the native WRF domain to a generic MET compatible grid.
 * `${IN_DT_SUBDIR}`  &ndash; provides the sub-path from ISO style directories to wrfout files including leading `"/"`, e.g, `"/wrfout"`. This is left as an empty string `""` if not needed.
 * `${OUT_DT_SUBDIR}` &ndash; provides the sub-path from ISO style directories to output cf-compliant files including leading `"/"`, e.g, `"/${GRD}"`. This is left as an empty string `""` if not needed.

The `run_wrfout_cf.sh` script is designed to be run with the `batch_wrfout_cf.sh`
script supplying the above arguments, as defined over a mapping of different
combinations of control flows and grids to process. For example, the settings
in the template for the `batch_wrfout_cf.sh`,
```{bash}
# array of control flow names to be processed
CTR_FLWS=(
          "NRT_gfs"
          "NRT_ecmwf"
         )

# model grid / domain to be processed
GRDS=( 
      "d01"
      "d02"
      "d03"
     )

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
and NRT_ecmwf forecasts in domains `d01`, `d02` and `d03` for all forecast zero
hours in the range from 2022-12-14_00 to 2023-01-18_00 with initial times
at 00-Z and forecast horizons rangeing from 1 up to 10 days. Control flow
and grid combinations that do not have forecasts as long as 10 days will
be analyzed for as many forecast days are available in the source data.
This entire analysis will be run by submitting batch_wrfout_cf.sh to the
scheduler, where each configuration corresponds to a sub-task of a SLURM
job array. In particular, there is one configuration defined for each control
flow and grid combination, meaning that the `batch_wrfout_cf.sh` should have
a job array defined as
```
#SBATCH --array=0-5
```
to run each sub-analysis over the date range and forecast horizons. Outputs
from this analysis will be written to the `${OUT_ROOT}` variable defined in
the `batch_wrfout_cf.sh`, this and other settings in the job array construction
should be defined accordingly by the user. Logs for each of the SLURM array
tasks will be written in the working directory of `batch_wrfout_cf.sh`.

## Running gridstat on cf-compliant WRF outputs
Once cf-compliant outputs have been written by running the steps above, one
can ingest this data into MET using the `run_gridstat.sh` script in this
directory. This script is designed similarly to the `run_wrfout_cf.sh` script
discussed above and requires the same arguments with the addition several others
discussed in the following. MET's Grid-Stat tool settings are controlled with a 
[GridStatConfig](https://met.readthedocs.io/en/latest/Users_Guide/config_options.html)
file. This workflow generates a GridStatConfig file in the working
directory for Grid-Stat by copying and updating the fields in the
template GridStatConfigTemplate in this directory. In addition to the arguments
required in the `run_wrfout_cf.sh` script described above, `run_gridstat.sh`
requires:

 * `${VRF_FLD}`    &ndash; the verification field to be computed, currently only
    "QPF" tested / supported.
 * `${CAT_THR}`    &ndash; a list of threshold values for verfication statistics
    in mm units, e.g., `"[ >0.0, >=10.0, >=25.4, >=50.8, >=101.6 ]"`
    (including quotations).
 * `${MSK}`         &ndash; the name of the landmask polygon (including file extension)
   to be used to define the verfication region.
 * `${INT_MTHD}`   &ndash; the [interpolation method](https://met.readthedocs.io/en/latest/Users_Guide/config_options.html?highlight=nterp_mthd#interp)
   to be passed to the Grid-Stat configuration file, defining how the native model
   grid is mapped to the StageIV grid.
 * `${INT_WDTH}`   &ndash; the neighborhood width to be used for the interpolation
   to StageIV grid, in model-native grid point units.
 * `${NBRHD_WDTH}` &ndash; the neighborhood width to be used for computing
   [neighborhood statistics](https://met.readthedocs.io/en/latest/Users_Guide/grid-stat.html#neighborhood-methods)
   in Grid-Stat. Note: the GridStatConfigTemplate defaults to square neighborhoods,
   though this setting can be changed there. This workflow always computes neighborhood
   statistics using the StageIV grid, so that `${NBHD_WDTH}` corresponds to the number
   of grid points to compute, e.g., the FSS in 4km grid spaces.
 * `${BTSTRP}`     &ndash; the number of iterations that will be used for resampling to
   generate bootsrap confidence intervals. Note: this is computationally expensive
   should be turned off (set equal to `0`) to speed up rapid diagnostics.
 * `${RNK_CORR}`   &ndash; `TRUE` or `FALSE`, if
   [Spearman rank correlation](https://met.readthedocs.io/en/latest/Users_Guide/appendixC.html#spearman-rank-correlation-coefficient-rho-s)
   and
   [Kendall's Tau](https://met.readthedocs.io/en/latest/Users_Guide/appendixC.html#kendall-s-tau-statistic-tau)
   robust statistics will be computed. Note: this is computationally expensive and
   should be turned off (`FALSE`) to speed up rapid diagnostics.
 * `${CMP_ACC}`    &ndash; `TRUE` or `FALSE`, if accumulations will be computed
   by Grid-Stat. This currently must be set to `TRUE` for WRF data processedi
   in this workflow, but should be set to `FALSE` for pre-processed background
   data from global models as is discussed below.
 * `${PRFX}`       &ndash;
   [string prefix](https://met.readthedocs.io/en/latest/Users_Guide/config_options.html#output-prefix)
   to be used in Grid-Stat tool's outputs. Set to an empty string `""` if not required.
 * `${DATA_ROOT}`  &ndash; the directory path to StageIV data pre-processed for
   usage with MET. This assumes files are following naming patterns of
   `StageIV_QPE_YYYYMMDDHH.nc`.
 * `${MET_SNG}`    &ndash; full path to the executable MET singularity image to
   be used.

The run_gridstat.sh script is designed to be run with the `batch_gridstat.sh`
script supplying the above arguments as defined over a mapping of different
combinations of control flows and grids to process. Note: the performance
of the interpolation method, and the required number of gridpoints, used
to regrid WRF outputs to the StageIV grid strongly depends on the
native WRF grid. It is required that each grid to be batch processed
(`d01`/`d02`/`d03`) has a corresponding setting for the `${INT_MTHD}` and the
`${INT_WDTH}`. For example, in the `batch_gridstat.sh` template,
```{bash}
GRDS=(
      "d01"
      "d02"
      "d03"
     )

# define the interpolation method and related parameters
INT_MTHDS=(
           "DW_MEAN"
           "DW_MEAN"
           "DW_MEAN"
          )
INT_WDTHS=(
           "3"
           "9"
           "27"
          )
```
each of grids `d01`, `d02` and `d03` will used the distance-weighted mean
interpolation scheme, but the number of WRF grid points used to compute
the distance-weighted mean in the StageIV grid depends on the resolution
of `d01`, `d02` and `d03` respectively. For 9km, 3km and 1km domains, this
corresponds to taking a 27km neighborhood in the WRF domain around each
StageIV gridpoint and defining the WRF forecast as the distance-weighted
mean value over this neighborhood.

The `batch_gridstat.sh` likewise uses job arrays to submit multiple configurations
at once and run them as indices of a parameter map. The parameter
map constructor and the SLURM job array should be set like the `batch_wrf_cf.sh`
as discussed above.

## Running gridstat on pre-processed background data (GFS / ECMWF)
There are two differences in running this workflow on preprocessed
background data from global models such as GFS and the deterministic
ECMWF. Firstly, for files of the form `ECMWF_24QPF_YYYYMMDDHH_FZZZ.nc`
one does not need to run the cf compliant conversion as above for the
NRT data. Secondly, the accumulation has already been computed
in the above file. In this respect, `${CMP_ACC}` should be set equal
to `FALSE` in the batch_gridstat.sh settings above. However, in all
other respects the analysis is the same, up to defining the appropriate
paths, interpolation schemes, neighborhood sizes, etc.

## Processing gridstat outputs
The MET Grid-Stat tool used in this workflow outputs
[ASCII text files](https://met.readthedocs.io/en/latest/Users_Guide/grid-stat.html#grid-stat-output)
with naming patterns following a general form of
```
grid_stat_${PRFX}_HHMMSSL_YYYYMMDD_HHMMSSV_${STAT}.txt
```
where `${PRFX}` indicates the user-defined output prefix (if one is defined above),
`HHMMSSL` indicates the forecast lead time and `YYYYMMDD_HHMMSSV` indicates the
forecast valid time. These text files are thus organized relative to the
valid date time for the forecast zero hour, with ISO date directories located
in the `${OUT_CYC_DIR}` defined in the batch_gridstat.sh script.


## Plotting from pickled data frames
