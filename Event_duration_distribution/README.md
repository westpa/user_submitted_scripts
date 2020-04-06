# Python script for plotting the probability distribution of event duration time from a WESTPA simulation
# by Alex J. DeGrave

The event duration time is the time required for transitions between stable states and 
therefore does not include the "waiting time" involving fluctuations in the initial stable
state. To generate a plot of the distribution of the event duration time, please specify 
following in "eventdurationdist.py": (i) HDF5 file (direct.h5) from your WESTPA simulation, 
(ii) total number of weighted ensemble iterations, (iii) target state, and (iv) tau-value in ns. 
The output from running the script will be a plot titled "durations.pdf". 

As an example, the direct.h5 file from the Basic WESTPA tutorial in 
Bogetti et al. LiveCoMS J. (2019) is provided. This tutorial involves the simulation of 
Na+/Cl- association using 100 weighted ensemble iterations. 
