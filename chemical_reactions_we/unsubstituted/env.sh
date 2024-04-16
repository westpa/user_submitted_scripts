# This file defines where WEST and NAMD can be found
# Modify to taste
#module load anaconda

module purge
module load intel/2017.3.196 amber/18
module unload python
source ~/.bashrc
conda activate westpa2-qmmm

# This is our local scratch, where we'll store files during the dynamics.
export NODELOC=$LOCAL
export USE_LOCAL_SCRATCH=1

# Explicitly name our simulation root directory
export WEST_SIM_ROOT="$PWD"

# Set simulation name
export SIM_NAME=$(basename $WEST_SIM_ROOT)
echo "simulation $SIM_NAME root is $WEST_SIM_ROOT"

# Export environment variables for the ZMQ work manager.
export WM_ZMQ_MASTER_HEARTBEAT=100
export WM_ZMQ_WORKER_HEARTBEAT=100
export WM_ZMQ_TIMEOUT_FACTOR=300
export BASH=$SWROOT/bin/bash
export PERL=$SWROOT/usr/bin/perl
export ZSH=$SWROOT/bin/zsh
export IFCONFIG=$SWROOT/bin/ifconfig
export CUT=$SWROOT/usr/bin/cut
export TR=$SWROOT/usr/bin/tr
export LN=$SWROOT/bin/ln
export CP=$SWROOT/bin/cp
export RM=$SWROOT/bin/rm
export SED=$SWROOT/bin/sed
export CAT=$SWROOT/bin/cat
export HEAD=$SWROOT/bin/head
export TAR=$SWROOT/bin/tar
export AWK=$SWROOT/usr/bin/awk
export PASTE=$SWROOT/usr/bin/paste
export GREP=$SWROOT/bin/grep
export SORT=$SWROOT/usr/bin/sort
export UNIQ=$SWROOT/usr/bin/uniq
export HEAD=$SWROOT/usr/bin/head
export MKDIR=$SWROOT/bin/mkdir
export ECHO=$SWROOT/bin/echo
export DATE=$SWROOT/bin/date
#export SANDER=/ihome/crc/build/amber/amber18/bin/pmemd
#export CPPTRAJ=/ihome/crc/build/amber/amber18/bin/cpptraj
