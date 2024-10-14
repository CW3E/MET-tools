# MET-tools Plotting
The MET-Tools workflow includes various plotting options to visualize 
forecast statistics. These options include various heat plots and line 
plots. These plotting scripts (and the changes made to them) will be 
briefly described below. 

The user must be on an interactive (`salloc`) node to run these plotting 
scripts. Once on the `salloc` node, the user must run the following line of code:

```
source config_plotDataFrames.sh 
```

The `config_plotDataFrames.sh` script defines a wrapper function 
(`mtpython()`) used for interactive shell Python-like calls of scripts. 
This wrapper function is defined with respect to the singularity container 
directory binds. Once sourced, the user will be able to interactively call 
and run the plotting scripts using the following syntax:

```
mtpython <<plot_script>> <<plot_config_file>>
```

Where `<<plot_script>>` is the filename of a plotting script and 
`plot_config_file` is the plotting script's respective configuration file. 
Each available plotting script and its respective configuration files are described below.  

### General Adjustments Made to All Plots
Adjustments were made to each plot to have more descriptive titles/subtitles. 
Across all plots, the following changes were made.

* New variables were added to the configuration file so the user could specify important information.
	* `QPE_SOURCE` - a user-defined value for the source of the QPE data (i.e., Stage-IV). Used for a plot subtitle.
	* `DMN_TITLE` - a user-defined value for the full name of the verification region. Used for a plot subtitle.

* The plot title is now defined (using if-elif-else loops) to expand the statistic name and grid.
	* For example, "RMSE" now is expanded to be "Root-Mean-Squared Error"
	* Instead of the grid being "d02", it is expanded to be "3km"

**The changes above in the configuration may have altered the plot's filename. This may need to be adjusted.**

## Line Plots
Two different line plot scripts are available in the MET-Tools workflow: 
one for grid point-based metrics (e.g., RMSE and PR_CORR) and one for
spatial-based metrics (e.g., FSS and AFSS). 

`plt_gridstat_multilead_lineplot.py`:
* This script plots the RMSE and PR_CORR for 24hr accumulated precipitation on a valid forecast datetime.
* `config_lineplotEnsVersBKG.py` is the respective configuration file.

`plt_gridstat_multilead_lineplot_level.py`:
* This script plots the FSS and AFSS for 24hr accumulated precipitation on a valid forecast datetime.
* `config_lineplotlevelEnsVersBKG.py` is the respective configuration file.

### Adjustments to Line Plots
For values on a fixed domain (i.e., FSS, AFSS, and PR_CORR), the plot y-axis only includes 6 ticks from 0.5 to 1.
For padding, the plots for these metrics have a y-axis limit of [0.45, 1.05]. The RMSE plot, however, is not on a
set domain. But, for the gridlines to have the same spacing as the PR_CORR plot, the RMSE plot was coded to
have a y-axis limit of +/- half the distance between successive ticks. 

**This may need to be adjusted if the fixed domains are changed**

## Heat Plots
Seven different heat plots are available in the MET-Tools workflow. Four of
which are for the relative difference between two models.

`plt_gridstat_multidate_heatplot.py`:
* This script is used for the RMSE or PR_CORR metrics with respect to the forecast lead time and verification valid date.
* `config_heatplotmultidateEns.py` is the respective configuration file.

`plt_gridstat_multidate_heatplot_level.py`:
* This script is used for the FSS or AFSS metrics with respect to the forecast lead time and verification valid date.
* `config_heatplotmultidatelevelEns.py` is the respective configuration file.

`plt_gridstat_multilevel_heatplot.py`:
* This script is used for the FSS or AFSS metrics with respect to the accumulation threshold and forecast lead time at a set valid time.
* `config_heatplotmultilevelEns.py` is the respective configuration file.

The next four are the relative difference heatplots. These plots show the skill gain/loss in the analysis model
compared to a reference model (e.g., the NRT_ECMWF relative difference from the ECMWF). Furthermore, these 
heat plots show the reference scores within the cells to help put into perspective the skill gain/loss.

`plt_gridstat_multidate_heatplot_relative_difference.py`:
* This script is used for the relative difference between two models for the the RMSE or PR_CORR metrics with respect to the forecast lead time and verification valid date.
* `config_heatplotmultidateEnsVersBKG.py` is the respective configuration file.

`plt_gridstat_multidate_heatplot_level_relative_difference.py`:
* This script is used for the relative difference between two models for the the FSS or AFSS metrics with respect to the forecast lead time and verification valid date.
* `config_heatplotmultidatelevelEnsVersBKG.py` is the respective configuration file.

`plt_gridstat_multidate_heatplot_level_fixedlead_relative_difference.py`:
* This script is used for the relative difference between two models for the the FSS or AFSS metrics with respect to the accumulation threshold and verification valid date at a set forecast lead time.
* `config_heatplotmultidatelevelfixedleadEnsVersBKG.py` is the respective configuration file.

`plt_gridstat_multilevel_heatplot_relative_difference.py`:
* This script is used for the relative difference between two models for the the FSS or AFSS metrics with respect to the accumulation threshold and forecast lead time at a set valid time.
* `config_heatplotmultilevelEnsVersBKG.py` is the respective configuration file.

### Adjustments to Heat Plots
The main changes are for the relative difference heat plots. A discrete custom color bar was made to visualize the skill gain/loss 
better. These colorbars are directly defined in the plotting scripts (no longer in the config files).
This is due to the the dependency on the values of `min_scale` and `max_scale`. If `max_scale` < 100 and `min_scale` > -100,
then the colorbar's endpoints are +/- 100%. If the absolute values of `min_scale` and `max_scale` are greater than 100, then 
the values of `min_scale` and `max_scale` are the colorbar's endpoints. 

The thresholds of the colorbar's data classes can be manually adjusted within the plotting script as well (ensure to change the label strings
as well).   

