These are the scripts used for the Barnase-Barstar all-atom WESTPA simulations

- BNBS\_custom\_init
- BNBS\_setup\_scripts

In BNBS\_custom\_init folder you can find the scripts for setting up a WESTPA simulation 
for binding after running WESTPA simulations for both binding partners separately. In this 
case barnase and barstar were simulated separately to explore their internal conformations 
and then the two WESTPA simulations were used to generate the WESTPA simulation setup for 
their binding. This setup generates binding pairs and their joint probabilities, the user
has to then add the waters to each and do equilibration for all of them before running
the WESTPA simulation of binding.

In BNBS\_setup\_scripts folder you can find the scripts and configuration files used for the 
eventual WESTPA simulation of the binding process. The custom initialization gives the west.h5 file 
required for the WESTPA simulation of binding. 
