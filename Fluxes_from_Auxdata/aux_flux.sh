#!/bin/bash

SCHEME="TEST"

mkdir -p direct_files
w_assign -W west.h5 --config-from-file --scheme ${SCHEME} --construct-dataset module.load_auxdata --serial
w_direct all -a ./ANALYSIS/${SCHEME}/assign.h5
mv ./ANALYSIS/${SCHEME}/assign.h5 ./direct_files/assign_${SCHEME}.h5
mv direct.h5 ./direct_files/direct_${SCHEME}.h5
rm -r ./ANALYSIS
