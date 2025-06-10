import logging
import math
import operator
import random
import pandas as pd

import numpy as np

import westpa
from westpa.core.we_driver import WEDriver
from westpa.core.segment import Segment
from westpa.core.states import InitialState

log = logging.getLogger(__name__)

class MABLDriver(WEDriver):
   
    def _split_by_data(self, bin, to_split, split_into):

        if len(to_split) > 1:
            for segment in to_split:
                bin.remove(segment)
                new_segments_list = self._split_walker(segment, split_into, bin)
                bin.update(new_segments_list)
        else:
            to_split = to_split[0]
            bin.remove(to_split)
            new_segments_list = self._split_walker(to_split, split_into, bin)
            bin.update(new_segments_list)


    def _merge_by_data(self, bin, to_merge):

        bin.difference_update(to_merge)
        new_segment, parent = self._merge_walkers(to_merge, None, bin)
        bin.add(new_segment)


    def _run_we(self):
        '''Run recycle/split/merge. Do not call this function directly; instead, use
        populate_initial(), rebin_current(), or construct_next().'''
        self._recycle_walkers()

        # sanity check
        self._check_pre()

        # dummy resampling block
        for bin in self.next_iter_binning:
            if len(bin) == 0:
                continue
            else:
                # this will just get you the final pcoord for each segment... which may not be enough
                segments = np.array(sorted(bin, key=operator.attrgetter('weight')), dtype=np.object_)
                pcoords_d1 = np.array(list(map(operator.attrgetter('pcoord'), segments)))[:,:,0]
                pcoords_d2 = np.array(list(map(operator.attrgetter('pcoord'), segments)))[:,:,1]
                pcoords_d3 = np.array(list(map(operator.attrgetter('pcoord'), segments)))[:,:,2]
                weights = np.array(list(map(operator.attrgetter('weight'), segments)))

                log_weights = -1 * np.log(weights)
 
                nsegs = pcoords_d1.shape[0]
                nframes = pcoords_d1.shape[1]

                pcoords_d1 = pcoords_d1.reshape(nsegs,nframes)
                pcoords_d2 = pcoords_d2.reshape(nsegs,nframes)
                pcoords_d3 = pcoords_d3.reshape(nsegs,nframes)

                # this will allow you to get the pcoords for all frames
                # here we just use it to check if we are initializing
                current_iter_segments = self.current_iter_segments

                curr_segments = np.array(sorted(current_iter_segments, key=operator.attrgetter('weight')), dtype=np.object_)
                curr_pcoords_d1 = np.array(list(map(operator.attrgetter('pcoord'), curr_segments)))[:,:,0]
                curr_weights = np.array(list(map(operator.attrgetter('weight'), curr_segments)))

                log_weights = -1 * np.log(weights)
 
                nsegs = pcoords_d1.shape[0]
                nframes = pcoords_d1.shape[1]
                
                curr_pcoords_d1 = curr_pcoords_d1.reshape(nsegs,nframes)

                # change the following for different algorithms
                start_d1 = 0
                target_d1 = 25
                
                start_d2 = 350
                target_d2 = -200

                start_d3 = 0
                target_d3 = 10

                progresses_d1 = np.zeros((nsegs), dtype=float)
                progresses_d2 = np.zeros((nsegs), dtype=float)
                progresses_d3 = np.zeros((nsegs), dtype=float)
                
                # find percent change between first and last frame for the first dimension
                for idx, ival in enumerate(pcoords_d1):
                    distance = np.abs(ival[0]-target_d1)/np.abs(start_d1-target_d1)
                    if distance > 1:
                        progress = 0
                    else:
                        progress = float(1-distance)
                    progresses_d1[idx] = progress

                # find percent change between first and last frame for the second dimension
                for idx, ival in enumerate(pcoords_d2):
                    distance = np.abs(ival[0]-target_d2)/np.abs(start_d2-target_d2)
                    if distance > 1:
                        progress = 0
                    else:
                        progress = float(1-distance)
                    progresses_d2[idx] = progress

                # find percent change between first and last frame for the second dimension
                for idx, ival in enumerate(pcoords_d3):
                    distance = np.abs(ival[0]-target_d3)/np.abs(start_d3-target_d3)
                    if distance > 1:
                        progress = 0
                    else:
                        progress = float(1-distance)
                    progresses_d3[idx] = progress

                if 13 > pcoords_d1[:,0][-1] > 10:
                    progresses_d1 *= 0.80

                # this will prioritize trajectories with higher weights
                scaled_progresses = progresses_d1 * progresses_d2 * progresses_d3 * (1/log_weights)

                # this is for if no weights are used, which is not recommended...
                #scaled_progresses = progresses * 1

                pd.set_option('display.colheader_justify', 'center')
                mydf = pd.DataFrame()
                mydf['pcoords d1'] = pcoords_d1[:,0]
                mydf['pcoords d2'] = pcoords_d2[:,0]
                mydf['pcoords d3'] = pcoords_d3[:,0]
                mydf['weights'] = weights
                mydf['scaled progress'] = scaled_progresses
                print("\n", mydf.sort_values(by=['scaled progress']))

                # check if not initializing, then split and merge
                init_check = curr_pcoords_d1[:,0] != curr_pcoords_d1[:,-1]

                if np.any(init_check):

                    # split walker with largest scaled diff
                    split_into = 2

                    to_split_list = np.argsort(-scaled_progresses,axis=0)
                    to_split_idx = []
                                                                                            
                    # don't split out of bounds walkers
                    for idx in to_split_list:
                        if scaled_progresses[idx] != 0 and pcoords_d1[:,0][idx] < target_d1 and pcoords_d2[:,0][idx] > target_d2 and pcoords_d3[:,0][idx] < target_d3:
                            to_split_idx.append(idx)
                                                                  
                    to_split_idx = to_split_idx[:5]
                                                                                            
                    pcoords_to_split_d1 = pcoords_d1[:,0][to_split_idx]
                    pcoords_to_split_d2 = pcoords_d2[:,0][to_split_idx]
                    pcoords_to_split_d3 = pcoords_d3[:,0][to_split_idx]
                                                                                            
                    mydf_split = pd.DataFrame()
                    mydf_split['split index'] = to_split_idx
                    mydf_split['pcoords d1'] = pcoords_to_split_d1
                    mydf_split['pcoords d2'] = pcoords_to_split_d2
                    mydf_split['pcoords d3'] = pcoords_to_split_d3
                    mydf_split['weights'] = weights[to_split_idx]
                    mydf_split['scaled progress'] = scaled_progresses[to_split_idx]
                                                                                            
                    print("\n", mydf_split)
                                                                                            
                    to_split = np.array([segments[to_split_idx]])[0]

                    self._split_by_data(bin, to_split, split_into)
    
                    # merge walker with lowest scaled diff into next lowest

                    to_merge_list = np.argsort(scaled_progresses,axis=0)
                    to_merge_idx = []
                                                                                            
                    # don't merge out of bounds walkers
                    for idx in to_merge_list:
                        if scaled_progresses[idx] != 0 and pcoords_d1[:,0][idx] < target_d1 and pcoords_d2[:,0][idx] > target_d2 and pcoords_d3[:,0][idx] < target_d3:
                            to_merge_idx.append(idx)
                                                                                            
                    to_merge_idx = to_merge_idx[:6]
                            
                    pcoords_to_merge_d1 = pcoords_d1[:,0][to_merge_idx]
                    pcoords_to_merge_d2 = pcoords_d2[:,0][to_merge_idx]
                    pcoords_to_merge_d3 = pcoords_d3[:,0][to_merge_idx]
                                                                                            
                    mydf_merge = pd.DataFrame()
                    mydf_merge['merge index'] = to_merge_idx
                    mydf_merge['pcoords d1'] = pcoords_to_merge_d1
                    mydf_merge['pcoords d2'] = pcoords_to_merge_d2
                    mydf_merge['pcoords d3'] = pcoords_to_merge_d3
                    mydf_merge['weights'] = weights[to_merge_idx]
                    mydf_merge['scaled progress'] = scaled_progresses[to_merge_idx]
                                                                                            
                    print("\n", mydf_merge)

                    to_merge = segments[to_merge_idx]

                    self._merge_by_data(bin, to_merge)

        # another sanity check
        self._check_post()

        self.new_weights = self.new_weights or []

        log.debug('used initial states: {!r}'.format(self.used_initial_states))
        log.debug('available initial states: {!r}'.format(self.avail_initial_states))
