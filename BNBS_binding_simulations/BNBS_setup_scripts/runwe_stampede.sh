#!/bin/bash
#SBATCH -J BNBS_new
#SBATCH -p normal
#SBATCH -n 1600
#SBATCH -t 24:00:00
#SBATCH --mail-user=asinansaglam@gmail.com

set -x

cd $SLURM_SUBMIT_DIR

pwd 

source env.sh || exit 1

cd $WEST_SIM_ROOT

SERVER_INFO=$WEST_SIM_ROOT/west_zmq_info-$WEST_JOBID.json

# start dedicated server
$WEST_ROOT/bin/w_run --debug --work-manager=zmq --n-workers=0 --zmq-mode=server --zmq-info=$SERVER_INFO &> west-$WEST_JOBID.log &


# wait on host info file up to ten minutes
for ((n=0; n<60; n++)); do
    date
    if [ -e $SERVER_INFO ] ; then
        echo "== server info file $SERVER_INFO =="
        cat $SERVER_INFO
        break
    fi
    sleep 10
done

# exit if host info file doesn't appear in time
if ! [ -e $SERVER_INFO ] ; then
    echo 'server failed to start'
    kill %1
    exit 1
fi

# start clients
for node in $(scontrol show hostname $SLURM_NODELIST); do
    ssh $node $WEST_SIM_ROOT/node_stampede.sh $WEST_JOBID --debug --work-manager=zmq --zmq-mode=client --zmq-info=$SERVER_INFO &
    sleep 5
done

wait

