# GridStat Tools

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
