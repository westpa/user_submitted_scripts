#!/bin/bash

# Set up simulation environment
source env.sh

# Clean up from previous/ failed runs
rm -rf traj_segs seg_logs istates west.h5 *.log *.json
mkdir   seg_logs traj_segs istates

# Set pointer to bstate and tstate
BSTATE_ARGS="--bstate-file $WEST_SIM_ROOT/bstates/bstate.file"
TSTATE_ARGS="--tstate-file $WEST_SIM_ROOT/tstate.file"

# Run w_init
w_init \
  $BSTATE_ARGS \
  $TSTATE_ARGS \
  --segs-per-state 1 \
  --work-manager=threads "$@"
