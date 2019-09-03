#!/bin/bash

cd $PBS_O_WORKDIR
source env.sh
echo -n "starting WEST client process on "; hostname
echo "current directory is $PWD"
/oasis/scratch/alisingl/temp_project/nacl_we/apps/epd/bin/python /oasis/scratch/alisingl/temp_project/bb_we_eq/build_state_dist_bb.py "$@" &> west-$PBS_JOBID-$PBS_NODENUM-$PBS_VNODENUM.log
