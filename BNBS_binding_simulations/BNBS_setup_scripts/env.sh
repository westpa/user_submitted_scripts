# This file defines where WEST and GROMACS can be found
# Modify to taste

# Inform WEST where to find Python and our other scripts where to find WEST
export WEST_PYTHON=/home1/02031/alisingl/apps/anaconda/bin/python
export WEST_ROOT=/home1/02031/alisingl/apps/westpa/
export GRO_BIN=/work/02031/alisingl/apps/gmx-4.6.5-mpi-sse4.1/bin/

export WEST_SIM_ROOT=/scratch/02031/alisingl/new_BNBS
export SIM_NAME=$(basename $WEST_SIM_ROOT)
echo "simulation $SIM_NAME root is $WEST_SIM_ROOT"
