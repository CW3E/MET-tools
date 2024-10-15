# Processing NRT Data Using MET
For the processing of NRT data, some adjustments were made to the MET-tools workflow.
This README is a temporary file to act as a guide to some of the changes made for 
the NRT data processing. 

## preprocessNRT
The first change involves the preprocessing of the NRT data. This section of the MET-tools 
workflow has had the most changes. A new directory, `MET-tools/preprocessNRT`, was created 
to host these changes. The main changes that were made are detailed below.

`batch_preprocessNRT.sh`:
* SBATCH job array - The job array is a product of # of `CTR_FLWS`, # of `MEMS`, # of `GRDS`, and # of `NRT_NAMES` (new array, see below).

`config_preprocessNRT.sh`:
* Added new array variable `NRT_NAME` - necessary for file handling between the two NRT models (ECMWF and GFS).

`run_preprocessNRT.sh`:
*  Changed `f_in` and `f_out` to match NRT cf data.
	* `f_in="wrfcf_${NRT_NAME}_${GRD}_${anl_dt}.nc"`
	* `f_out="wrfcf_${NRT_NAME}_${GRD}_${anl_dt}.nc"`
> NOTE: As the cf NRT data needs to be regridded, I have made `f_in` and `f_out` the same filename (directory locations differ). 
* Changed the filename pattern for the combining of precip in the accumulation period.
	* `pcp_combine -subtract /wrk_dir/wrfcf_${NRT_NAME}_${GRD}_${anl_stop}.nc /wrk_dir/wrfcf_${NRT_NAME}_${GRD}_${anl_strt}.nc\`

`wrfout_to_cf.py`:
* To combine the precip for the accumulation period, the wrfcf NRT data has to be regridded. 
* The precip data, however, does not need to be loaded into xarray and extracted. Thus, these steps have been removed from the script.  


## Other Workflow Changes
Along with the major changes done within the `preprocessNRT` directory, small adjustments
were made throughout the MET-tools workflow. These changes mainly include the addition of
NRT-specific scripts for GridStat and GenEnsProd. The new scripts are:

* `batch_GridStatNRT.sh`
* `config_GridStatNRT.sh`
* `batch_GenEnsProdNRT.sh`
* `config_GenEnsProdNRT.sh`

These scripts are similar to their WRF and BKG counterparts but are adjusted for processing 
of the `NRT_ECMWF` and `NRT_GFS` data.
 
