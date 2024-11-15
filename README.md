# MET-tools

## Description
This is a workflow template for batch processing numerical weather prediction (NWP) data with the 
[Model Evaluation Tools (MET)](https://met.readthedocs.io/en/latest/index.html)
framework, and for batch processing MET output products for rapid plotting,
forecast verification and diagnostics. These workflow tools are designed for use in the
CW3E near-real-time (NRT) system and for research purposes.  The repository is designed to run
with an embedded Cylc installation using
[Micromamba](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html#)
with an automated build procedure for the Cylc environment and its configuration for this repository.

This repository is structured as follows:
```
MET-tools/
├── cylc
├── cylc-run
├── cylc-src
│   ├── GenEnsProdMPAS
│   ├── GenEnsProdWRF
│   ├── GridStatBKG
│   ├── GridStatMPAS
│   ├── GridStatWRF
│   ├── preprocessMPAS
│   ├── preprocessWRF
│   └── vxmask
├── settings
│   ├── mask-root
│   │   ├── kml_files
│   │   ├── lat-lon
│   │   └── mask-lists
│   ├── shared
│   ├── sites
│   │   └── expanse-cwp168
│   └── template_archive
│       └── build_examples
└── src
    ├── drivers
    ├── plotting
    └── utilities
```
Currently this repository only includes workflows for producing a deterministic or ensemble-based analysis with 
the [GridStat tool](https://met.readthedocs.io/en/latest/Users_Guide/grid-stat.html) with further tool integrations
pending.

## Installing Cylc
Cylc can be run on an HPC system in a centralized or a distributed fashion.  This build procedure will
create an embedded Cylc installation with the configuration of Cylc inferred from the `config_workflow.sh`
at the root of the repository.  One should edit this file as in the following to define the local
HPC system parameters for the workflow and source this to define the Cylc environment when running the workflow.

###  Workflow configuration
In the workflow configuration one should define the full path of clone
```
export HOME="/expanse/nfs/cw3e/cwp168/MET-tools"
```
NOTE: when sourcing this configuration the Unix `${HOME}` variable will be reset in the shell
to the repository.  This is to handle Cylc's usual dependence on a `${HOME}` directory
to write out workflow logs and make them shareable in a self-contained repository / project folder
directory structure.

One should also define a site-specific configuration to source for HPC global variables
throughout the workflow and for the software environment to load for the model and DA executables.
```
export SITE="expanse-cwp168"
```
the settings for the local HPC system parameters are sourced in the `config_workflow.sh` file as
```
source ${HOME}/settings/sites/${SITE}/config.sh
```
New "sites" can be defined by creating a new directory containing a `config.sh` file
edited to set local paths / computing environment. Example configuration variables for
the workflow include:
```
export SOFT_ROOT= # Root directory for software environment singularity images
export SIM_ROOT= # Root directory of simulation IO for sourcing model outputs
export VRF_ROOT= # Root directory of simulation verification IO with MET and plotting utilities
export STC_ROOT= # Root directory for verification static data including obs and global model outputs
export MSH_ROOT= # Root directory for MPAS static files for sourcing static IO streams
```

### Building Cylc
The Cylc build script
```
${HOME}/cylc/cylc_build.sh
```
sources the `config_workflow.sh` configuration file to configure the local installation of
the Cylc executable in a self-contained Micromamba enviornment.  The Cylc installation
will be built at
```
${HOME}/cylc/Micromamba/envs/${CYLC_ENV_NAME}
```
with the Cylc software environment defined in the file
```
${HOME}/scripts/environments/${CYLC_ENV_NAME}.yml
```
sourcing a `.yml` definition file for the build.  Sourcing the `config_workflow.sh` the `${PATH}`
is set to source the cylc-wrapper script
```
${HOME}/cylc/cylc
```
configured to match the self-contained Micromamba environment.  Cylc command Bash auto-completion
is configured by default by sourcing the `config_workflow.sh` file.  Additionally the 
[cylc global configuration file](https://cylc.github.io/cylc-doc/stable/html/reference/config/global.html#global.cylc)
```
${HOME}/cylc/global.cylc
```
is configured so that workflow definitions will source the global variables
in `config_workflow.sh`, and so that task job scripts will inherit these variables as well.

### The cylc-run and log files
The Cylc workflow manager uses the [cylc-run directory](https://cylc.github.io/cylc-doc/stable/html/glossary.html#term-cylc-run-directory)
```
${HOME}/cylc-run
```
to [install workflows](https://cylc.github.io/cylc-doc/stable/html/user-guide/installing-workflows.html),
[run workflows](https://cylc.github.io/cylc-doc/latest/html/user-guide/running-workflows/index.html)
and [manage their progress](https://cylc.github.io/cylc-doc/latest/html/user-guide/interventions/index.html)
with automated logging of job status andt task execution within the associated run directories.  Job execution such as
MPAS / WRF simulation IO will not be performed in the `cylc-run` directory, as this run directory only encompasses
the execution of the workflow prior to calling the task driving script.  Task driving scripts will have
work directories nested in the directory structure at `${WORK_ROOT}` defined in the `config_workflow.sh`.

## Installing software
The installation of software dependencies outlined below can be performed 
on a shared system with the
[Apptainer](https://apptainer.org/docs/user/latest/) 
([Singularity](https://docs.sylabs.io/guides/latest/user-guide/index.html))
software container system already installed.

### Installing MET
MET can be installed as an [Apptainer](https://apptainer.org/docs/user/latest/index.html)
([Singularity](https://docs.sylabs.io/guides/latest/user-guide/index.html)) image from the
DTC's provided Dockerhub image
[without needing sudo privileges](https://apptainer.org/docs/user/latest/fakeroot.html)
on large-scale, shared computing resources.  This is performed as with the
[instructions](https://apptainer.org/docs/user/latest/build_a_container.html#downloading-an-existing-container-from-docker-hub)
for building an Apptainer / Singularity container from a DockerHub image, using a tagged image
from [MET Dockerhub](https://hub.docker.com/r/dtcenter/met). 
This workflow has been tested with MET version 11.1.1, installing the tagged version
11.1.1 from DockerHub can be performed with either Apptainer (or legacy Singularity) as
```
apptainer build met-11.1.1.sif docker://dtcenter/met:11.1.1
singularity build met-11.1.1.sif docker://dtcenter/met:11.1.1
```
where the executable singularity image is the output file `met-11.1.1.sif`.

### Installing additional libraries
Supplementary libraries for running these workflows are provided in additional containers
or can be installed indpendently.  The directory
```
${HOME}/docs
```
contains `.def` definition files for
[building](https://apptainer.org/docs/user/latest/build_a_container.html#building-containers-from-apptainer-definition-files)
the following `.sif` containers:
 * `MET-tools-py.def` is the definition for the `MET-tools-py.sif` for containerized calls of Python libraries; and
 * `convert_mpas.def` is the definition for the `convert_mpas.sif` for running the [convert_mpas](https://github.com/mgduda/convert_mpas) MPAS postprocessing utility;

to be used in this workflow.  The Python libraries can be alternatively
[constructed as a conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file)
on a local system using the `MET-tools-py.yml`.  This allows additional development of plotting and diagnostics and to add
new libraries to the MET-tools-py conda environment, where the `MET-tools-py.yml` file is to be frozen to the dependencies in the currently
supported main branch.

## Running MET-tools Cylc templates
Substeps of the workflow are templated for different use-cases illustrating analysis of WRF, MPAS and CW3E preprocessed
global model outputs.  Utilities for preprocessing WRF and MPAS for ingestion into MET are included in this
repository.  It is assumed that operational model data such as ECMWF, GFS, GEFS have already been preprocessed
as in internally standardized CW3E data products.  All workflows below are templated in the `cylc-src` directory
and are installable from there.  New workflows can be similarly constructed by defining a workflow name and configuration,
and installing and running this.

### Generating Regional Landmasks for Verification
In order to calculate relevant verification statistics, one should pre-generate
a landmask for the relevant region(s) over which forecast verification is to take place. Verification
regions are defined as a subdomain of the ground truth grid.  The following steps
illustrate the process of generating landmasks.

#### Creating User-Defined Verification Regions From Google Earth
A variety of commonly used lat-lon regions are included in the
```
${HOME}/settings/mask-root/lat-lon
```
directory in this repository, which can be used to generate the NetCDF landmasks
for the verification region. New lat-lon files can be added to this directory without
changing the behavior of existing workflow routines.

In this repository, the user also has the ability to create custom verification regions 
from KML files. One can generate their own KML file for a region through Google Earth. 
In Google Earth, the "Add path or polygon" tool can be used to click points on the map 
to draw a custom polygon for the verification region of interest. Once made, the custom 
verification region can be exported as a KML file to the system for processing. 

The naming of the KML file should be of the form
```
Mask_Name.kml
```
where `Mask_Name` is the name of the verification region. This `Mask_Name` will match 
the mask's short name in plotting routines, with any underscores 
transformed into emtpy characters when printed. Example KML files are located in the 
```
${HOME}/settings/mask-root/kml_files
```
directory.  

The KML file must be converted to a MET-compatible polygon for use in the MET-tools 
workflow. This conversion can be done through the scripts
```
${HOME}/src/utilities/config_kml.pl
${HOME}/src/utilities/kml_2_poly.pl
```
The `kml_2_poly.pl` script reads in a KML formatted file and convert its polygon geographic data to
a lat-lon text file. The arguments required to run the `kml_2_poly.pl` script are defined
in the configuration file `config_kml.pl`.

Similar to the KML file, the naming of the output lat-lon text files should be of the form
```
Mask_Name.txt
```
The formatting of the lat-lon text file should have the `Mask_Name` as the first line of
the file. Each line after the first corresponds to a latitude-longitude pair
defining the polygon region to be verified, with paired values separated by
a single blank space.

#### Computing NetCDF Landmasks From Lat-Lon Text Files
A landmask list, which is sourced by the 
```
${HOME}/src/drivers/vxmask.sh
```
defines a collection of landmasks / regions to perform verification over.
A landmask list is a text file with lines consisting of each `Mask_Name` region
over which to perform verification. Example landmask lists can be found in the
```
${HOME}/settings/mask-root/mask-lists
```
directory.

If a custom verification region is created using a KML file, running the
`kml_2_poly.pl` script will also generate a landmask list text file. This 
landmask list text file will include the `Mask_Name` of each polygon in the KML 
file that was processed by the script. 

NetCDF landmasks generated with the 
```
${HOME}/src/drivers/vxmask.sh
```
script are written out to the directory
```
${VRF_STC}/vxmask
```
with `${VRF_STC}` specified in the site configuration.
The output NetCDF masks from this script can be re-used
over valid dates that study the same verification regions and ground truth data.
The `vxmask.sh` script is called in the workflow by installing and
running the workflow
```
${HOME}/cylc-src/vxmask
```
with parameters for defining the reference grid and mask list to
process in the `flow.cylc` file therein.

### Case study / Configuration / Tool / Date Nesting
In the following steps, processing the data assumes a generic directory structure (which can be
created by linking) for the input data and creates a consistent pattern through the outputs for
internal data pipelines. It is assumed that at the `${SIM_ROOT}` defined in the site configuration paths,
simulation data is nested according to a case study / configuration directory structure.  This
matches the conventions of the
[case stud example](https://github.com/CW3E/Ensemble-DA-Cycling-Template/blob/main/README.md#case-study--configuration--sub-configuration)
for running an ensemble forecast with WRF or MPAS. For example, in the path
```
${SIM_ROOT}/valid_date_2022-12-28T00/WRF_9-3_WestCoast/2021122300/wrf_model/ens_00/
```
the `valid_date_2022-12-28T00` directory would be the `CSE_NME` variable in the templates,
at which control flows such as `WRF_9-3_WestCoast` and `WRF_9_WestCoast` would
have their simulation outputs nested.
In the example above, the forecast start date is `2021-12-23T00Z` and WRF model
outputs are nested according to ensemble index in the `wrf_model` subdirectory.

Using the case study / configuration nested convention helps to procedurally generate the paths for batch
processing multiple control flows with heterogeneous data simulataneously. For example in preprocessing WRF
data, IO is templated as
```
IN_DIR = {{environ['SIM_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/$CYC_DT/{{IN_DT_SUBDIR}}/{{ENS_PRFX}}{{idx}}
WRK_DIR = {{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/Preprocess/$CYC_DT/{{ENS_PRFX}}{{idx}}/{{grd}}
```
In the above, this is designed for Cylc to distribute tasks to batch process data over:
  * `{{ctr_flw}}` -- configuration names;
  * `$CYC_DT/{{IN_DT_SUBDIR}}` -- forecast start valid dates / simulation output subdirectories; and
  * `{{ENS_PRFX}}{{idx}}` -- ensemble member IDs.

The above template writes output data according to the nested structures
  * `{{ctr_flw}}` -- configuration names;
  * `$CYC_DT/{{IN_DT_SUBDIR}}` -- forecast start valid dates;
  * `{{ENS_PRFX}}{{idx}}` -- ensemble member IDs; and
  * `{{grd}}` subdomains.

The corresponding preprocessed WRF outputs from the templates and exmaple above would be written to the
two directories
```
${VRF_ROOT}/valid_date_2022-12-28T00/WRF_9-3_WestCoast/Preprocess/2022122300/ens_00/d01
${VRF_ROOT}/valid_date_2022-12-28T00/WRF_9-3_WestCoast/Preprocess/2022122300/ens_00/d02
```
For other models such as MPAS which do not utilize the paradigm of nested domains,
these domain subdirectories are neglected, with model specific conventions included in their
respective workflows.  The templated output paths above can be changed arbitrarily, but
note that the subsequent steps of the workflow also need to inherit IO changes.

### Preprocessing WRF outputs
WRF model outputs may not be ingestible to MET by default and preprocessing
routines are included to bring WRF outputs into a format that can be
analyzed in MET.  The script
```
${HOME}/src/drivers/preprocessWRF.sh
```
takes arguments in the workflow
```
${HOME}/cylc-src/preprocessWRF
```
to produce MET ingestible forecast files from batches of data.  This
script uses the auxiliary module / script:
```
${HOME}/src/utilites/WRF-cf.py
${HOME}/src/utilites/wrfout_to_cf.py
```
The `WRF-cf.py` module defines generic methods for ingesting raw WRF outputs in
[xarray](https://docs.xarray.dev/en/stable/index.html) to compute [CF-compliant](https://cfconventions.org/)
NetCDF files in MET readable formats.  The `wrfout_to_cf.py` is a simple wrapper that
is called in the workflow to perform computation of CF-fields and optionally regridding
WRF outputs to a generic intermediate lat-lon grid for analysis in MET.
Workflows are templated for preprocessing outputs to be written to
```
WRK_DIR = {{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/Preprocess/$CYC_DT/{{ENS_PRFX}}{{idx}}/{{grd}}
```
following the nesting conventions described above.

### Preprocessing MPAS outputs
MPAS model outputs are not ingestible to MET by default due to MET's dependence on
a lat-lon grid, and preprocessing routines are included to bring MPAS outputs into
a format that can be analyzed in MET.  The script
```
${HOME}/src/drivers/preprocessMPAS.sh
```
takes arguments in the workflow
```
${HOME}/cylc-src/preprocessMPAS
```
to produce MET ingestible forecast files from batches of data.  This
script uses the auxiliary module / scripts:
```
${HOME}/src/utilites/mpas_to_latlon.sh
${HOME}/src/utilites/MPAS-cf.py
${HOME}/src/utilites/mpas_to_cf.py
```
The `mpas_to_latlon.sh` script utilizes the [convert_mpas utility](https://github.com/mgduda/convert_mpas)
to transform the unstructured MPAS mesh to a generic lat-lon grid.  This executable has been containerized
for portability and can be built from the
[definition file](https://github.com/CW3E/MET-tools/blob/main/settings/template_archive/build_examples/convert_mpas.def)
included in the repository.  The workflow scripts call `convert_mpas` from the containerized executable
and wraps containerized commands with site-specific bindings.  Following the conventions of the latest MPAS
releases, static information can be sourced from a separate stream from the dynamic fields in MPAS outputs.
The root directory of static files `${MSH_ROOT}` can be specified in the site configuration, where it is
templated such that if
```
IN_MSH_STRM = 'TRUE'
```
then mesh static files will be sourced from configuration static files as
```
IN_MSH_DIR = {{environ['MSH_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/static
IN_MSH_F = {{msh_nme}}
```
These paths can be changed arbitrarily, and static information can be taken from MPAS outputs
alternatively if this is available. 

The `MPAS-cf.py` module defines generic methods for ingesting regridded MPAS outputs in
xarray to compute CF-compliant NetCDF files in MET readable formats.  The `mpas_to_cf.py` is a simple wrapper that
is called in the workflow to perform computation of CF-fields for analysis in MET.

### Generating Ensemble Products from WRF and MPAS
Once WRF / MPAS model outputs have been preprocessed with the workflows above, these preprocessed files can be ingested into
GridStat directly following the instructions below, or these can be combined with the GenEnsProd tool in MET to generate
ensemble forecast statistics files including mean and spread products.  The script
```
${HOME}/src/drivers/GenEnsProd.sh
```
takes arguments in the workflows
```
${HOME}/cylc-src/GenEnsProdWRF
${HOME}/cylc-src/GenEnsProdMPAS
```
to produce ensemble products as above. Inputs for GenEnsProd are determined by the minimum and maximum
ensemble index, their padding and their prefix, e.g.
```
ENS_PRFX = 'ens_'
ENS_PAD = 2
ENS_MIN = 0
ENS_MAX = 2
```
will search for preprocessed outputs in subdirectories
```
{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/Preprocess/$CYC_DT/ens_00
{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/Preprocess/$CYC_DT/ens_01
{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/Preprocess/$CYC_DT/ens_02
```
and these naming conventions carry over to the outputs of GenEnsProd.

Outputs from GenEnsProd are handled specially by GridStat with switches
included in these workflows for processing ensemble products and individual members respectively.
Outputs of GenEnsProd are templated to be written following the directory structure
```
{{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/GenEnsProd/$CYC_DT
```
with additional subdirectories for subdomains therein.

### Generating GridStat Analyses for WRF, MPAS and Background Operational Models
Workflows are provided for running GridStat on:
  * WRF ensemble member and ensemble mean outputs
    ```
    ${HOME}/cylc-src/GridStatWRF
    ```
  * MPAS ensemble member and ensemble mean outputs
    ```
    ${HOME}/cylc-src/GridStatMPAS
    ```
  * Background operational global model products
    ```
    ${HOME}/cylc-src/GridStatBKG
    ```

Arguments from these files are propagated to the driving script
```
${HOME}/src/drivers/GridStat.sh
```
which utilizes the auxilliary module / script
```
${HOME}/src/utilities/DataFrames.py
${HOME}/src/utilities/ASCII_to_DataFrames.py
```
to produce additional postprocessing of GridStat outputs.

To run GridStat, one must have appropriate gridded ground truth at the corresponding valid times
and land masks precomputed for that grid.  Gridded ground truth data is sourced in the workflows from the
`${STC_ROOT}` directory dfined in the site configuration.  Currently only CW3E preprocessed
StageIV products are supported with further ground truth data sets pending integration.  Global
model data is also templated to be sourced from the `${STC_ROOT}` directory as
```
IN_DIR = {{environ['STC_ROOT']}}/{{ctr_flw}}/{{IN_STC_SUBDIR}}/$CYC_DT/{{IN_DT_SUBDIR}}
```
where for example ECMWF precip data with a forecast start on 2022-12-23T00Z
```
${STC_ROOT}/ECMWF/Precip/2022122300
```
can be sourced by including ECMWF in the control flow list and setting
```
IN_STC_SUBDIR = 'Precip'
IN_DT_SUBDIR = ''
```
in the workflow template.

For WRF and MPAS, workflow switches are included to source data from ensemble members or from ensemble
mean products as
```
IF_ENS_MEAN = 'TRUE'
IF_ENS_MEMS = 'TRUE'
```
Setting values to `TRUE` directs the Cylc template to create tasks for running GridStat on
  * the ensemble mean product generated over the indices specified, e.g., with IO as
    ```
    IN_DIR = {{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/GenEnsProd/$CYC_DT/{{grd}}
    WRK_DIR = {{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/GridStat/{{VRF_REF}}/$CYC_DT/mean/{{grd}}
    ```
  * or the ensemble members over the indices specified, e.g., with IO as
    ```
    IN_DIR = {{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/Preprocess/$CYC_DT/{{ENS_PRFX}}{{idx}}/{{grd}}
    WRK_DIR = {{environ['VRF_ROOT']}}/{{CSE_NME}}/{{ctr_flw}}/GridStat/{{VRF_REF}}/$CYC_DT/{{ENS_PRFX}}{{idx}}/{{grd}}
    ```

respectively, where `{{VRF_REF}}` is the specified ground truth.  For example, an output path produced by the templates
for a WRF mean product on domain `d01` verified versus StageIV is
```
${VRF_ROOT}/valid_date_2022-12-28T00/WRF_9-3_WestCoast/GridStat/StageIV/2022122300/mean/d01
```
Raw outputs of GridStat are ASCII tables written to the work directories above, with naming conventions including
the analyzed field, the lead and the valid time, e.g.,
```
grid_stat_QPF_24hr_1200000L_20221228_000000V_nbrcnt.txt
```
The types of ASCII tables output are described in the 
[GridStat documentation](https://met.readthedocs.io/en/latest/Users_Guide/grid-stat.html#grid-stat-output).  For

### Plotting
