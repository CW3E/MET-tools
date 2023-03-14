# MET-tools

## Getting started

## Installing software

### Installing MET
MET can be installed as a singularity container from the Dockerhub image
[without needing sudo privileges](https://docs.sylabs.io/guides/2.6/user-guide/introduction.html#security-and-privilege-escalation)
on large-scale, shared computing resources.  This is performed as with the
[instructions](https://docs.sylabs.io/guides/2.6/user-guide/build_a_container.html#downloading-a-existing-container-from-docker-hub)
for building a singularity container from a Dockherub image, using a tagged image
from [MET Dockerhub](https://hub.docker.com/r/dtcenter/met). 
This workflow has been tested with MET version 10.0.1, installing the tagged version
10.0.1 from DockerHub can be performed as
```
singularity build met-10.0.1.simg docker://dtcenter/met:10.0.1
```
where the executable singularity image is the output file `met-10.0.1.simg`.

### Conda Environments
To get started with this repository you will need to use conda to install 
software dependencies. Bash scripts use the Conda environment `netcdf` to process
NetCDF files. This environment can be created as follows:
```
conda create --name netcdf
conda activate netcdf
conda install -c conda-forge ncl
conda install -c conda-forge cdo
conda install -c conda-forge nco
```

Dataframes for MET outputs and plotting routines based on these dataframes
are implemented with the Conda environment `ipython`.  This environment can
be created as follows:
```
conda create --name ipython
conda activate ipython
conda install ipython
conda install matplotlib
conda install seaborn
```

## Workflow for generating precipitation diagnostics

### Converting wrfout to cf-compliant files

wrfout_to_cf.ncl is a modified version of the original wrfout_to_cf specifically for west-wrf output
that includes added variables of ivt and precipitation. 

You will set output variables to TRUE within this code to convert them into cf-compliant netcdf
files.  The cf-compliant files are neccessary (at this time) to import into MET, but will become
obsolete in future iterations.

It is best to create a driver to loop through the experiment files that you would like to verify.
Below is an example of the commands used to run the ncl file from a shell script:                 

    statement="ncl 'file_in=\"${input_path}${input_file}\"' 'file_prev=\"${file_prev}\"
    ' 'file_out=\"${output_path}${output_file}\"' wrfout_to_cf.ncl "
    eval $statement

* Note, two files are needed because the 24-hr accumulation of precipitation is calculated by
subtracting the simulation accumulation variables for rain at t=valid time and t=valid_time-1

### Running gridstat on cf-compliant wrfout

### Running gridstat on pre-processed background data (GFS / ECMWF)

### Processing gridstat outputs

### Plotting from pickled data frames
