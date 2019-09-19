# Files for running WESTPA on GPUs
Move this env.sh, runwe_bridges.sh and node.sh into your main simualtion directory.
This run script will start the zmq work manager, which will manually ssh into each
node requested and execute the node.sh script, which will execute w_run.  This collection
of scripts will work on a single GPU node or on multiple GPU nodes.
