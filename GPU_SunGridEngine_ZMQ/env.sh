#!/bin/bash

# Set up environment for westpa
# Actviate a conda environment containing westpa, openmm and mdtraj;
# you may need to create this first (see install instructions)

export WEST_SIM_ROOT="$PWD"
export SIM_NAME=$(basename $WEST_SIM_ROOT)

source ~/.bashrc
conda activate westpa
module load cuda/11.2

export PATH=/data01/software/cuda11.2/bin:$PATH
export LD_LIBRARY_PATH=/data01/software/cuda11.2/lib64/:$LD_LIBRARY_PATH
export OPENMM_CUDA_COMPILER=$(which nvcc)
echo $CUDA_VISIBLE_DEVICES

