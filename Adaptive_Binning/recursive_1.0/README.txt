Overview
--------

These are the instructions and necessary files needed for running the Minimal Adaptive Binning Algorithm in a recursive binning scheme. The adaptive algorithm is designed to be used in n dimensions and with the enhanced feature favor multiple unique trajectories. Refer to (Torrillo, Bogetti, and Chong, J Chem. Phys. A, 2021) for more information.

This version includes changes in the "withandor" version and works for westpa 2.0.

Using the script
----------------

1.	Download the following three files from Github Repository system.py, manager.py, driver.py and place them in the directory you are running the simulation from (WEST_SIM_ROOT)
2.	In your west.cfg file you want the following. An example file has been provided.
west:
  system:
    driver: system.SDASystem
    module_path: $WEST_SIM_ROOT
  drivers:
    sim_manager: manager.WESimManager
    module_path: $WEST_SIM_ROOT
    we_driver: driver_threshold.WEDriver
  we:
    smallest_allowed_weight: 1.E-300
    largest_allowed_weight: 1.0
3.	 Make desired changes to system.py (instructions within file)

