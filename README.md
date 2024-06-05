# MET-tools

## Description
This is a workflow template for batch processing numerical weather prediction (NWP) data with the 
[Model Evaluation Tools (MET)](https://met.readthedocs.io/en/latest/index.html)
framework, and for batch processing MET output products for rapid plotting,
forecast verification and diagnostics. These workflow tools are designed for use in the
CW3E near-real-time (NRT) system and for research purposes. Workflow tools are in
continuous development with direct and indirect contributions from multiple
authors. This repository has benefitted from source code and other
contributions by Colin Grudzien, Rachel Weihs, Corrine DeCiampa,
Jozette Conti, Evan Sawyer, Caroline Papadopoulos, Dan Stienhoff,
Laurel Dehaan, Matthew Simpson, Brian Kawzenuck, Nora Mascioli,
Patrick Mulrooney, Minghua Zheng, Ivette Hernandez Ba&ntilde;os, and others.

## Installing software
The tools for batch processing NWP data and MET outputs are designed to be
largely system agnostic, though examples will utilize SLURM scheduling commands
which can be modified to other environments. Currently this workflow is SLURM
job array driven for naive parallism using shared resources to distribute tasks.
This workflow is pending a re-write to be 
[Cylc](https://cylc.github.io/) driven to automate the sequence
of tasks and to simplify the configuration / job array creation and submission.
This work is also pending adoption of more conventions from METplus wrappers
to utilize the functionality from the parallel developments.  Documentation will
be updated when major re-writes are completed for Cylc and METplus integration.

The installation of software dependencies outlined below can be performed 
on a shared system with the
[Apptainer](https://apptainer.org/docs/user/latest/) software container
system already installed.

### Installing MET
MET can be installed as an [Apptainer](https://apptainer.org/docs/user/latest/index.html)
([Singularity](https://docs.sylabs.io/guides/latest/user-guide/index.html)) image from the
DTC's provided Dockerhub image
[without needing sudo privileges](https://apptainer.org/docs/user/latest/fakeroot.html)
on large-scale, shared computing resources.  This is performed as with the
[instructions](https://apptainer.org/docs/user/latest/build_a_container.html#downloading-an-existing-container-from-docker-hub)
for building an Apptainer / Singularity container from a DockerHub image, using a tagged image
from [MET Dockerhub](https://hub.docker.com/r/dtcenter/met). 
This workflow has been tested with MET version 11.0.1, installing the tagged version
11.0.1 from DockerHub can be performed with either Apptainer (or legacy Singularity) as
```
apptainer build met-11.0.1.sif docker://dtcenter/met:11.0.1
singularity build met-11.0.1.sif docker://dtcenter/met:11.0.1
```
where the executable singularity image is the output file `met-11.0.1.sif`.

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
on a local system using the `MET-tools-py.yml`.
