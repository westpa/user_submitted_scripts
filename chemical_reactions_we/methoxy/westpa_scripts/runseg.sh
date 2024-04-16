#!/bin/bash

set -x

cd $WEST_SIM_ROOT
mkdir -pv $WEST_CURRENT_SEG_DATA_REF
cd $WEST_CURRENT_SEG_DATA_REF

ln -sv $WEST_SIM_ROOT/common_files/cat5.top .

if [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_CONTINUES" ]; then
  sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md.in > md.in
  ln -sv $WEST_PARENT_DATA_REF/seg_img.rst ./parent.rst
elif [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_NEWTRAJ" ]; then
  sed "s/RAND/$WEST_RAND16/g" $WEST_SIM_ROOT/common_files/md.in > md.in
  ln -sv $WEST_PARENT_DATA_REF/bstate.rst ./parent.rst
fi

sander -O -i md.in   -p cat5.top  -c parent.rst \
          -r seg_img.rst -x seg.nc      -o seg.log    -inf seg.nfo

COMMAND="         parm $WEST_SIM_ROOT/common_files/cat5.top\n" 
COMMAND="$COMMAND trajin $WEST_CURRENT_SEG_DATA_REF/parent.rst\n"
COMMAND="$COMMAND trajin $WEST_CURRENT_SEG_DATA_REF/seg.nc\n"
COMMAND="$COMMAND image center :1\n"
#COMMAND="$COMMAND nativecontacts :1 :2 mindist out distance.dat\n"
COMMAND="$COMMAND nativecontacts :1@1  :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1 :2 mindist out c-n_dist.dat\n"
#COMMAND="$COMMAND nativecontacts :1@5,9,12,16,21,23  :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@5  :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@7  :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@9  :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@12 :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@14 :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@16 :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@21 :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@25 :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND nativecontacts :1@23 :2 mindist out c-n_dist.dat\n"
COMMAND="$COMMAND dihedral imp :1@1 :1@2 :1@3 :1@4 out imp.dat\n"
COMMAND="$COMMAND strip :WAT,ACN\n"
COMMAND="$COMMAND trajout seg.pdb\n"
COMMAND="$COMMAND go"

echo -e "$COMMAND" | cpptraj

COMMAND="         parm $WEST_SIM_ROOT/common_files/cat10.top\n" 
COMMAND="$COMMAND trajin $WEST_CURRENT_SEG_DATA_REF/seg.rst\n"
COMMAND="$COMMAND image center :2\n"
COMMAND="$COMMAND trajout seg_img.rst restart\n"
COMMAND="$COMMAND go"

echo -e "$COMMAND" | cpptraj

# Calculate progress coordinate data
paste <(cat c-n_dist.dat | tail -n +2 | awk {'print $4'})  <(cat c-n_dist.dat | tail -n +2 | awk {'print $7'}) > $WEST_PCOORD_RETURN

# Calculate auxiliary data
cat seg.pdb | grep 'ATOM' | awk '{print $6, $7, $8}' > $WEST_SOLUTE_COORDS_RETURN
cat imp.dat | tail -n +2 | awk {'print $2'}          > $WEST_DIHEDRAL_RETURN
#cat distance.dat | tail -n +2 | awk {'print $2'}     > $WEST_DISTANCE_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $10'}    > $WEST_C5N34_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $13'}    > $WEST_C7N34_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $16'}    > $WEST_C9N34_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $19'}    > $WEST_C12N34_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $22'}    > $WEST_C14N34_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $25'}    > $WEST_C16N34_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $28'}    > $WEST_C21N34_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $31'}    > $WEST_C25N34_RETURN
cat c-n_dist.dat | tail -n +2 | awk {'print $34'}    > $WEST_C23N34_RETURN

# Clean up
#rm -f $TEMP md.in parent.rst seg.nfo seg.pdb c-n_dist.dat distance.dat imp.dat seg.pdb
rm -f $TEMP md.in parent.rst seg.nfo seg.pdb c-n_dist.dat imp.dat seg.pdb

