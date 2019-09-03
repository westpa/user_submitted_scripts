'''
Take a HDF5 file with a bunch of weighted structures, put them all in one
bin space, and run WE to generate a new WE simulation, including writing 
initial state files.
'''

from __future__ import print_function, division; __metaclass__ = type

import os, sys, argparse, operator, random, collections
from itertools import izip
from math import ceil, floor
import numpy, h5py
from bitarray import bitarray

class IntSet(collections.MutableSet):
    def __init__(self, size_or_iterable=None):
        if size_or_iterable is None:
            self._bitarray = bitarray()
        elif numpy.isscalar(size_or_iterable):
            self._bitarray = bitarray(size_or_iterable)
            self._bitarray.setall(False)
        elif isinstance(size_or_iterable,IntSet):
            self._bitarray = size_or_iterable._bitarray.copy()
        else:
            self._bitarray = bitarray()
            for x in size_or_iterable:
                self.add(x)
        
    def __repr__(self):
        return '<{} at 0x{:x} containing {} elements>'.format(self.__class__.__name__, id(self), len(self))
    
    def __str__(self):
        return str(set(self))
        
    def __len__(self):
        return self._bitarray.count()
    
    def __contains__(self, value):
        try:
            return self._bitarray[value]
        except IndexError:
            return False
    
    def __iter__(self):
        return self._bitarray.itersearch(bitarray([True]))
    
    def add(self, value):
        if len(self._bitarray) <= value:
            self._bitarray.extend([False]*(value - len(self._bitarray)+1))
        self._bitarray[value] = True
        
    def discard(self, value):
        if value < len(self._bitarray):
            self._bitarray[value] = False
            
    def as_bitarray(self):
        return self._bitarray.copy()

       
class WTElement:
    def __init__(self, input=None, output=None):
        # each is a list of (history ID, weight) pairs
        self.input = list(input) or []
        if not output:
            self.output = list(self.input)
        else:
            self.output = list(output)
        
    def __repr__(self):
        return '<{} at 0x{}: input={}, output={}>'.format(self.__class__.__name__, id(self), self.input, self.output)
    
    @classmethod
    def combined(cls, wt_elements, N=None):
        '''Build a new WTElement combining all walkers (input and output) from ``wt_elements``.
        If a desired walker count ``N`` is given, then renormalize to that number of walkers.'''
        
        combined_input = []
        combined_output = []
        for w in wt_elements:
            combined_input.extend(w.input)
            combined_output.extend(w.output)
        
        wte = cls(input=combined_input, output=combined_output)
        if N:
            wte.renorm(N)
        return wte
                    
    @property
    def weight(self):
        return sum(wt for (_id, wt) in self.input)
                    
    def renorm(self, N):
        '''Choosing history with appropriate probability from input walkers, generate
        N output walkers from input walkers, discarding current output walkers.'''
        
        tot_wt = self.weight
        cum_wt = numpy.add.accumulate([i[1] for i in self.input])
        
        # New output weight
        owt = tot_wt / N
        
        output_walkers = []
        for i in xrange(N):
            iparent = numpy.digitize((random.uniform(0,tot_wt),), cum_wt)[0]
            assert iparent < len(self.input)
            output_walkers.append((self.input[iparent][0], owt))
        self.output = output_walkers
        
    def combine_with(self, wt_element, N=None):
        '''Combine the input walkers from ``wt_element`` with those contained in this
        object and optionally renormalize output walkers. If an output walker count ``N`` is
        given, then renormalize to that walker count, otherwise, simply merge the output
        walker lists.'''
        
        self.input.extend(wt_element.input)
        self.output.extend(wt_element.output)
        if N:
            self.renorm(N)
            
    def __len__(self):
        return len(self.output)
        
        

class LeanWE:
    '''Per-bin WE class'''
    def __init__(self):
        # Bin ID (for logging weight transfers)
        self.bin_id = None
        
        # Current walkers (after recycling)       
        self.input_weights = [] # vector of weights
        self.input_history_ids = [] # vector of history (trajectory) IDs
        self.output_groups = None
        
        self.merge_ub = 0.5
        self.split_lb = 2.0
        self.exact_counts = False
        self._merged_walkers = None    
    
    def run_we(self, n_desired):
        self.wtlog = None
        self._merged_walkers = None
        
        input_weights = numpy.array(self.input_weights)
        input_history_ids = numpy.array(self.input_history_ids)
        input_ids = numpy.arange(len(input_weights), dtype=numpy.int32)
        sort_indices = numpy.argsort(input_weights, kind='heapsort')
        
        input_history_ids = input_history_ids[sort_indices]
        input_weights = input_weights[sort_indices]

        del sort_indices
        
        output_groups = []
        
        total_weight = input_weights.sum() 
        ideal_weight = total_weight / n_desired
        
        merge_stop = numpy.searchsorted(input_weights, [ideal_weight*self.merge_ub], side='right')
        split_start = numpy.searchsorted(input_weights, [ideal_weight*self.split_lb], side='left')
        
        # Allow all walkers not subject to split/merge to continue unchanged
        output_weights = input_weights[merge_stop:split_start]
        output_parent_ids = input_ids[merge_stop:split_start]
        
        for (pid, weight) in izip(output_parent_ids, output_weights):
            print('  walker {} (weight {}) continues'.format(pid, weight))
            output_groups.append(WTElement([(pid,weight)]))
        
        # split
        for (pid, weight) in izip(input_history_ids[split_start:], input_weights[split_start:]):
            ratio = weight / ideal_weight
            n_new = int(ceil(ratio))            
            print('  walker {} (weight {}) splits into {} (ratio {})'.format(pid, weight, n_new, ratio))
            n_new = int(ceil(weight / ideal_weight))
            
            gp = WTElement([(pid,weight)])
            gp.renorm(n_new)
            output_groups.append(gp)
        
        # merge
        max_glom_wt = ideal_weight*self.merge_ub
        merge_start = 0
        while merge_start < merge_stop:
            cum_wts = numpy.add.accumulate(input_weights[merge_start:merge_stop])
            glom_stop = numpy.searchsorted(cum_wts, max_glom_wt , side='right') + merge_start
            print('  merging {} walkers into 1 of weight {}'.format(glom_stop-merge_start,
                                                                    input_weights[merge_start:glom_stop].sum()))
            gp = WTElement([(pid,wt) for (pid,wt) in izip(input_history_ids[merge_start:glom_stop], input_weights[merge_start:glom_stop])])
            gp.renorm(1)
            output_groups.append(gp)
            merge_start = glom_stop
            
        # adjust count
        output_wt = sum(gp.weight for gp in output_groups)
        n_output_walkers = sum(len(gp.output) for gp in output_groups)
        print('  --> {} walkers of total weight {} (original weight {})'.format(n_output_walkers, output_wt, total_weight))
        
        if self.exact_counts and n_output_walkers != n_desired:
            while n_output_walkers > n_desired:
                n_excess = n_output_walkers - n_desired
                orig_output_groups = sorted(output_groups, key=operator.attrgetter('weight'))
                print('  too many walkers; merging two lowest-weight groups')
                
                gp = WTElement.combined(orig_output_groups[:2])
                gp.renorm(max(len(gp.output)-n_excess,1))
                output_groups = [gp] + orig_output_groups[2:]
                n_output_walkers = sum(len(gp.output) for gp in output_groups)
                del orig_output_groups
                
            while n_output_walkers < n_desired:
                print('  too few walkers; splitting highest-weight group')
                orig_output_groups = sorted(output_groups, key=operator.attrgetter('weight'))
                orig_output_groups[-1].renorm(len(orig_output_groups[-1])+1)
                output_groups = orig_output_groups
                n_output_walkers = sum(len(gp.output) for gp in output_groups)
                del orig_output_groups
                
            assert n_output_walkers == n_desired, 'count adjustment not correct'
                
        output_wt = sum(gp.weight for gp in output_groups)
        n_output_walkers = sum(len(gp.output) for gp in output_groups)
        print('  --> {} walkers of total weight {} (original weight {})'.format(n_output_walkers, output_wt, total_weight))
        assert abs(output_wt - total_weight) < numpy.finfo(numpy.float64).eps*len(self.input_weights), 'weight not conserved'
        self.output_groups = output_groups
        
        #print('  walkers merged out of existence: {}'.format(list(self.merged_walkers)))
        
    
    @property
    def output_walkers(self):
        '''Yield all output walkers (for next iteration) as an iterator of (history ID, weight) pairs'''
        for ogrp in self.output_groups:
            for pair in ogrp.output:
                yield pair
                
    @property        
    def merged_walkers(self):
        if self._merged_walkers is not None:
            return iter(self._merged_walkers)
        else:
            input_id_set = IntSet(self.input_history_ids)
            output_id_set = IntSet()
            for gp in self.output_groups: 
                output_id_set |= [ow[0] for ow in gp.output]
            
            self._merged_walkers = input_id_set - output_id_set
            return iter(self._merged_walkers) 
                    
if __name__ == '__main__':
    import westpa
    import west
    from west.states import BasisState, InitialState
    from west import Segment
    
    import MDAnalysis
            
    
    parser = argparse.ArgumentParser()
    westpa.rc.add_args(parser)
    parser.add_argument('-b', '--basis-file', default='basis.h5',
                        help='Basis (mega)state is in BASIS_FILE (default: %(default)s)')
    parser.add_argument('-t', '--template-file', default='ref_2.pdb',
                        help='Template file (to write initial state coordinates)')
    
    
    
    args = parser.parse_args()
    westpa.rc.process_args(args)
    
    system = west.rc.get_system_driver()
    data_manager = west.rc.get_data_manager()
    h5file = data_manager.we_h5filename
    try:
        os.unlink(h5file)
    except OSError as e:
        pass
    data_manager.prepare_backing()
    
    uv = MDAnalysis.Universe(args.template_file)
    
    bstate = BasisState('extsim', 1.0, pcoord=[0.0, 0.0, 0.0, 0.0], auxref=args.basis_file, state_id=0)
    data_manager.create_ibstate_group([bstate])
    
    basis_h5 = h5py.File(args.basis_file, 'r')
    bs_norm_rmsd = basis_h5['normal_rmsd'][...]
    min_dist = basis_h5['mindist'][...]
    bs_side_chain = basis_h5['side_rmsd'][...]
    bs_ca = basis_h5['ca_rmsd'][...]
    coord_ds = basis_h5['coords']
    all_weight = basis_h5['weight'][...]
    print('Total weight of all possible structures: {}'.format(all_weight.sum()))
    all_pcoord = numpy.column_stack([min_dist, bs_norm_rmsd, bs_ca, bs_side_chain])
    nstructs = len(all_pcoord)
    
    mapper = system.bin_mapper
    assignments = mapper.assign(all_pcoord)
    print('{} structures assigned'.format(len(assignments)))
    counts = numpy.bincount(assignments, minlength=mapper.nbins)
    occ_mask = counts > 0
    occupied = numpy.count_nonzero(counts)
    n_walkers = system.bin_target_counts[occ_mask].sum()
    walker_ids = numpy.arange(nstructs, dtype=numpy.min_scalar_type(nstructs))
    bin_ids = numpy.arange(mapper.nbins, dtype=numpy.min_scalar_type(mapper.nbins))
    print('{} of {} bins occupied, for {} initial walkers'.format(occupied, mapper.nbins, n_walkers))
    
    we = LeanWE()
    
    istate_id = 0
    seg_id = 0
    initial_states = {}
    segments = []
    bin_labels = list(mapper.labels)
    for ibin in bin_ids[occ_mask]:
        in_bin = (assignments == ibin)
        ids = walker_ids[in_bin]
        weights = all_weight[in_bin]
        idset = set(ids)
        target_count = system.bin_target_counts[ibin]
        count = len(ids)
        ideal_weight = weights.sum() / target_count
        print('splitting/merging in bin {} with count {}, w/ bin label {}'.format(ibin, count, bin_labels[ibin]))
        print('  ideal weight={}, min weight={}, max weight={}'.format(ideal_weight, weights.min(), weights.max()))
        
        if (weights > 2*ideal_weight).any():
            print('  need to split')
        if (weights < 0.5*ideal_weight).any():
            print('  need to merge')
            
        we.exact_counts = True
        we.input_weights = weights
        we.input_history_ids = ids
        we.run_we(8)
        
        for (struct_id, weight) in we.output_walkers:
            try:
                istate = initial_states[struct_id]
            except KeyError:
                istate = InitialState(state_id=istate_id, basis_state_id=0, iter_created=1, iter_used=1, 
                                      istate_type=InitialState.ISTATE_TYPE_GENERATED, istate_status=InitialState.ISTATE_STATUS_PREPARED,
                                      pcoord=all_pcoord[struct_id])
                initial_states[struct_id] = istate
                istate_filename = 'istates/struct_{:06d}.gro'.format(istate_id)
                uv.selectAtoms('all').positions = coord_ds[struct_id]
                uv.selectAtoms('all').write(istate_filename)
                print('  wrote {} containing initial state {} from structure {} with weight {}'.format(istate_filename, istate_id, struct_id, weight))
                istate_id += 1
            
            segment = Segment(seg_id=seg_id, n_iter=1, weight=weight, pcoord=system.new_pcoord_array(),
                              status=Segment.SEG_STATUS_PREPARED)
            segment.parent_id = -(istate.state_id+1)
            segment.wtg_parent_ids = [segment.parent_id]
            segment.pcoord[0,] = istate.pcoord[:]
            segments.append(segment)            
            seg_id += 1
        sys.stdout.flush()

    data_manager.save_target_states([], n_iter=1)
    data_manager.create_initial_states(len(initial_states),1)            
    data_manager.update_initial_states(initial_states.values(), n_iter=1)
    data_manager.prepare_iteration(1, segments)
    data_manager.flush_backing()
    data_manager.close_backing()
    
