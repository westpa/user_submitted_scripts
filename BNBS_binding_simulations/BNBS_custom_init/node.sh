#!/bin/bash

cd $WEST_SIM_ROOT
source env.sh
echo -n "starting WEST client process on "; hostname
echo "current directory is $PWD"

set -x
python build_state_dist_bb.py "$@" &> west-node.log
