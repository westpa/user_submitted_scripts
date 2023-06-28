Overview
--------

DEPRECATION WARNING: These versions of the Adaptive Algorithm (Minimal Adaptive Binning/MAB) is deprecated in favor of the bullt-in MAB BinMapper in WESTPA 2.0 (v2022.XX). The BinMapper includes the same functionality. For more information, see Tutorial 7.6 in our WESTPA Tutorials (https://github.com/westpa/tutorials).

These are the instructions and necessary files needed for running the Adaptive Algorithm. The adaptive algorithm is designed to be used in n dimensions and with the enhanced feature favor multiple unique trajectories. Refer to (future paper) for more information.

Using the script
----------------

1.	Download the following three files from Github Repository adaptive.py, manager.py, driver.py and place them in the directory you are running the simulation from (WEST_SIM_ROOT)
2.	In your west.cfg file you want the following
west:
  system:
    driver: adaptive.System
    module_path: $WEST_SIM_ROOT
  drivers:
    sim_manager: manager.WESimManager
    module_path: $WEST_SIM_ROOT
    we_driver: driver.WEDriver
3.	 Make desired changes to adaptive.py (instructions within file)

