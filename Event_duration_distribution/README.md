# Python script for plotting the probability distribution of event duration times
# from a WESTPA simulation
# by Alex J. DeGrave

In the main script, specify the HDF5 file (direct.h5) from your WESTPA simulation and the 
total number of weighted ensemble iterations, target state, and tau-value in ns. 
The output from running the script will be a plot titled "durations.pdf". 
As an example, the direct.h5 file from the Basic WESTPA tutorial in 
Bogetti et al. LiveCoMS J. (2019) is provided. This tutorial involves the simulation of 
Na+/Cl- association using 100 weighted ensemble iterations. 
