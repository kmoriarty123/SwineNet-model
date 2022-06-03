#!/bin/bash

prj_dir=/storage/homefs/km21a901/NetworkMaterial/SwineNet-model
date=2019_7_1
output_dir=$prj_dir/output/$date

echo "Concat files..."

for level1 in $output_dir/*
do
  for level2 in $level1/*
  do
    cd $level2
    cat results_by_contact_grp_*.csv > results_by_contact_grp_all.txt
    cat results_by_compart_*.csv > results_by_compart_all.txt
    cat results_inspected_farms_*.csv > results_inspected_farms_all.txt
  done
done

cd $output_dir

echo "Create tar gzip..."

# Create the tar gzip
file_prefix=`date '+%Y_%m_%d'`
tar -cvzf ${file_prefix}_all_txt.tar.gz `find ./ | grep '.txt'`
