Shell scripts for running WESTPA on GPUs
----------------------------------------

This collection of scripts will work on a single GPU node or across multiple GPU nodes. To use these scripts, move them into your main simulation directory.The run script will start the zmq work manager, which will manually ssh into each
node requested and execute the node.sh script, which will execute w_run.  
