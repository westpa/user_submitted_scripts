This folder contains the scripts and configuration files for the WESTPA all-atom simulation of 
barnase and barstar binding. To run a simulation like this you would have to use the scripts in
custom initialization to get the west.h5 file required for WESTPA simulations. You also would
have to equilibrate the initial states given by that initialization script. 

There are several things to note in this folder
- There are a lot of hardcoded paths, this is to ensure that the simulation uses
the exact desired versions of all software (e.g. specific force field for GROMACS
specific python with certain libraries and more). 
- This setup uses a plugin called constantratio.TargetRatio which keeps the total 
number of walkers constant. This allows for better computing resource management. 
This is not currently in the main WESTPA repo but it's being ported over right now. 
