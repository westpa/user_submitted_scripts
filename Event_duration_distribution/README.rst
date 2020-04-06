Overview
--------

This Python script (eventdurationdist.py) was written by Alex J. DeGrave (ajd98) to generate a plot of the probability 
distribution of the event duration time from a WESTPA simulation. The event duration time is the time required for transitions 
between stable states and does not include the "waiting time" involving fluctuations in the initial stable state. 

Using the script
----------------

To run the script, please specify the following in "eventdurationdist.py": 

* HDF5 file (direct.h5) from your WESTPA simulation
* total number of weighted ensemble iterations
* target state
* tau-value in ns. 

The output from running the script will be a plot titled "durations.pdf". 

As an example, the direct.h5 file from the Basic WESTPA tutorial in the LiveCoMS Journal publication_ is provided. 
This tutorial involves the simulation of Na+/Cl- association using 100 weighted ensemble iterations. 

.. _publication: https://www.livecomsjournal.org/article/10607-a-suite-of-tutorials-for-the-westpa-rare-events-sampling-software-article-v1-0
