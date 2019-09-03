#!/bin/bash
#$ -N build_state
#$ -q compute48.q
#$ -l h_rt=36:00:00
#$ -pe same_node 48
#$ -V
#$ -cwd

source env.sh || exit 1
source source_we.sh || exit 1

cd $WEST_SIM_ROOT
SERVER_INFO=$WEST_SIM_ROOT/west_zmq_info-$JOB_ID.json

# start server
python build_state_dist_bb.py --reference min.gro --bn unbound.gro --bs barstar.gro --bn_path $PWD/000146/ --bs_path $PWD/000163/ bn_west.h5 bs_west.h5 --wm-work-manager=zmq --wm-n-workers=0 --wm-zmq-mode=server --wm-zmq-info=$SERVER_INFO --debug &> state_build.log &

# wait on host info file up to one minute
for ((n=0; n<60; n++)); do
    if [ -e $SERVER_INFO ] ; then
        echo "== server info file $SERVER_INFO =="
        cat $SERVER_INFO
        break
    fi
    sleep 1
done

# exit if host info file doesn't appear in one minute
if ! [ -e $SERVER_INFO ] ; then
    echo 'server failed to start'
    exit 1
fi

# start clients, with the proper number of cores on each
while read -r machine ncores _j _k ; do 
   qrsh -inherit -V $machine $PWD/node.sh --reference min.gro --bn unbound.gro --bs barstar.gro --bn_path $PWD/000146/ --bs_path $PWD/000163/ bn_west.h5 bs_west.h5 --wm-work-manager=zmq --wm-zmq-mode=client --wm-n-workers=$ncores --wm-zmq-info=$SERVER_INFO &> west-$JOB_ID-$machine.log &
done < $PE_HOSTFILE

wait
