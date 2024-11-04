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

## Installing Cylc
Cylc can be run on an HPC system in a centralized or a distributed fashion.  This build procedure will
create an embedded Cylc installation with the configuration of Cylc inferred from the `config_workflow.sh`
at the root of the repository.  One should edit this file as in the following to define the local
HPC system paramters for the workflow.

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
or can be installed indpendently.  In the 
```
MET-tools/docs
```
directory, you can find `.def` definition files for
[building](https://apptainer.org/docs/user/latest/build_a_container.html#building-containers-from-apptainer-definition-files)
the following `.sif` containers:
 * `MET-tools-py.def` is the definition for the `MET-tools-py.sif` for containerized calls of Python libraries; and
 * `convert_mpas.def` is the definition for the `convert_mpas.sif` for running the [convert_mpas](https://github.com/mgduda/convert_mpas) MPAS postprocessing utility;

to be used in this workflow.  The Python libraries can be alternatively
[constructed as a conda environment](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file)
on a local system using the `MET-tools-py.yml`.  The convert_mpas tool can also be compiled directly on a host system according to its instructions.

## Running MET-tools Cylc templates
Substeps of the workflow are templated for different use-cases illustrating analysis of WRF, MPAS and CW3E preprocessed
global model outputs.  Utilities for preprocessing for WRF and MPAS for ingestion into MET are included in this
repository.  It is assumed that operational model data such as ECMWF, GFS, GEFS have already been preprocessed
as in standardized CW3E data products.

### Generating Regional Landmasks for Verification
In order to calculate relevant verification statistics, one should pre-generate
a landmask for the region over which the verification is to take place. This
region will be defined as a sub-domain of the StageIV grid, which can be generated
in the following steps.


#### Creating User-Defined Verification Regions From Google Earth

A variety of commonly used lat-lon regions are included in the
```
MET-tools/settings/mask-root/lat-lon
```
directory in this repository, which can be used to generate the NetCDF landmasks
for the verification region in the StageIV grid. New lat-lon files can be added
to this directory without changing the behavior of existing workflow routines.

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
the mask's printed name in plotting routines, with any underscores corresponding to 
blank spaces - these underscores are parsed in the plotting scripts when defining 
the printed name with spaces. Example KML files are located in the 
```
MET-tools/settings/mask-root/kml_files
```
directory.  

The KML file must be converted to a MET software-compatible polygon for use in the MET-tools 
workflow. This conversion can be done through the script `kml_2_poly.pl`. The purpose of 
this script is to read in a KML formatted file and convert its polygon geographic data to
a lat-lon text file. The arguments required to run the `kml_2_poly.pl` script are defined
in the configuration file `config_kml.pl`. The required arguments are as follows:

 * `${USR_HOME}`   - the directory path for the MET-tools clone. 
 * `${MSK_ROOT}`   - the root directory path for the landmasks, lat-lon files, KML files, and reference grids.
 * `${MSK_LTLN}`   - the directory path for the lat-lon files for mask generation. 
 * `${VRF_RGN}`    - the name of the verification region (i.e., the `Mask_Name`). 
 * `${KML_IN}`     - the directory path for the input KML file.
 * `${MSK_LST}`    - the directory path for the text file with a list of landmasks for the verification region. 

Similar to the KML file, the naming of the output lat-lon text files should be of the form
```
Mask_Name.txt
```
The formatting of the lat-lon text file should have the `Mask_Name` as the first line of
the file. Each line after the first corresponds to a latitude-longitude pair
defining the polygon region to be verified, with paired values separated by
a single blank space.


#### Computing NetCDF Landmasks From Lat-Lon Text Files

In order to define a collection of landmasks to perform verification over,
one will define a landmask list, which will be sourced by the `run_vxmask.sh`
and `run_GridStat.sh` scripts in the following. A landmask list is a text file
with lines consisting of each `Mask_Name` region over which to perform
verification. Example landmask lists can be found in the
```
MET-tools/settings/mask-root/mask-lists
```
directory.

If a custom verification region is created using a KML file, running the
`kml_2_poly.pl` script will also generate a landmask list text file. This 
landmask list text file will include the `Mask_Name` of each polygon in the KML 
file that was processed by the script. 

The NetCDF landmasks that will be ingested by GridStat are generated
with the `run_vxmask.sh` script. The output NetCDF masks from this script can be re-used
over multiple analyses that study the same verification regions.

### Preprocessing WRF outputs

### Preprocessing MPAS outputs

### Generating Ensemble Products from WRF and MPAS

### Generating GridStat Analyses for WRF, MPAS and Background Operational Models

### Plotting
