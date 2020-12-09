Overview
--------

The Python script (rate.py) was written by Alex J. DeGrave (ajd98) and Anthony Bogetti (atbogetti)
and allows users to apply the RED scheme to their simulation analysis. A WESTPA-generated hdf5 file
(direct.h5, which is the output of w_ipa analysis) is used as input and users are provided with a
numpy array of corrected rates for a single simulation at a time. The current script corrects one 
simulation at a time but users can adapt it based on their needs to iterate through a number of
simulations, saving off a numpy array of corrected rates for each.

Using the script
----------------

To run the script, please specify the following in "rate.py": 

* HDF5 file (direct.h5) from your WESTPA simulation
* total number of weighted ensemble iterations
* number of timepoints per iteration
* tau-value in picoseconds
* concentration in Molar 

The outputs from running the script will be two numpy arrays titled "raw_rates.npy" and "rates.npy".
The "rates.npy" is the corrected set of rates.

Users can then load a series of .npy files into the included plot.py script, which will calculate
a mean rate and 95% CI from a set of rate arrays and plot them in the file "rates.pdf" for viewing.
You should change index for plot limits and labels according to your particular system.
