#!/bin/bash

set -x 

WEST_JOBID=$1; shift

cd $(dirname $0)
export WEST_SIM_ROOT=/scratch/02031/alisingl/new_BNBS
(source env.sh
echo -n "starting WEST client process on "; hostname
echo "current directory is $PWD"
echo "environment is:"
env | sort
$WEST_ROOT/bin/w_run "$@" ) &> west-$WEST_JOBID-$(hostname -s).log
