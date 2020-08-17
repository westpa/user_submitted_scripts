# Some custom functions I use 
import numpy as np
import MDAnalysis as MDA 
from numpy.linalg import svd
from scipy.spatial.distance import cdist

def doKabsch(uni1, uni2, sel=None):
    '''Assuming uni1 is the stationary'''
    # Translation 
    if sel:
        cent1 = uni1.select_atoms(sel).center_of_geometry()
        cent2 = uni2.select_atoms(sel).center_of_geometry()
    else:
        cent1 = uni1.atoms.center_of_geometry()
        cent2 = uni2.atoms.center_of_geometry()
    # Find the difference vector 
    uni1.atoms.translate(-cent1)
    uni2.atoms.translate(-cent2)
    ### Now onto the rotation
    # Use selection if available
    if sel:
        coords1 = uni1.select_atoms(sel).coordinates()
        coords2 = uni2.select_atoms(sel).coordinates()
    else:
        coords1 = uni1.atoms.coordinates()
        coords2 = uni2.atoms.coordinates()

    covMat = coords1.transpose().dot(coords2)
    # Check if 3x3 now
    # Now onto the SVD calculation
    V,S,W = svd(covMat)
    d = np.sign(np.linalg.det(W.transpose().dot(V.transpose())))
    I_mod = np.identity(3)
    I_mod[2][2] = d
    U = W.transpose().dot(I_mod)
    U = U.dot(V.transpose())
    uni2.atoms.rotate(U.transpose())

def calcRMSD(uni1, uni2, sel=None):
    '''Simple RMSD calculator'''
    if sel:
        coords1 = uni1.select_atoms(sel).coordinates()
        coords2 = uni2.select_atoms(sel).coordinates()
    else:
        coords1 = uni1.atoms.coordinates()
        coords2 = uni2.atoms.coordinates()
    # Now calculate distances
    distMat = cdist(coords1, coords2)
    diag    = np.diag(distMat)
    N = np.float(len(diag))
    return np.sqrt(1/N * (sum(diag**2)))

def MDAloader(gro_file, xtc_file):
    if xtc_file:
        uni = MDA.Universe(gro_file, xtc_file)
    else: 
        uni = MDA.Universe(gro_file)
    return uni

def pair_loader(pair_file):
    open_file = np.loadtxt(pair_file)
    return open_file

def make_idDict(uni):
    resids = {}
    nAtoms = uni.atoms.numberOfAtoms()
    for iatom in range(1,nAtoms+1):
        resids[iatom] = find_resid(uni, iatom)
    return resids

def find_resid(uni, index):
    sel = uni.select_atoms('bynum %i'%(index))
    return sel.resids()[0]

def unique_rows(pairs):
    pairs = np.ascontiguousarray(pairs)
    unique_pairs = np.unique(pairs.view([('',pairs.dtype)]*pairs.shape[1]))
    return unique_pairs.view(pairs.dtype).reshape((unique_pairs.shape[0],pairs.shape[1]))
