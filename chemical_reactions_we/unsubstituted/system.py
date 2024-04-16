#!/usr/bin/env python

import numpy 
import westpa
import os
from westpa.core.systems import WESTSystem
from westpa.core.binning import RectilinearBinMapper 
from westpa.core.binning import FuncBinMapper 
from westpa.core.binning import RecursiveBinMapper 
import logging

log = logging.getLogger(__name__)
log.debug('loading module %r' % __name__)

def radial_map(coords, mask, output):                                  
    center = numpy.array((1.6, 1.6))
    coords -= center
    quotients = numpy.divide(coords[:,1],coords[:,0])
    angles = numpy.arctan(quotients)/(2*numpy.pi)*360
    bins = numpy.arange(0,91,1)
    output[mask] = numpy.digitize(angles, bins)[mask]
    return output 
class SDASystem(WESTSystem):
    '''
    Class specify binning schemes, walker counts, and other core weighted
    ensemble parameters.
    '''
    def initialize(self):
        self.pcoord_ndim            = 2
        self.pcoord_len             = 3
        self.pcoord_dtype           = numpy.float32
        
        outer_mapper = RectilinearBinMapper(
                [[0, 1.6, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 'inf'],
                 [0, 1.6, 4, 5, 'inf']]
                                            )
      
#        inner_mapper = RectilinearBinMapper(
#                []
#                                            )
         
        radial_mapper = FuncBinMapper(radial_map, nbins=91)


        self.bin_mapper = RecursiveBinMapper(outer_mapper)
        self.bin_mapper.add_mapper(
                radial_mapper, 
                [1.6,1.6]
                                   )

        self.bin_target_counts = numpy.empty((self.bin_mapper.nbins,), 
                                             dtype=numpy.int)
        self.bin_target_counts[...] = 5
