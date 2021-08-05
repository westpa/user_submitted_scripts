from __future__ import print_function, division

import numpy

from west.propagators import WESTPropagator

from west.systems import WESTSystem

from westpa.binning import RectilinearBinMapper

from westpa.binning import FuncBinMapper

from westpa.binning import RecursiveBinMapper

import logging

log = logging.getLogger('westpa.rc')

PI = numpy.pi

from numpy import *

pcoord_dtype = numpy.float32

import scipy

from scipy import sparse

bintargetcount = 4  # number of walkers per bin

numberofdim = 3  # number of dimensions

binsperdim = 5  # You will have prod(binsperdim)+numberofdim*(2+2*splitIsolated)+activetarget bins total

pcoordlength = 101  # length of the pcoord

maxcap = [inf, inf,
          inf]  # for each dimension enter the maximum number at which binning can occur, if you do not wish to have a cap use inf

mincap = [
    -inf, 3,
    -inf]  # for each dimension enter the minimum number at which binning can occur, if you do not wish to have a cap use -inf

targetstate = [
    [12.6, 10, 8]]  # enter boundaries for target state or None if there is no target state in that dimension

targetstatedirection = [[
    1, 1,
    1]]  # if your target state is meant to be greater that the starting pcoor use 1 or else use -1. This will be done for each dimension in your simulation

activetarget = 1  # if there is no target state make this zero

splitIsolated = 1  # choose 0 to disable the use of bottleneck walkers (not recomended)

targeted = [2.6, 10, 7]


#########

def normalize(coords):
    coords = coords.astype(float)

    coords = numpy.append(coords, targetstate, axis=0)

    for n in range(numberofdim):

        dinmax = amax(coords[:-1, n])

        dinmin = amin(coords[:-1, n])

        if (dinmax - dinmin) == 0:
            return coords
        for i in range(len(coords[:, n])):
            coords[i, n] = (coords[i, n] - dinmin) / (dinmax - dinmin)

    return coords


def path_calc(adj, index, pred, current):
    if pred[index] == -9999:
        return current
    else:
        current = current+adj[index , pred[index]]
        return path_calc(adj,pred[index],pred,current)


def treeTranslate(coords):
    alternatecoords = copy(coords)

    adjacency = zeros([len(alternatecoords[:, 0]), len(alternatecoords[:, 0])])

    stand = zeros([len(alternatecoords[:, 0]), len(alternatecoords[:, 0])])

    for i in range(len(alternatecoords[:, 0])):

        for j in range(1, len(alternatecoords[:, 0])):

            norm = 0

            dist = 0

            for k in range(numberofdim):
                norm = norm + (alternatecoords[i, k] - alternatecoords[j, k]) ** 2
                dist = dist + (alternatecoords[i, k] - alternatecoords[j, k]) **2

            adjacency[i, j] = norm

            adjacency[j, i] = norm

            stand[i, j] = sqrt(dist)

            stand[j, i] = sqrt(dist)

    dist_matrix, predecessors = scipy.sparse.csgraph.dijkstra(adjacency, indices=len(adjacency) - 1, return_predecessors=True)

    for i in range(len(dist_matrix)-1):
        dist_matrix[i]=path_calc(stand,i,predecessors,0)
    return dist_matrix[:len(adjacency) - 1]


def marking(coords, output):
    marks = zeros_like(output)

    for i in range(len(marks)):  # this section deals with proper assignment of walkers to bins

        binnumber = 0  # essentially the bin number

        intarget = False

        for k in range(len(targetstate)):

            for l in range(len(targetstate[k])):

                if (activetarget == 1) and targetstate[k][l] is not None:

                    if (coords[i, l] * targetstatedirection[k][l]) >= (
                            targetstate[k][l] * targetstatedirection[k][
                        l]):  # if the target state has been reached assign to following bin

                        intarget = True

                    else:

                        break

                        intarget = False

            if intarget:
                binnumber = 2 * numberofdim + 5

                break

        for n in range(numberofdim):

            if (
                    binnumber == 2 * numberofdim + 5):  # this ends the loop if binned in target state, n= numberofdim should not go in above line because of elif statements

                break

            elif coords[i, n] >= maxcap[
                n]:  # assign maxima or those over max cap to own bin

                binnumber = 2 * n + 1

                break

            elif coords[i, n] <= mincap[
                n]:  # assign minima or those under minima to own bin

                binnumber = 2 * n + 2

                break
        marks[i] = binnumber
    return marks


def function_map(coords, output):
    splittingrelevant = True  # This is to make sure splitting is relevant (not relevant for binner after recycling for example)

    originalcoords = copy(coords)  # It is a good idea to keep an original array

    marked = marking(coords, output)

    coords = treeTranslate(normalize(coords[:, :numberofdim]))

    maximum = amax(coords[:])

    minimum = amin(coords[:])

    if shape(originalcoords)[1] > numberofdim:

        temp = column_stack((coords, originalcoords[:, -1]))

        temp = column_stack((temp, marked))

        temp = temp[temp[:, 0].argsort()]  # Sort this by progress coordinate

        for p in range(
                len(temp)):  # This just deals with the fact that currently received probailities are in float32 (it is probably best to disregard probailities smaller than E-39 anyway for tagging

            if temp[p][1] == 0:
                temp[p][1] = 10 ** -39

        fliptemp = flipud(temp)  # Recived sorted array in opposite direction

        difflist = 0  # Provide starting minimum of 0 (in very unlikely case of pcoord 0 and no tagged this could cause arbitrary tag (very minor impact), work to fix)

        flipdifflist = 0

        maxdiff = 0

        flipmaxdiff = 0

        for i in range(1,
                       len(temp) - 1):  # calculating of the "bottleneck" values, we need to sum all of the probability past a potential "bottleneck"

            comprob = 0

            flipcomprob = 0

            j = i + 1

            while j < len(temp):  # calculating the cumulative probability past the each walker in each direction

                comprob = comprob + temp[j][1]

                flipcomprob = flipcomprob + fliptemp[j][1]

                j = j + 1

            if temp[i][2] == 0:

                if (-log(comprob) + log(temp[i][
                                            1])) > maxdiff:  # we want to find the point where the difference between the walker and the cumulative probability past it is at a maximum, we use logarithms to compare differences

                    difflist = temp[i][0]

                    maxdiff = -log(comprob) + log(temp[i][1])

            if fliptemp[i][2] == 0:

                if (-log(flipcomprob) + log(fliptemp[i][1])) > flipmaxdiff:
                    flipdifflist = fliptemp[i][0]

                    flipmaxdiff = -log(flipcomprob) + log(fliptemp[i][1])

    else:

        splittingrelevant = False  # if an error is thrown tagging of bottleneck walkers is not needed

    for i in range(len(output)):  # this section deals with proper assignment of walkers to bins

        binnumber = marked[i] - 1  # essentially the bin number

        if binnumber == -1:  # calculate  binning for evenly spaced bins

            if splittingrelevant and difflist == coords[i]:

                binnumber = 2 * numberofdim

            elif splittingrelevant and flipdifflist == coords[i]:

                binnumber = 2 * numberofdim + 1

            elif maximum == coords[i]:

                binnumber = 2 * numberofdim + 2

            elif minimum == coords[i]:

                binnumber = 2 * numberofdim + 3

            else:

                binnumber = digitize(coords[i],
                                     linspace(minimum, maximum, binsperdim + 1)) + 2 * numberofdim + binnumber + 4

        output[i] = binnumber

    return output

class System(WESTSystem): #class initialization

	def initialize(self):

		self.pcoord_ndim = numberofdim

		self.pcoord_len = pcoordlength

		self.pcoord_dtype = numpy.float32 

		self.bin_mapper = FuncBinMapper(function_map, binsperdim+6+2*numberofdim+binnumber) #Changed binsperbin to binsperdim
 
		self.bin_target_counts = numpy.empty((self.bin_mapper.nbins,), numpy.int_)

		self.bin_target_counts[...] = bintargetcount
