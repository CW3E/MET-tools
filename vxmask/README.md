# Generating Regional Landmasks for Verification
In order to calculate relevant verification statistics, one should pre-generate
a landmask for the region over which the verification is to take place. This
region will be defined as a sub-domain of the StageIV grid, which can be generated
in the following steps.


## Creating User-Defined Verification Regions From Google Earth

A variety of commonly used lat-lon regions are included in the
```
MET-tools/vxmask/lat-lon
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
MET-tools/vxmask/kml_files
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


## Computing NetCDF Landmasks From Lat-Lon Text Files

In order to define a collection of landmasks to perform verification over,
one will define a landmask list, which will be sourced by the `run_vxmask.sh`
and `run_GridStat.sh` scripts in the following. A landmask list is a text file
with lines consisting of each `Mask_Name` region over which to perform
verification. Example landmask lists can be found in the
```
MET-tools/vxmask/mask-lists
```
directory.

If a custom verification region is created using a KML file, running the
`kml_2_poly.pl` script will also generate a landmask list text file. This 
landmask list text file will include the `Mask_Name` of each polygon in the KML 
file that was processed by the script. 

The NetCDF landmasks that will be ingested by GridStat are generated
with the `run_vxmask.sh` script. The output NetCDF masks from this script can be re-used
over multiple analyses that study the same verification regions. The required arguments of 
the `run_vxmask.sh` script are defined in the configuration file `config_vxmask.sh` and are as follows:

 * `${USR_HOME}`    - the directory path for the MET-tools clone (sourced by `../config_MET-tools.sh`).
 * `${MSK_ROOT}`    - the root directory path for the landmasks, lat-lon files, KML files, and reference grids (sourced by `../config_MET-tools.sh`).
 * `${MET}`         - the MET singularity image path (sourced by `../config_MET-tools.sh`).
 * `${VRF_RGN}`     - the verification region group name.
 * `${MSK_LTLN}`    - the directory path to lat-lon text files for mask generation.
 * `${MSK_LST}`     - the directory path to the file with a list of landmasks for verification regions.
 * `${MSK_GRDS}`    - the root directory of regridded .nc landmasks on StageIV domain for verification.
 * `${OBS_F_IN}`    - the generic StageIV data product for reference verification grid in `${MSK_ROOT}`.
 
Currently, the StageIV 4km precipitation grid is supported, and integration of the PRISM 
precipitation grid in the workflow is pending. In this repository, a generic StageIV 
product is included in the following path:
```
MET-tools/vxmask/StageIV_QPE_2019021500.nc
```
which can be used for the `${OBS_F_IN}` above as the reference grid for
generating landmasks.


