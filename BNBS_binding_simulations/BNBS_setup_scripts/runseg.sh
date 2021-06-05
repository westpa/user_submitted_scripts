#!/bin/bash

if [ -n "$SEG_DEBUG" ] ; then
    set -x
    env | sort
fi

cd $WEST_SIM_ROOT

mkdir -pv $WEST_CURRENT_SEG_DATA_REF || exit 1
cd $WEST_CURRENT_SEG_DATA_REF || exit 1

# General variables needed
TPR=eq1.tpr
TOP=bn_bs.top
NDX=bn_bs.ndx

# Set up the run
ln -sv $WEST_SIM_ROOT/{$TOP,$NDX,$TPR,*.mdp,*.itp} .

case $WEST_CURRENT_SEG_INITPOINT_TYPE in
    SEG_INITPOINT_CONTINUES)
        # A continuation from a prior segment
        ln -sv $WEST_PARENT_DATA_REF/seg.gro ./parent.gro
        ln -sv $WEST_PARENT_DATA_REF/seg.trr ./parent.trr
      	ln -sv $WEST_PARENT_DATA_REF/seg.edr ./parent.edr
        cp -L $WEST_PARENT_DATA_REF/seg.top ./parent.top
        cp -L $WEST_PARENT_DATA_REF/seg.ndx ./parent.ndx
        cp -L $WEST_PARENT_DATA_REF/seg.top ./seg.top
        cp -L $WEST_PARENT_DATA_REF/seg.ndx ./seg.ndx
        cp -L $WEST_PARENT_DATA_REF/*itp .
        ln -s $WEST_SIM_ROOT/amber03-star.ff .
        ln -s $WEST_SIM_ROOT/bn_bs.ndx .
        ln -s $WEST_SIM_ROOT/calc_walker.py .
        ln -s $WEST_SIM_ROOT/custMDAFuncs.py .
        ln -s $WEST_SIM_ROOT/ref_2.pdb .
        ${GRO_BIN}grompp -f md-continue.mdp -c parent.gro -t parent.trr -p parent.top -o seg.tpr -n bn_bs.ndx -e parent.edr &> seg_grompp.log || exit 1
    ;;

    SEG_INITPOINT_NEWTRAJ)
        prepFile=$WEST_PARENT_DATA_REF
        NAME=`basename $prepFile|sed 's/.gro//'`
        #NAME=$(echo $prepFile|sed 's/.gro//')
        ln -s $WEST_SIM_ROOT/eqed_istates/${NAME}.gro parent.gro 
        ln -s $WEST_SIM_ROOT/eqed_istates/${NAME}.trr initial.trr
        ln -s $WEST_SIM_ROOT/eqed_istates/${NAME}.edr initial.edr 
        ln -s $WEST_SIM_ROOT/eqed_istates/${NAME}.ndx seg.ndx
        ln -s $WEST_SIM_ROOT/eqed_istates/${NAME}.top seg.top
        ln -s $WEST_SIM_ROOT/eqed_istates/${NAME}*.itp .
        ln -s $WEST_SIM_ROOT/amber03-star.ff .
        ln -s $WEST_SIM_ROOT/bn_bs.ndx .
        ln -s $WEST_SIM_ROOT/calc_walker.py .
        ln -s $WEST_SIM_ROOT/custMDAFuncs.py .
        ln -s $WEST_SIM_ROOT/ref_2.pdb .
        ${GRO_BIN}grompp -f md-continue.mdp -c parent.gro -p seg.top -o seg.tpr -n bn_bs.ndx -e initial.edr -t initial.trr &> seg_grompp.log || exit 1
    ;;

    *)
        echo "unknown init point type $WEST_CURRENT_SEG_INITPOINT_TYPE"
        exit 2
    ;;
esac
    

# Propagate segment
${GRO_BIN}mdrun -s seg.tpr -o seg.trr -x seg.xtc -c seg.gro \
      -e seg.edr -g seg.log &> seg_mdrun.log \
      || exit 1

# Visualization 
echo 1 0|${GRO_BIN}trjconv -f seg.xtc -s seg.tpr -n $NDX -o seg_cluster.xtc -pbc cluster &> cluster.txt || exit 1
${GRO_BIN}trjconv -f seg_cluster.xtc -o seg_nojump.xtc -pbc nojump &> nojump.txt || exit 1
#echo 1 0|${GRO_BIN}trjconv -f seg_nojump.xtc -o seg_nopbc.xtc -s seg.tpr -center -pbc atom &> nopbc.txt || exit 1

# Trim down the seg log to get the energies
grep -A 1 "Coul. recip." seg.log|awk '{print $5}' > energies.txt

# Calculate all the aux data
/home1/02031/alisingl/apps/anaconda/bin/python calc_walker.py -g parent.gro -x seg_nojump.xtc -sx ref_2.pdb -ef energies.txt

# Return the data
paste pc_rmsd.txt pc_mdist.txt > $WEST_PCOORD_RETURN || exit 1
cat cogs.npy > $WEST_COG_RETURN || exit 1
cat coms.npy > $WEST_COM_RETURN || exit 1
cat mdid.txt > $WEST_MINID_RETURN || exit 1
cat estat.txt > $WEST_ESTAT_RETURN || exit 1

# Clean up
rm -f parent.top parent.ndx seg_cluster.xtc *npy *txt mdout.mdp *cpt seg_mdrun.log seg_grompp.log seg_nojump.xtc
