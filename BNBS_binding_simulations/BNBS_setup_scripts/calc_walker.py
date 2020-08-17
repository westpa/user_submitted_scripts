# Written by Ali Sinan Saglam, 25-Jul-14

#!/home/ali/apps/anaconda/bin/python

import MDAnalysis as MDA
import MDAnalysis.analysis.hbonds
# Some stuff I wrote 
import custMDAFuncs as CMF
import numpy as np
import scipy as sp
from scipy.spatial.distance import cdist
import argparse

# Parsing time
parser = argparse.ArgumentParser()
parser.add_argument("-g", "--gro_file", dest="gro_file", default="seg.gro",
                  help="input gro file") 
parser.add_argument("-x", "--xtcfile", dest="xtc_file", default="seg.xtc",
                  help="input xtc file") 
parser.add_argument("-sx", "--stat_xray", dest="stat_xray", default="xray_prot.gro",
                  help="Stationary xray object to align onto") 
parser.add_argument("-ef", "--efile", dest="enerFile", default=None,
                  help="State file name") 
parser.add_argument("-o", "--output", dest="output", default=True,
                  help="Turn outputting on and off") 
args = parser.parse_args()

if __name__ == "__main__":
    # Pull the stationary a3
    stat_xray = CMF.MDAloader(args.stat_xray, None)
    # Now pull the mobile a3
    mob_uni   = CMF.MDAloader(args.gro_file, args.xtc_file)
    # Pull the protein
    bn_prot = stat_xray.select_atoms('bynum 1-1727')
    bs_prot = stat_xray.select_atoms('bynum 1728-3159')
    bn_mob = mob_uni.select_atoms('bynum 1-1727')
    bs_mob = mob_uni.select_atoms('bynum 1728-3159')
    # Max frame count
    max_frame = mob_uni.trajectory.totaltime / mob_uni.trajectory.dt
    # Initialize the arrays for the data sets!
    PC_MDIST = np.zeros(max_frame)
    PC_RMSD = np.zeros(max_frame)
    COGs = np.zeros((max_frame,199,3))
    COMs = np.zeros((max_frame,2,3))
    MDID = np.zeros((max_frame,2))
    ESTAT = np.zeros(max_frame)
    # Loop over trajectory for the rest of the analysis 
    for ts in mob_uni.trajectory:
        # Pull the coords
        bn_mob = mob_uni.select_atoms('bynum 1-1727')
        bs_mob = mob_uni.select_atoms('bynum 1728-3159')
        # Distance matrix calculations
        distMat = cdist(bn_mob.coordinates(), bs_mob.coordinates())
        # Add the minimums of these to the array
        PC_MDIST[ts.frame-1] = distMat.min()
        # MDID 
        MDID_ind = np.where(distMat==distMat.min())
        MDID[ts.frame-1] = np.array([MDID_ind[0][0],MDID_ind[1][0]])
        # COGs
        COG_arr = bn_mob.residues[0].center_of_geometry()
        for res in bn_mob.residues[1:]:
            COG_arr = np.vstack((COG_arr, res.center_of_geometry()))
        for res in bs_mob.residues[:]:
            COG_arr = np.vstack((COG_arr, res.center_of_geometry()))
        COGs[ts.frame-1] = COG_arr
        # COMs
        COM_arr = bn_mob.center_of_mass()
        COM_arr = np.vstack((COM_arr, bn_mob.center_of_mass()))
        COMs[ts.frame-1] = COM_arr
        # This is the entire protein rmsd stuff
        CMF.doKabsch(stat_xray, mob_uni, sel='(bynum 1-1727) and not (name H*)')
        PC_RMSD[ts.frame-1] = CMF.calcRMSD(stat_xray, mob_uni, sel="(bynum 1728-3159) and (resnum 35 or resnum 39) and (not (name H*))")
        # ESTAT
        efile = open(args.enerFile)
        efile = efile.readlines()
        efile = map(lambda x: x.replace('\n',''), efile)
        efile = filter(lambda x: x != 'corr.', efile)
        efile = filter(lambda x: x != '', efile)
        ESTAT = np.array(map(np.float32, efile))
    # Now finally, we write the output
    if args.output: 
        np.savetxt("pc_mdist.txt", PC_MDIST)
        np.savetxt("pc_rmsd.txt", PC_RMSD)
        np.savetxt("mdid.txt", MDID)
        np.savetxt("estat.txt", ESTAT)
        np.save("cogs", COGs)
        np.save("coms", COMs)
