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

PI = numpy.pi
from numpy import *
pcoord_dtype = numpy.float32

# WARNING:
# These are the things you should change.
# For recursive binning with MAB (putting MAB within another rectilinear bin), make sure to
# specify the binning in SDASystem at the bottom of this document. `multi_idx` specifies 
# which parameter it should read. Each adaptive binning scheme should get their own multi_idx.

bintargetcount=12 #number of walkers per bin
numberofdim=1  # number of dimensions. If using recursive, this should be for the inner adaptive bins.
binsperdim=[15]   # You will have prod(binsperdim)+numberofdim*(2+2*splitIsolated)+activetarget bins total for that mab
pcoordlength=51 # length of the pcoord
maxcap=[[numpy.inf,8],[numpy.inf,numpy.inf]]    #MAB doesn't respect the outter mapper boundaries so make sure you set the caps of each one in sync with the outer rectilinear bin you want contained
mincap=[[3.5,0],[0,8]]  #They are nested because you could have multiple MAB schemes nested in different bins. The each min/max cap entry should be in sync with multi_idx. For each entry, left is the first dimension, right is the second, etc.

targetstate=[3.5, 8]    #enter boundaries for target state or None if there is no target state in that dimension
targetstatedirection=[-1, -1]  #if your target state is meant to be greater that the starting pcoor use 1 or else use -1. This will be done for each dimension in your simulation
activetarget=1      #if no target state make this zero
splitIsolated=1     #choose 1 if you want to split the most isolated walker (this will add an extra bin)

#########
def function_map(coords, mask, output, multi_idx=0, **kwargs):
    splittingrelevant=True
    varcoords=copy(coords)
    originalcoords=copy(coords)
    multi_idx = int(multi_idx)
    maxlist=[]
    minlist=[]
    difflist=[]
    flipdifflist=[]
    orderedcoords=copy(originalcoords)
    for n in range(numberofdim):
        try:
            extrema_file=load('binbounds.npz')
            extremabounds=extrema_file(extrema_file.files[multi_idx])
            currentmax=amax(extremabounds[:,n])
            currentmin=amin(extremabounds[:,n])
        except:
            currentmax=amax(coords[:,n])
            currentmin=amin(coords[:,n])
        if maxcap[multi_idx][n]<currentmax:
            currentmax=maxcap[multi_idx][n]
        if mincap[multi_idx][n]>currentmin:
            currentmin=mincap[multi_idx][n]
        maxlist.append(currentmax)
        minlist.append(currentmin)
        try:    
            temp=column_stack((orderedcoords[:,n],originalcoords[:,numberofdim]))
            temp=temp[temp[:,0].argsort()]
            for p in range(len(temp)):
                if temp[p][1]==0:
                    temp[p][1]=10**-39
            fliptemp=flipud(temp)
            difflist.append(0)
            flipdifflist.append(0)  
            maxdiff=0
            flipmaxdiff=0
            for i in range(1,len(temp)-1):
                comprob=0
                flipcomprob=0
                j=i+1
                while j<len(temp):
                    comprob=comprob+temp[j][1]
                    flipcomprob=flipcomprob+fliptemp[j][1]
                    j=j+1
                if temp[i][0]<maxcap[multi_idx][n] and temp[i][0]>mincap[multi_idx][n]:
                    if (-log(comprob)+log(temp[i][1]))>maxdiff:
                        difflist[n]=temp[i][0]
                        maxdiff=-log(comprob)+log(temp[i][1])
                if fliptemp[i][0]<maxcap[multi_idx][n] and fliptemp[i][0]>mincap[multi_idx][n]:
                    if (-log(flipcomprob)+log(fliptemp[i][1]))>flipmaxdiff:
                        flipdifflist[n]=fliptemp[i][0]
                        flipmaxdiff=-log(flipcomprob)+log(fliptemp[i][1])
        except:
            splittingrelevant=False
    for i in range(len(output)):
        holder=2*numberofdim
        for n in range(numberofdim):
            if (activetarget==1) and targetstate[n] is not None:
                if (originalcoords[i,n]*targetstatedirection[n]) >= (targetstate[n]*targetstatedirection[n]):
                    holder=prod(binsperdim)+numberofdim*2
            if (holder==prod(binsperdim)+numberofdim*2):
                n=numberofdim
            elif coords[i,n]>=maxlist[n] or originalcoords[i,n]>=maxcap[multi_idx][n]:
                holder= 2*n
                n=numberofdim
            elif coords[i,n]<=minlist[n] or originalcoords[i,n]<=mincap[multi_idx][n]:
                holder =2*n+1
                n=numberofdim
            elif splittingrelevant and coords[i,n]==difflist[n] and splitIsolated==1:
                holder=prod(binsperdim)+numberofdim*2+2*n+activetarget
                n=numberofdim
            elif splittingrelevant and coords[i,n]==flipdifflist[n] and splitIsolated==1:
                holder=prod(binsperdim)+numberofdim*2+2*n+activetarget+1
                n=numberofdim
        if holder==2*numberofdim:
            for j in range(numberofdim):
                holder = holder + (digitize(coords[i][j],linspace(minlist[j],maxlist[j],binsperdim[j]+1))-1)*prod(binsperdim[0:j])
        output[i]=holder
    return output

class SDASystem(WESTSystem):
    '''
    Class specify binning schemes, walker counts, and other core weighted
    ensemble parameters.
    '''
    def initialize(self):

	#   pcoord dimensionality and length. This should match your outside bin
        self.pcoord_ndim            = 2
        self.pcoord_len             = pcoordlength
        self.pcoord_dtype           = pcoord_dtype
        
        #   These are your "outer" bins in both dimensions
        outer_mapper = RectilinearBinMapper(
            [[0.00, numpy.inf],
             [0.00, 8.00, numpy.inf]]
                                       )        
        #   These define the "inner" adaptive bins. Each one indicates an independent
        #   adaptive binning scheme. Copy for more. Respects the parameters at the start.
        adaptive_mapper0 = FuncBinMapper(function_map, prod(binsperdim)+numberofdim*(2+2*splitIsolated)+activetarget, kwargs={"multi_idx": 0}) # Bottom bin
        adaptive_mapper1 = FuncBinMapper(function_map, prod(binsperdim)+numberofdim*(2+2*splitIsolated)+activetarget, kwargs={"multi_idx": 1}) # Top bin

        #   These are the bins where you'll place each adaptive scheme.
        self.bin_mapper = RecursiveBinMapper(outer_mapper)
        self.bin_mapper.add_mapper(adaptive_mapper0, [5,1]) #Bottom mapper
        self.bin_mapper.add_mapper(adaptive_mapper1, [5,10]) #Top mapper

        ######################### JL ##########################################
        #    This is the what the example looks like.   
        #
        #   inf --------------------------------------------------------
        #      |                                                        |
        #      |                    adaptive_mapper1                    |
        #      |                                                        |
        #     8 --------------------------------------------------------
        #  D2  |        |                                               |
        #      | TARGET |           adaptive_mapper0                    |
        #      | STATE  |                                               |
        #     0 --------------------------------------------------------
        #              3.5 (soft bound via mincap)                     inf
        #                        Dimension 1 of pcoord
        #
        #######################################################################
    
        self.bin_target_counts = numpy.empty((self.bin_mapper.nbins,), 
                                             dtype=numpy.int)
    
        #   Number of walkers per bin
        self.bin_target_counts[...] = bintargetcount
