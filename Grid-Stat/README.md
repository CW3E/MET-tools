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

## Workflow configuration files
For this workflow, environmental variables have been defined in two 
configuration files: `pre_processing_config.sh` for the shell scripts and 
`post_processing_config.py` for the Python scripts. In these files, any shared variables
among scripts will be defined in the respective configuration file. Most global 
parameters are defined in the configuration file, with some exceptions for 
script-dependent variables (such as `IN_ROOT` or `OUT_ROOT`). These files 
are divided into three sections for user efficiency:

* Global parameters to be set                   &ndash; location for environmental variables that are user-dependent.
* Global parameters that may need to change     &ndash; location for environmental variables that may need to be changed by the user before use depending on the desired output.
* Global parameters that won't change           &ndash; location for environmental variables that probably won't need to be changed by the user before use.

For the shell scripts, the required variables are referenced at the top of each script 
through the command `source pre_processing_config.sh`.
For the Python scripts, the required variables are referenced in the import section of 
each script by the command `import post_processing_config as config`.

For more information on how these configuration files were made and implemented into this 
workflow, refer to the [Research Code Portability Tutorial repository](https://github.com/CW3E/Research-Code-Portability-Tutorial/tree/main).

Environmental variables needed for this workflow are described in the subsequent sections.

## Converting wrfout history files to cf-compliant files
Included in this workflow is the NCL script `wrfout_to_cf.ncl`. This is a modified
version of the original `wrfout_to_cf.ncl` specifically for West-WRF output that
includes added variables of IVT and precipitation. One must set output variables
to `TRUE` within this code to convert them into cf-compliant netcdf files. The
conversion of raw wrfout history files to cf-compliant NetCDF files is neccessary
(at this time) for compatibility with MET. However, this step will eventually
become obsolete in future WRF versions.

The modified `wrfout_to_cf.ncl` script ingests two `wrfout_d0?` files at different
valid times in order to compute the accumulation period over a desired interval.
Two files are needed because the, e.g., 24-hour accumulation of precipitation is
calculated by subtracting the simulation accumulation variables for rain at
t=valid_time and t=valid_time-24_hours. 

### Running cf-compliant batch processing
The `wrfout_to_cf.ncl` script is called in a loop in the execution of the
`run_wrfout_cf.sh` script included in this directory. The `run_wrfout_cf.sh` script
will run through a range of valid date times for zero hours and a range of forecast
hours for each valid zero hour to produce cf-compliant accumulation files. This
assumes that wrfout history files are organized according to ISO style directories
corresponding to forecast zero hours, each of the format `YYYYMMDDHH`. This script
requires the following configuration parameters to be defined:

 * `${USR_HME}`       &ndash; the directory path for the MET-tools clone.
 * `${CTR_FLW}`       &ndash; the name of the control flow, e.g., `"NRT_gfs"`.
 * `${GRD}`           &ndash; the grid to be analyzed, e.g., `d01` indicating the domain of the native WRF grid.
 * `${STRT_DT}`       &ndash; start date time of first forecast zero hour to be analyzed in `YYYYMMDDHH` format.
 * `${END_DT}`        &ndash; end date time of last forecast zero hour to be analyzed in `YYYYMMDDHH` format.
 * `${ANL_MIN}`       &ndash; first forecast hour to be analyzed for each forecast initial time.
 * `${ANL_MAX}`       &ndash; last forecast hour to be analyzed for each forecast initial time.
 * `${ANL_INT}`       &ndash; interval of forecast analyses to be performed between `${ANL_MIN}` and `${ANL_MAX}`, `HH` format.
 * `${ACC_INT}`       &ndash; the accumulation interval to compute precipitation over in hours (values other than `24` pending testing).
 * `${IN_CYC_DIR}`    &ndash; the root directory of ISO style directories for input files organizing forecast initial valid times.
 * `${OUT_CYC_DIR}`   &ndash; the root directory of ISO style directories for output files organizing forecast initial valid times.
 * `${IN_DT_SUBDIR}`  &ndash; provides the sub-path from ISO style directories to
   wrfout files including leading `"/"`, e.g, `"/wrfout"`. This is left as an empty string `""` if not needed.
 * `${OUT_DT_SUBDIR}` &ndash; provides the sub-path from ISO style directories to output cf-compliant files including leading `"/"`, e.g, `"/${GRD}"`. This is left as an empty string `""` if not needed.
 * `${RGRD}`          &ndash; `TRUE` or `FALSE`, whether to regrid the native WRF domain to a generic
   MET compatible lat-lon grid.

The `run_wrfout_cf.sh` script is designed to be run with the `batch_wrfout_cf.sh`
script supplying the above arguments by sourcing `pre_processing_config.sh`, as 
defined over a mapping of different combinations of control flows and grids to 
process. For example, the settings in the template for the `pre_processing_config.sh`,
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
This entire analysis will be run by submitting `batch_wrfout_cf.sh` to the
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
tasks will be written in `${OUT_ROOT}` defined in `batch_wrfout_cf.sh`.

## Generating Regional Landmasks for verification
In order to calculate relevant verification statistics, one should pre-generate
a landmask for the region over which the verification is to take place. This
region will be defined as a sub-domain of the StageIV grid, which can be generated
in the following steps.


### Generating user-defined lat-lon regions from Google Earth

Naming of the lat-lon text files should be of the form
```
Mask_Name.txt
```
where the `Mask_Name` will match the mask's printed name in plotting routines,
with underscores corresponding to blank spaces - these underscores are parsed in
the plotting scripts when defining the printed name with spaces. The
formatting of the file should have the `Mask_Name` as the first line of
the file. Each line after the first corresponds to a latitude-longitude pair
defining the polygon region to be verified, with paired values separated by
a single blank space.

A variety of commonly used lat-lon regions are included in the
```
MET-tools/polygons/lat-lon
```
directory in this repository, which can be used to generate the NetCDF landmasks
for the verification region in the StageIV grid. New lat-lon files can be added
to this directory without changing the behavior of existing workflow routines.

### Computing NetCDF landmasks from lat-lon text files

In order to define a collection of landmasks to perform verification over,
one will define a landmask list which will be sourced by the `run_vxmask.sh`
and `run_gridstat.sh` scripts in the following. A landmask list is a text file
with lines consisting of each `Mask_Name` region over which to perform
verfication. Example landmask lists can be found in the
```
MET-tools/polygons/mask-lists
```
directory.

The NetCDF landmasks that will be ingested by Grid-Stat are generated
with the `run_vxmask.sh` script. This script is run offline and standalone, where
the output NetCDF masks can be re-used over multiple analyses that study the same
verification regions. The required arguments of the `run_vxmask.sh` script are as follows:

 * `${USR_HME}`       &ndash; the directory path for the MET-tools clone.
 * `${SOFT_ROOT}`     &ndash; the directory path for the MET singularity image.
 * `${MET_SNG}`       &ndash; the full path of the MET singularity image.
 * `${MSK_ROOT}`      &ndash; the directory path for the root directorie containing lat-lon, landmask list and landmask NetCDF files.
 * `${MSKS}`          &ndash; the full path of the landmask list file to be sourced.
 * `${MSK_IN}`        &ndash; the directory path of the lat-lon files to be used for generating landmasks.
 * `${MSK_OUT}`       &ndash; the directory path for the output NetCDF landmasks.
 * `${OBS_F_IN}`      &ndash; the full path of a processed StageIV product for the reference grid.

In this repository, a generic StageIV product is included in the following path:
```
MET-tools/polygonsStageIV_QPE_2019021500.nc
```
which can be used for the `${OBS_F_IN}` above as the reference grid for
generating landmasks.

## Running Grid-Stat
Once cf-compliant outputs and verification landmasks have been written by
running the steps above, one can ingest this data into MET using the
`run_gridstat.sh` script in this directory. This script is designed similarly
to the `run_wrfout_cf.sh` script discussed above and requires the same
arguments with the addition several others. MET's Grid-Stat tool settings
are controlled with a 
[GridStatConfig](https://met.readthedocs.io/en/latest/Users_Guide/config_options.html)
file. This workflow generates a GridStatConfig file in the working
directory for Grid-Stat by copying and updating the fields in the
template
[GridStatConfigTemplate](https://github.com/CW3E/MET-tools/blob/main/Grid-Stat/GridStatConfigTemplate)
in this directory. In addition to the arguments
required in the `run_wrfout_cf.sh` script described above, `run_gridstat.sh`
requires:

 * `${VRF_FLD}`    &ndash; the verification field to be computed, currently only
    `QPF` tested / supported.
 * `${CAT_THR}`    &ndash; a list of threshold values for verfication statistics
    in mm units, e.g., `"[ >0.0, >=10.0, >=25.4, >=50.8, >=101.6 ]"`
    (including quotations).
 * `${MSKS}`       &ndash; the full path to the landmask list to be used to define the verfication region(s) for Grid-Stat.
 * `${MSK_IN}`     &ndash; the directory path to the NetCDF landmasks sourced in the landmask list `${MSKS}`.
 * `${INT_MTHD}`   &ndash; the [interpolation method](https://met.readthedocs.io/en/latest/Users_Guide/config_options.html?highlight=nterp_mthd#interp)
   to be passed to the Grid-Stat configuration file, defining how the native model
   grid is mapped to the StageIV grid.
 * `${INT_WDTH}`   &ndash; the neighborhood width to be used for the interpolation
   to StageIV grid, in model-native grid point units.
 * `${NBRHD_WDTH}` &ndash; the neighborhood width to be used for computing
   [neighborhood statistics](https://met.readthedocs.io/en/latest/Users_Guide/grid-stat.html#neighborhood-methods)
   in Grid-Stat. Note: the GridStatConfigTemplate defaults to square neighborhoods,
   though this setting can be changed therein. This workflow always computes neighborhood
   statistics using the StageIV grid, so that `${NBHD_WDTH}` corresponds to the number
   of grid points to compute, e.g., the FSS, in 4km grid spaces.
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
   by Grid-Stat. This currently must be set to `TRUE` for WRF data processed
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

### Running gridstat batch analysis on cf-compliant WRF outputs

The `run_gridstat.sh` script is designed to be run with the `batch_gridstat.sh`
script sourcing `pre_processing_config.sh` and supplying the above arguments 
as defined over a mapping of different combinations of control flows and grids 
to process. Note: the performance of the interpolation method, and the required 
number of gridpoints, used to regrid WRF outputs to the StageIV grid strongly 
depends on the native WRF grid. It is required that each grid to be batch processed
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
corresponds in each analysis to taking a 27km neighborhood in the WRF domain
around each StageIV gridpoint and defining the WRF forecast as the
distance-weighted mean value over this neighborhood.

The `batch_gridstat.sh` likewise uses job arrays to submit multiple configurations
at once and run them as indices of a parameter map. The parameter
map constructor and the SLURM job array should be set like the `batch_wrf_cf.sh`
as discussed above. Logs for `batch_gridstat.sh` will be written in
the `${OUT_ROOT}` directory set in the script.

### Running gridstat batch analysis on pre-processed background data (GFS / ECMWF)
There are two differences in running this workflow on preprocessed
background data from global models such as GFS and the deterministic
ECMWF. Firstly, for files of the form `*_24QPF_YYYYMMDDHH_FZZZ.nc`
one does not need to run the cf-compliant conversion as above for the
NRT data. Secondly, the accumulation has already been computed
in the above file. In this respect, `${CMP_ACC}` should be set equal
to `FALSE` in the `batch_gridstat.sh` settings above. However, in all
other respects the analysis is the same, up to defining the appropriate
paths, interpolation schemes, neighborhood sizes, etc.

## Processing Grid-Stat outputs
The MET Grid-Stat tool used in this workflow writes outputs to
[ASCII text files](https://met.readthedocs.io/en/latest/Users_Guide/grid-stat.html#grid-stat-output)
with naming patterns following a general form of
```
grid_stat_${PRFX}_HHMMSSL_YYYYMMDD_HHMMSSV_${STAT}.txt
```
where `${PRFX}` indicates the user-defined output prefix (if one is defined above),
`HHMMSSL` indicates the forecast lead time and `YYYYMMDD_HHMMSSV` indicates the
forecast valid time and `${STAT}` is a category of statistics that are contained
in the given file. These text files are thus organized relative to the
valid date time for the forecast zero hour, with ISO date directories located
in the `${OUT_CYC_DIR}` defined for each control flow in the `batch_gridstat.sh`
script. In this workflow, the Grid-Stat outputs for each domain for a given
control flow are organized into a sub-directory of the ISO named directory for the
forecast zero hour, e.g.,
```
/cw3e/mead/projects/cwp106/scratch/DeepDive/NRT_gfs/2022121400/d01
```
contains the `grid_stat_*.txt` files for all `d01` forecasts up to the
`${ANL_MAX}` time that are initialized at `2022121400`.

These Grid-Stat text files are human-readable as column-organized data. In
order to parse the text into a statistical and graphical language, this
workflow has implemented the `proc_gridstat.py` script to efficiently batch
process all control flows, statisics types, domains and valid dates for forecast
zero hours in parallel, while looping over forecast hours for each zero. Parallelism
is acheived using
[Python multiprocessing](https://docs.python.org/3/library/multiprocessing.html).
This script requires the following arguments:

 * `CTR_FLWS` &ndash; a list of all control flows to be processed.
 * `CSE`      &ndash; the name of the case study being performed.
 * `GRDS`     &ndash; the model grids to be processed.
 * `START_DT` &ndash; the first valid date time for a forecast to be processed
   (`YYYYMMDDHH` format).
 * `END_DT`   &ndash; the last valid date time for a forecast to be processed
   (`YYYYMMDDHH` format).
 * `CYC_INT`  &ndash; the interval between valid date times to be processed.
 * `PRFXS`    &ndash; a list of all prefixes for Grid-Stat output files to be processed.
 * `IN_ROOT`  &ndash; the directory path for all control flow-named directories containing
   Grid-Stat outputs to be processed.
 * `OUT_ROOT` &ndash; the directory path for all `proc_gridstat.py` outputs to be
   written, sub-organized by control flow names and ISO start date directories. 

Note that this script generates a mapping for a parallel analysis over control flow,
grid, prefix and valid start date, where IO directories may depend on these parameters.
In order to handle this dependency, one should edit the arguments that are mapped
to the `proc_gridstat` function defined in the script, where configurations are
defined in terms of Python lists of arguments, constructed in the nested loops before
the parameter map.

With the parameters appropriately set as above, one can call `proc_gridstat.py` 
using the Singularity conatiner as
```
singularity exec --bind /cw3e:/cw3e,/scratch:/scratch /cw3e/mead/projects/cwp106/scratch/MET_tools_conda_ipython.sif python /path/to/proc_gridstat.py
```
to parse all files available within these directories. 

If one was not using the containers, they can call `proc_gridstat.py` as
```
python -u proc_gridstat.py
```

Note: the -u flag is is optional and is only to set this to write logs in real-time 
instead of at the time of script completion.

The `proc_gridstat.py` script is designed to be agnostic of what statistics are 
available at each directory, using [glob](https://docs.python.org/3/library/glob.html) and
Bash wildcards to search for any files available matching the specified patterns.
Valid start dates are processed in parallel for start dates between `START_DT` and `END_DT`
at step sizes `CYC_INT` between these dates.  For each file of the type
```
grid_stat_${PRFX}_HHMMSSL_YYYYMMDD_HHMMSSV_${STAT}.txt
```
the `${STAT}` variable will be read as the key name for a
[Python dictionary](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
entry, with a matching value equal to a [Pandas](https://pandas.pydata.org/)
dataframe which inherits all column names and values from the corresponding
ASCII file. 

One output data file and one log file is generated per valid start date, of the form
```
grid_stats_d0?_YYYYMMDDHH.bin
proc_gridstat_NRT_*_d0?_YYYYMMDDHH.log
```
respectively. Logs for `proc_gridstat.py` are written in `OUT_ROOT + '/batch_logs'`
while data outputs are written to corresponding ISO start date directories by default.
Statistics for distinct forecast leads are processed sequentially and increasing in
forecast length for each valid start date. New files with type `${STAT}` are parsed
and concatenated vertically to an existing `${STAT}` dataframe associated to the
dictionary key `${STAT}` if it already exists, or this will be newly created if it does
not exist already.  This script also filters missing values, replacing them with entries of
[Numpy NaN](https://numpy.org/doc/stable/reference/constants.html#numpy.NAN)
for later analysis and suppression of entries during plotting.

The `*.bin` files are binary files containing
[Python pickled](https://docs.python.org/3/library/pickle.html)
binary data, where the above dictionaries of dataframes are serialized,
preserving the full object structure discussed above. To open such a file,
one needs to unpickle the contents of this file, e.g., in a Python script or
interactive session one may write
```{python}
import pickle
import pandas as pd
with open('grid_stats_d01_2022121400.bin', 'rb') as f:
    gridstat_data = pickle.load(f)
```
where the variable `gridstat_data` now references our dictionary of dataframes.
To view the dataframe key names which call the parsed data, one may write
```{python}
gridstat_data.keys()
Out: dict_keys(['cnt', 'ctc', 'cts', 'fho', 'nbrcnt', 'nbrctc', 'nbrcts'])
```
To, e.g., call the dataframe of neighborhood continuous statistics, one may call
```{python}
nbrcnt = gridstat_data['nbrcnt']
```
and work with the `nbrcnt` variable to analyze and plot the data.

## Plotting from pickled data frames
Several examples of plottting from processed gridstat data binary files
```{bash}
grid_stats_${GRD}_YYYYMMDDHH.bin
```
are provided, where the plotting routines therein are integrated to this
workflow. Specifically, all scripts import the path variable
```{python}
from proc_gridstat import OUT_ROOT 
```
so that the path to the binary files can be used for sourcing the data
and writing out saved figures automatically. Secondly, plotting routines
are designed to be robust to missing data, and to non-existing configurations
while looping over various combinations of control flows, grids and
valid dates / lead times for verification. Discussing all options in these
routines is beyond the current scope of the documentation and it is recommended
instead to follow the steps up to this point, and to learn the plotting features
from running the `plot_*.py` scripts and changing the options within the 
`post_plotting_config.py` script. For specific, publication-quality figures, 
it is expected that a user will modify these scripts themselves to set the needed 
stylistic options, etc. These are templates only, and performing a specific study 
may involve rewriting these templates to one's own needs.

To run any respective plotting script using the Singularity container, one 
can use the following command
```
singularity exec --bind /cw3e:/cw3e,/scratch:/scratch /cw3e/mead/projects/cwp106/scratch/MET_tools_conda_ipython.sif python /path/to/scripts/python_plotting_script.py
```

> Currently, the plotting scripts are not designed for live plotting due to restrictions involving the iPython Singularity container. 
> A solution to this issue depends on factors involving the move to Expanse, but work will be done down the line to fix this.
