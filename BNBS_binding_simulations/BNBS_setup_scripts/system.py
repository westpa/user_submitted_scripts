from __future__ import division, print_function; __metaclass__ = type
import os, sys, math, itertools
import numpy
import west
from west import WESTSystem
from westpa.binning import RectilinearBinMapper

import logging
log = logging.getLogger(__name__)
log.debug('loading module %r' % __name__)

class System(WESTSystem):
    def initialize(self):
        self.pcoord_ndim = 2
        self.pcoord_len = 21
        self.pcoord_dtype = numpy.float32
        binbounds1 = [0.5*i for i in range(0,21)] + [i for i in range(11,61)] + [float('inf')]
        binbounds2 = [0.0, 3.0, float('inf')]
        self.bin_mapper = RectilinearBinMapper([binbounds1, binbounds2])
        self.bin_target_counts = numpy.empty((self.bin_mapper.nbins,), numpy.int)
        self.bin_target_counts[...] = 8

def COGloader(fieldname, coord_filename, segment, single_point=False):
    cogs = numpy.load(coord_filename)
    segment.data[fieldname] = cogs

def COMloader(fieldname, coord_filename, segment, single_point=False):
    coms = numpy.load(coord_filename)
    segment.data[fieldname] = coms
