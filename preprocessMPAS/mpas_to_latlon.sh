#!/bin/bash
#SBATCH --account=cwp157
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=16
#SBATCH --mem=249208M
#SBATCH -p cw3e-compute
#SBATCH -t 01:00:00
#SBATCH -J convert_mpas

# take the input file from script argument
F_IN=$1

# clean up old link of executable and relink
rm -f ./convert_mpas
ln -sf ${SOFT_ROOT}/convert_mpas/convert_mpas ./

# clean up old configuration files
rm -f ./target_domain
rm -f ./include_fields

# clean up old lalon files
rm -f latlon.nc

# Regrid to generic lat-lon grid for MET, passed to convert_mpas tool
NLAT=750
NLON=1375
LAT1=5.
LAT2=65.
LON1=162.
LON2=272.

# set domain parameters from configuration file
printf "nlat = ${NLAT}\n" >> ./target_domain
printf "nlon = ${NLON}\n" >> ./target_domain
printf "startlat = ${LAT1}\n" >> ./target_domain
printf "startlon = ${LON1}\n" >> ./target_domain
printf "endlat = ${LAT2}\n" >> ./target_domain
printf "endlon = ${LON2}\n" >> ./target_domain

# set fields to be regridded
printf "rainc\n" >> ./include_fields
printf "rainnc\n" >> ./include_fields

# run convert mpas
./convert_mpas ${F_IN}

# remove link / configuration files
rm -f ./convert_mpas
rm -f ./target_domain
rm -f ./include_fields

# rename output to something non-generic
IFS="." read -ra tmp_array <<< "$F_IN"
str_len=${#tmp_array[@]}
rename=""
for (( i = 0 ; i < ${str_len} ; i ++ )); do
  tmp_str=${tmp_array[i]}
  if [[ ${tmp_str} = "history" && ${tmp_str} = "diag" ]]; then
    rename="${rename}latlon."
  else
    rename="${rename}${tmp_array[i]}."
  fi
done

rename="${rename}latlon.${tmp_array[$str_len]}"
mv latlon.nc ${rename}

exit 0
