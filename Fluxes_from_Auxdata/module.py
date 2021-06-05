#!/usr/bin/env python

import numpy

def load_distances(n_iter, iter_group):
    auxgroup1 = iter_group['auxdata/dataset']
    auxgroup2 = iter_group['auxdata/dataset']
    dataset = numpy.dstack((auxgroup1, auxgroup2))
    return dataset
