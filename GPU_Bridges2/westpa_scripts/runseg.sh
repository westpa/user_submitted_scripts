#!/bin/bash

if [ -n "$SEG_DEBUG" ] ; then
  set -x
  env | sort
fi

cd $WEST_SIM_ROOT
mkdir -pv $WEST_CURRENT_SEG_DATA_REF
cd $WEST_CURRENT_SEG_DATA_REF

ln -sv $WEST_SIM_ROOT/common_files/system.top .

if [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_CONTINUES" ]; then
  sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md.in > md.in
  ln -sv $WEST_PARENT_DATA_REF/seg.rst ./parent.rst
elif [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_NEWTRAJ" ]; then
  sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md.in > md.in
  ln -sv $WEST_PARENT_DATA_REF ./parent.rst
fi

export CUDA_DEVICES=(`echo $CUDA_VISIBLE_DEVICES_ALLOCATED | tr , ' '`)
export CUDA_VISIBLE_DEVICES=${CUDA_DEVICES[$WM_PROCESS_INDEX]}

echo "RUNSEG.SH: CUDA_VISIBLE_DEVICES_ALLOCATED = " $CUDA_VISIBLE_DEVICES_ALLOCATED
echo "RUNSEG.SH: WM_PROCESS_INDEX = " $WM_PROCESS_INDEX
echo "RUNSEG.SH: CUDA_VISIBLE_DEVICES = " $CUDA_VISIBLE_DEVICES

$PMEMD -O -i md.in   -p system.top  -c parent.rst \
          -r seg.rst -x seg.nc      -o seg.log    -inf seg.nfo

#RMSD=$(mktemp)

COMMAND="         parm $WEST_SIM_ROOT/common_files/system.top\n"
COMMAND="$COMMAND trajin ./parent.rst \n"
COMMAND="$COMMAND trajin $WEST_CURRENT_SEG_DATA_REF/seg.nc \n"
COMMAND="$COMMAND reference $WEST_SIM_ROOT/reference/ref.pdb [reference] \n"
COMMAND="$COMMAND autoimage\n"
COMMAND="$COMMAND rms RMS_Heavy (:1-59)&!(@/H) reference out RMS_Heavy.dat \n"
COMMAND="$COMMAND go\n"

echo -e "${COMMAND}" | $CPPTRAJ

COMMAND="         parm $WEST_SIM_ROOT/common_files/system.top\n"
COMMAND="$COMMAND trajin $WEST_CURRENT_SEG_DATA_REF/seg.nc \n"
COMMAND="$COMMAND strip :WAT \n"
COMMAND="$COMMAND trajout $WEST_CURRENT_SEG_DATA_REF/seg-nowat.nc \n"
COMMAND="$COMMAND go\n"

echo -e "${COMMAND}" | $CPPTRAJ

#cat $RMSD | tail -n +2 | awk '{print $2}' > $WEST_PCOORD_RETURN
paste <(cat RMS_Heavy.dat | tail -n +2 | awk {'print $2'}) > $WEST_PCOORD_RETURN

# Clean up
rm -f md.in parent.rst seg.nfo seg.pdb system.top RMS_Heavy.dat

if [ -f "seg-nowat.nc" ]; then
    rm seg.nc && 
    mv seg-nowat.nc seg.nc
fi

#rm -f $RMS
