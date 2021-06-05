# This file defines where WEST and GROMACS can be found
# Modify to taste
case $HOSTNAME in
    assign)
        # Find EPD and GROMACS
        source /etc/profile.d/modules.sh
        module load epd
        module load gromacs

        # Inform WEST where to find Python and our other scripts where to find WEST
        export WEST_PYTHON=$(which python2.7)
        export WEST_ROOT=$HOME/westpa
        export USE_LOCAL_SCRATCH=0
        export SWROOT=""
    ;;

    ltc1|compute8*|compute48*)
        source /etc/profile.d/modules.sh
        module load epd
        module load gromacs
        export WEST_PYTHON=$(which python2.7)
        export WEST_ROOT=$HOME/westpa.devel
        export USE_LOCAL_SCRATCH=1
        export SWROOT=""
    ;;
    # gordon

    g*)
        export USE_LOCAL_SCRATCH=1
	export GRO_BIN=/oasis/scratch/alisingl/temp_project/nacl_we/apps/gromacs/bin/
        export WEST_PYTHON=/oasis/scratch/alisingl/temp_project/nacl_we/apps/epd/bin/python2.7
        export WEST_ROOT=/oasis/scratch/alisingl/temp_project/nacl_we/apps/westpa.devel/
	#export WEST_ROOT=/home/alisingl/west_new/westpa/
        export SWROOT=""

    ;;
    
    *)
        export TMPDIR=/var/tmp
        export USE_LOCAL_SCRATCH=0

        SCRATCH=/lustre/scratch/mczwier
        export SWROOT=$SCRATCH/gentoo
        export WEST_ROOT=/lustre/scratch/mczwier/westpa.devel
        export AMBERHOME=$SWROOT/opt/amber12
        export WEST_PYTHON=$SWROOT/opt/epd/bin/python2.7

        export GREP=$SWROOT/bin/grep

        if ! echo $LD_LIBRARY_PATH | $GREP $SWROOT &> /dev/null ; then
            export LD_LIBRARY_PATH="$SWROOT/lib:$SWROOT/usr/lib/gcc/x86_64-pc-linux-gnu/4.5.3"
        fi

        if ! echo $PATH | $GREP $SWROOT &> /dev/null ; then
            export PATH="$SWROOT/bin:$SWROOT/usr/bin"
        fi

        
    ;;
esac

# Divine a queue-independent job ID
if [[ -n "$PBS_JOBID" ]] ; then WEST_JOBID=$PBS_JOBID ; # PBS
elif [[ -n "$JOB_ID" ]]; then WEST_JOBID=$PBS_JOBID ;   # GridEngine
else WEST_JOBID="${HOSTNAME}.$$"
fi
export WEST_JOBID

# Explicitly name our simulation root directory
if [[ -z "$WEST_SIM_ROOT" ]]; then
    export WEST_SIM_ROOT="$PWD"
fi
export SIM_NAME=$(basename $WEST_SIM_ROOT)
echo "simulation $SIM_NAME root is $WEST_SIM_ROOT (job ID $WEST_JOBID)"

export WM_ZMQ_TASK_TIMEOUT=7200
export WM_ZMQ_HEARTBEAT_INTERVAL=600
