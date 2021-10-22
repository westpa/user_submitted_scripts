Shell scripts for running WESTPA on GPUs on PSC Bridges-2
---------------------------------------------------------

This collection of shell scripts will work on a single GPU node or across multiple GPU nodes. To use these scripts, move them into your main simulation directory. The runwe_bridges2_gpu.sh script will start the zmq work manager, which will manually ssh into each node requested and execute the node.sh script, which will execute w_run.  

Please modify your installation paths and project directories before running. ``#MODIFY`` indicate locations where user-dependent parameters will need to be changed.
