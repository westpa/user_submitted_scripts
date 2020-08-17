# Original written by Matt Zwier, modified by Ali Sinan Saglam to work with Barnase-Barstar

'''
Using results from WE explorations of component RMSDs, construct a WE simulation
for (equilibrium) binding.
'''

from __future__ import print_function, division; __metaclass__ = type

import os, sys, argparse
import numpy, h5py
from scipy.spatial.distance import cdist

import westpa
import work_managers

import MDAnalysis
import MDAnalysis.analysis.align as mdaa #@UnresolvedImport

def gen_rand_Q():
    '''Generate a random rotation matrix Q which can be used to randomly reorient
    a molecule with numpy.dot(coord_array, Q). The matrix is generated according
    to the prescription of J. Arvo in "Fast random rotation matrices" in
    Graphics Gems III (1992).'''
    
    x = numpy.random.uniform(size=(3,))
    twopix = 2*numpy.pi*x
    cx = numpy.cos(twopix)
    sx = numpy.sin(twopix)
    sqrtx2 = x[2]**0.5
    I = numpy.matrix([[1,0,0],[0,1,0],[0,0,1]])
    R = numpy.matrix([[cx[0], sx[0], 0],[-sx[0], cx[0], 0], [0, 0, 1]])
    v = numpy.matrix([[cx[1]*sqrtx2],[sx[1]*sqrtx2], [(1-x[2])**0.5]])
    Q = numpy.array(-(I - 2*v*v.T)*R)
    assert numpy.allclose(Q.T, numpy.linalg.inv(Q)) # check orthogonality
    assert abs(numpy.linalg.det(Q)-1) < 1.0e-14     # check unitarity
    return numpy.matrix(Q)

# Define loaders
def bs_coord_loader(gro_path):
    uni = MDAnalysis.Universe(gro_path)
    bs_coord = uni.selectAtoms('bynum 1-1432').coordinates()
    del uni
    return bs_coord

def bn_coord_loader(gro_path):
    uni = MDAnalysis.Universe(gro_path)
    bn_coord = uni.selectAtoms('bynum 1-1727').coordinates()
    del uni
    return bn_coord

# Define a function to return iter/seg pair given segNo and a segments list
#def get_is(segList, segNo):
    #c_segs = numpy.cumsum(segList)
    #for i,j in enumerate(c_segs):
        #if segNo < j: 
            #iterNo = i+1
            #if i > 0:
                #segIt = segNo - c_segs[i-1] 
            #else:
                #setIt = segNo
            #return iterNo, segIt

class StateBuilder:
    def __init__(self, reference_filename):
        self.reference_filename = reference_filename
        
        ref_uv = self.ref_uv = MDAnalysis.Universe(self.reference_filename)
        self.output_uv = MDAnalysis.Universe(self.reference_filename)
        
        self.ref_atoms = ref_uv.selectAtoms('all')
        self.ref_bn_atoms = ref_uv.selectAtoms('bynum 1:1727')
        self.ref_bs_atoms  = ref_uv.selectAtoms('bynum 1728:3159') 
        
        self.atomic_masses = self.ref_atoms.masses()
        
        self.heavy_indices = self.ref_atoms.selectAtoms('not name H*').indices()
        self.bn_indices = self.ref_bn_atoms.indices()
        self.bs_indices = self.ref_bs_atoms.indices()
        self.bn_heavy_indices = self.ref_bn_atoms.selectAtoms('not name H*').indices()
        self.bs_heavy_indices  = self.ref_bs_atoms.selectAtoms('not name H*').indices()
        
        self._update_ref_coords()
        
    def _update_ref_coords(self):
        self._ref_coords = self.ref_atoms.positions.copy()
        
    def translate(self, coords, indices, to=[0,0,0], weights=None, subset=None):
        '''Return a copy of ``coords``, translated so that the center of mass of the atoms
        at indices ``indices`` corresponds to the point ``to`` (which is the origin by
        default).'''
        
        if weights is None:
            weights = self.atomic_masses[indices]
            
        to = numpy.asanyarray(to)
        
        com = numpy.average(coords[indices,:], axis=0, weights=weights)
        
        if subset is not None:
            return coords[subset] - com + to
        else:
            return coords - com + to
    
    def rotate(self, coords, R):
        '''Return a copy of ``coords``, rotated by the matrix ``R``'''
        return coords * numpy.matrix(R).T
    
    def align_on(self, coords, indices, weights=None, subset=None):
        '''Align the structure with coordinates ``coords`` on the reference structure,
        using only atoms at the given ``indices``.  Returns ``(new_coords, rmsd)``, where
        ``new_coords`` is the aligned structure and ``rmsd`` is the RMSD after alignment.'''
        
        if weights is None:
            weights = self.atomic_masses[indices]
             
        ref_coords = self._ref_coords.copy()
        
        coord_com =  numpy.average(coords[indices,:], axis=0, weights=weights)
        ref_com   =  numpy.average(self._ref_coords[indices,:], axis=0, weights=weights)
    
        new_coords = coords - coord_com # move to origin
        ref_coords -= ref_com           # move ref to origin
        
        # Calculate rotation matrix
        (R, _old_rmsd) = mdaa.rotation_matrix(new_coords[indices], ref_coords[indices], weights=weights)
        new_coords = new_coords * numpy.matrix(R.T)
        
        # Calculate updated RMSD
        (R, new_rmsd) = mdaa.rotation_matrix(new_coords[indices], ref_coords[indices], weights=weights)

        # move structure to coincide with ref
        new_coords += ref_com
        
        if subset is not None:
            new_coords = new_coords[subset]
        
        return new_coords, new_rmsd
    
    def rmsd_to(self, coords, indices, weights=None):
        if weights is None:
            weights = self.atomic_masses[indices]
        
        return mdaa.rotation_matrix(coords[indices], self._ref_coords[indices], weights=weights)[1]
        
    def center_align_reference(self):
        '''Translate barnase to the origin and align barnase's principal axes with
        the Cartesian axes.'''
        
        bn_heavy_atoms = self.ref_bn_atoms.selectAtoms('not name H*')
        com = bn_heavy_atoms.centerOfMass()
        self.ref_atoms.translate(-com)
        U, S, V = numpy.linalg.svd(bn_heavy_atoms.momentOfInertia())
        self.ref_atoms.rotate(V)
        self._update_ref_coords()
        
    def write_structure(self, coords, filename):
        self.output_uv.selectAtoms('all').positions = coords
        self.output_uv.selectAtoms('all').write(filename)
        

parser = argparse.ArgumentParser()
westpa.rc.add_args(parser)
parser.add_argument('-d', '--distance', type=float, default=20.0, help="minimum separation of partners in A ")
parser.add_argument('--reference', default='min.gro',
                    help='reference for RMSD and template GRO for output ')
parser.add_argument('--bn', default='barnase.gro',
                    help='structure file for barnase')
parser.add_argument('--bs', default='barstar.gro',
                    help='structure file for barstar')
parser.add_argument('-o', '--output', default='basis.h5',
                    help='store output in OUTPUT') 
parser.add_argument('--bn_path', type=str ,help='Path to the barnase simulation')
parser.add_argument('--bs_path', type=str ,help='Path to the barstar simulation')
parser.add_argument('bn_h5', help='BN HDF5 file')
parser.add_argument('bs_h5', help='BS HDF5 file')
work_managers.environment.add_wm_args(parser)

args = parser.parse_args()
westpa.rc.process_args(args)
work_managers.environment.process_wm_args(args)
westpa.rc.work_manager = work_manager = work_managers.environment.make_work_manager()

print("Making state builder")
sb = StateBuilder(args.reference)
sb.center_align_reference()

print("Opening up h5 files")
input_1_h5 = h5py.File(args.bn_h5, 'r')
input_2_h5 = h5py.File(args.bs_h5, 'r')

print("Pulling current iterations")
cur_iter_1 = (input_1_h5.attrs['west_current_iteration'] - 1)
cur_iter_2 = (input_2_h5.attrs['west_current_iteration'] - 1)

group_1 = input_1_h5['/iterations/iter_{:08d}'.format(cur_iter_1)]
group_2 = input_2_h5['/iterations/iter_{:08d}'.format(cur_iter_2)]

print("Pulling weights")
weights_1 = group_1['seg_index']['weight']
weights_2 = group_2['seg_index']['weight']

############################################
# For segs, use summary, we already know the number of atoms
segList_1 = input_1_h5['summary']['n_particles']
nsegs_1 = segList_1[(cur_iter_1 - 1)]
natoms_1 = 1727
segList_2 = input_2_h5['summary']['n_particles']
nsegs_2 = segList_2[(cur_iter_2 - 1)]
natoms_2 = 1432

natoms_total = natoms_1+natoms_2
nstructs_total = nsegs_1*nsegs_2

#coords_1 = group_1['auxdata/coords'][:,0,:,:]
#coords_2 = group_2['auxdata/coords'][:,0,:,:]

print('Partner 1: {} segments, {} atoms'.format(nsegs_1, natoms_1))
print('Partner 2: {} segments, {} atoms'.format(nsegs_2, natoms_2))
print('There will be {} candidate structures'.format(nstructs_total))

current_coords = numpy.empty((natoms_total,3), numpy.float32)

def get_reoriented_structures(iseg1):
    print("Working on barnase segment %i"%(iseg1))
    all_coords = numpy.empty((nsegs_2,natoms_total,3), numpy.float32)
    all_weights = numpy.empty((nsegs_2,), numpy.float64)
    all_bn_rmsds = numpy.empty((nsegs_2,), numpy.float32)
    all_bs_self_rmsds = numpy.empty((nsegs_2,), numpy.float32)
    all_bs_orientational_rmsds = numpy.empty((nsegs_2,), numpy.float32)
    
    bn_gro_path = "{}/traj_segs/{:06d}/{:06d}/seg.gro".format(args.bn_path, cur_iter_1, iseg1)
    current_coords[:natoms_1,:] = bn_coord_loader(bn_gro_path)
    (current_coords[:natoms_1,:], bn_rmsd) = sb.align_on(current_coords[:natoms_1,:], sb.bn_heavy_indices)

    for iseg2 in xrange(nsegs_2):
        print("Working on barstar segment %i"%(iseg2))
        #current_coords[natoms_1:,:] = group_2['auxdata/coords'][iseg2,0,:,:]
        # Since we need to load in the coordinates we need to specify the path to the gro
        bs_gro_path = "{}/traj_segs/{:06d}/{:06d}/seg.gro".format(args.bs_path, cur_iter_2, iseg2)
        # Now load in the coordinates from the gro
        current_coords[natoms_1:,:] = bs_coord_loader(bs_gro_path)
     
        # Align barstar and calculate self-RMSD
        (current_coords[natoms_1:,:],bs_self_rmsd) = sb.align_on(current_coords, sb.bs_heavy_indices,
                                                                subset=numpy.s_[natoms_1:])
     
        # Apply random rotation to MDM2, which is already at origin
        current_coords[:natoms_1,:] = current_coords[:natoms_1,:] * gen_rand_Q()
     
        # Translate p53 to the origin and apply a random rotation
        current_coords[natoms_1:,:] = sb.translate(current_coords, sb.bs_heavy_indices, subset=numpy.s_[natoms_1:])
        current_coords[natoms_1:,:] = current_coords[natoms_1:,:] * gen_rand_Q() 
        # Translate p53 so that there is 1.5*args.distance separation in z
        # this is a first approximation to the desired separation
        max_bn_z = current_coords[natoms_1:,2].max()
        min_bs_z  = current_coords[:natoms_1,2].min()
     
        current_coords[natoms_1:,:] = sb.translate(current_coords, sb.bs_heavy_indices,
                                                to=[0,0,1.5*args.distance-min_bs_z+max_bn_z],
                                                subset=numpy.s_[natoms_1:])
             
        # Find minimum separation
        distmat = cdist(current_coords[:natoms_1], current_coords[natoms_1:])
        minpair = numpy.unravel_index(distmat.argmin(), distmat.shape)
        print(minpair, distmat[minpair], distmat.min())
     
        # translate all atoms of p53 along the line between the minimum 
        # separated atoms of p53/MDM2 so that the min dist becomes the target dist
        sep_vec = current_coords[natoms_1 + minpair[1],:] - current_coords[minpair[0],:]
        unit_sep = sep_vec / (sep_vec*sep_vec).sum()**0.5
        desired_sep_vec = unit_sep * args.distance
        delta_sep = desired_sep_vec - sep_vec
        current_coords[natoms_1:,:] += delta_sep
     
        # Calculate min dist (check)
        distmat = cdist(current_coords[:natoms_1], current_coords[natoms_1:])
        minpair = numpy.unravel_index(distmat.argmin(), distmat.shape)
        print(minpair, distmat[minpair], distmat.min())
     
        # Align on MDM2 for RMSD calculation (and leave there for beginning of simulation)
        (current_coords[:,:], _junk) = sb.align_on(current_coords, sb.bn_heavy_indices)
     
        bs_crossalign_rmsd = sb.rmsd_to(current_coords, sb.bs_heavy_indices)
     
        combined_weight = weights_1[iseg1] * weights_2[iseg2]
     
        print('(Bn {}, bs {}) weight={}'.format(iseg1, iseg2, combined_weight))

        all_coords[iseg2] = current_coords
        all_weights[iseg2] = combined_weight
        all_bn_rmsds[iseg2] = bn_rmsd
        all_bs_self_rmsds[iseg2] = bs_self_rmsd
        all_bs_orientational_rmsds[iseg2] = bs_crossalign_rmsd
        del distmat, sep_vec, unit_sep, desired_sep_vec, delta_sep
        
    return {'coords': all_coords,
            'weight': all_weights,
            'bn_rmsd': all_bn_rmsds,
            'bs_self_rmsd': all_bs_self_rmsds,
            'bs_orientational_rmsd': all_bs_orientational_rmsds}
    

with work_manager:
    if work_manager.is_master:
        sb.write_structure(sb.ref_atoms.positions, 'ref.pdb')
        
        offset = 0
        out_h5 = h5py.File(args.output)
        
        weight_ds = out_h5.require_dataset('weight', shape=(nstructs_total,), dtype=numpy.float64,
                                          compression=9, shuffle=True)
        bn_rmsd_ds = out_h5.require_dataset('bn_rmsd', shape=(nstructs_total,), dtype=numpy.float32,
                                             scaleoffset=3)
        bs_self_rmsd_ds = out_h5.require_dataset('bs_self_rmsd', shape=(nstructs_total,), dtype=numpy.float32,
                                                 scaleoffset=3)
        bs_orientl_rmsd_ds = out_h5.require_dataset('bs_orientl_rmsd', shape=(nstructs_total,), dtype=numpy.float32,
                                                    scaleoffset=3)
        coords_ds = out_h5.require_dataset('coords', shape=(nstructs_total, natoms_total, 3), chunks=(25,natoms_total,3),
                                          dtype=numpy.float32, scaleoffset=3)
        
        futures = set(work_manager.submit_many([(get_reoriented_structures, [x], {}) for x in xrange(nsegs_1)]))
        for future in work_manager.as_completed(futures):
            print('writing at position {}'.format(offset))
            allstructdat = future.get_result()
            futures.remove(future)
        
        #for iseg1 in xrange(1):#nsegs_1):
            #allstructdat = get_reoriented_structures(iseg1)
            
            weight_ds[offset:offset+nsegs_2] = allstructdat['weight']
            bn_rmsd_ds[offset:offset+nsegs_2] = allstructdat['bn_rmsd']
            bs_self_rmsd_ds[offset:offset+nsegs_2] = allstructdat['bs_self_rmsd']
            bs_orientl_rmsd_ds[offset:offset+nsegs_2] = allstructdat['bs_orientational_rmsd']
            coords_ds[offset:offset+nsegs_2,:,:] = allstructdat['coords']
            offset += nsegs_2
            
            out_h5.flush()
            
            del allstructdat
            
            #sb.write_structure(current_coords, 'aligned.pdb')
    else:
        work_manager.run()
