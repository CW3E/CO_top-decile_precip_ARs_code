#!/bin/bash

start_yr=2012
end_yr=2019

for year in $(seq $start_yr $end_yr)
do
    mkdir ${year}
    touch ${year}/test.txt
done