# MET-tools

## Description
This is a working template repository for tools for batch processing numerical
weather prediction (NWP) data with the [Model Evaluation Tools (MET)](https://met.readthedocs.io/en/latest/index.html)
framework, and for batch processing MET output products for rapid plotting,
forecast verification and diagnostics. These tools are designed for use in the
CW3E near-real-time (NRT) system and for research purposes. Tools are in
continuous development with direct and indirect contributions from multiple
authors. This repository has benefitted from source code and other
contributions by Colin Grudzien, Rachel Weihs, Caroline Papadopoulos,
Dan Stienhoff, Laurel Dehaan, Matthew Simpson, Brian Kawzenuck, Nora Mascioli,
Minghua Zheng, Ivette Hernandez Ba&ntilde;os, Patrick Mulrooney, Jozette Conti, and others.

## Installing software
The tools for batch processing NWP data and MET outputs are designed to be
largely system agnostic, though examples will utilize SLURM scheduling commands
which can be modified to other environments. The installtion of software
dependencies outlined below can be performed on a shared system with the
[Singularity](https://docs.sylabs.io/guides/latest/user-guide/) software container
system already installed.

### Installing MET
MET can be installed as a singularity container from the Dockerhub image
[without needing sudo privileges](https://docs.sylabs.io/guides/latest/user-guide/introduction.html#security-and-privilege-escalation)
on large-scale, shared computing resources.  This is performed as with the
[instructions](https://docs.sylabs.io/guides/latest/user-guide/build_a_container.html#downloading-a-existing-container-from-docker-hub)
for building a singularity container from a DockerHub image, using a tagged image
from [MET Dockerhub](https://hub.docker.com/r/dtcenter/met). 
This workflow has been tested with MET version 11.0.1, installing the tagged version
11.0.1 from DockerHub can be performed as
```
singularity build met-11.0.1.sif docker://dtcenter/met:11.0.1
```
where the executable singularity image is the output file `met-11.0.1.sif`.

### Singularity Containers
To get started with this repository, the required Singularity containers need to be downloaded.
These Singularity containers replace the need for the user to initialize the 
conda environment manually, making the workflow more portable and user-friendly. Two Singularity 
containers are provided, one for the NetCDF pre-processing environment and one for the 
iPython post-processing environment. These containers can be obtained by running the following lines of code.

Bash scripts use the Conda environment `netcdf` to process
NetCDF files. This Singularity container can be obtained by running the following:

```
singularity pull https://g-811a55.0f1d28.a567.data.globus.org/MET_tools/MET_tools_conda_netcdf.sif
```

Dataframes for MET outputs and plotting routines based on these dataframes
are implemented with the Conda environment `ipython`. This Singularity container 
can be obtained by running the following:
```
singularity pull https://g-811a55.0f1d28.a567.data.globus.org/MET_tools/MET_tools_conda_ipython.sif
```

For reference on the package dependencies in which these containers were built from, 
this repository includes the respective requirements.txt files. Two files were made 
and used, one for the NetCDF environment, `netcdf_requirements.txt`, and one for the 
iPython environment, `ipython_requirements.txt`.  

For more information on how these containers were built and implemented into the scripts, 
refer to the [Research Code Portability Tutorial repository](https://github.com/CW3E/Research-Code-Portability-Tutorial).

## Repository Organization
Currently this repository has focused on developing batch processing routines for
the [Grid-Stat](https://met.readthedocs.io/en/latest/Users_Guide/grid-stat.html)
module from the MET framework. Related scripts are included in the `Grid-Stat`
subdirectory. Instructions on how to use these batch processing scripts
are included in the README therein. New batch processing tools will be
organized similarly for other MET modules as they are developed.

## Known Issues
With the current workflow having contained environments, there is an 
ongoing issue involving the live plotting ability of the Python scripts. 
With the Singularity containers, generated plots can be viewed through 
the GUI desktop option on Comet. Live plotting is available, however, for 
the previous uncontained environments. If this is preferred, the 
environment can be established by the commands provided in the following section.

### Conda Environments
While the containerized conda environments needed for this workflow are provided, users 
can establish the environments manually if preferred. Sofware environments that are not 
containerized are managed by creating appropriate [Conda environments](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
The NetCDF environment can be created as follows:
```
conda create --name netcdf
conda activate netcdf
conda install -c conda-forge ncl
conda install -c conda-forge cdo
conda install -c conda-forge nco
```

The iPython environment can be created as follows:
```
conda create --name ipython
conda activate ipython
conda install ipython
conda install matplotlib
conda install seaborn
```
