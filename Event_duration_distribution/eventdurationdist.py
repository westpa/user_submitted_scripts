#!/usr/bin/env python
import h5py
import numpy
import matplotlib
import matplotlib.pyplot as pyplot

def convert_to_step(dataset):
    return numpy.hstack((numpy.array(0.0),
                        numpy.repeat(dataset, 2),
                        numpy.array(0.0)
                        ))

class DurationHistogram(object):
    def __init__(self):
        pass

    def from_list(self, kinetics_path_list, fstate, lastiter=100, **kwargs):
        weights = []
        durations = []
        for path in kinetics_path_list: 
            print('Loading {:s}'.format(path))
            kinetics_file = h5py.File(path, 'r')
            if lastiter is not None:
                where = numpy.where(
                    numpy.logical_and(kinetics_file['durations'][:lastiter]\
                                                   ['weight'] > 0,
                                      kinetics_file['durations'][:lastiter]\
                                                   ['fstate'] == fstate))
                d = kinetics_file['durations'][:lastiter]['duration'] 
                w = kinetics_file['durations'][:lastiter]['weight']
            else:
                where = numpy.where(
                    numpy.logical_and(kinetics_file['durations']\
                                                   ['weight'] > 0,
                                      kinetics_file['durations']\
                                                   ['fstate'] == fstate))
                d = kinetics_file['durations']['duration'] 
                w = kinetics_file['durations']['weight']
            for i in range(where[1].shape[0]):
                weight = w[where[0][i],where[1][i]]
                duration = d[where[0][i],where[1][i]]
                if duration > 0:
                    durations.append(duration)
                else:
                    durations.append(where[0][i])
                weights.append(weight)

        weights = numpy.array(weights)
        durations = numpy.array(durations)
        print(durations.min())

        self.histogram(durations, weights, lastiter=lastiter, **kwargs)
        return

    def integrate(self, hist, edges, lb=None, ub=None):
        if lb is None:
           lb = edges[0]

        if ub is None:
           ub = edges[-1]

        integral = 0.0
       
        setbreak = False
        for i, leftedge in enumerate(edges[:-1]):
            if leftedge >= lb:
                rightedge = edges[i+1] 
                if rightedge > ub:
                    rightedge = ub
                    setbreak = True
                delta = rightedge-leftedge 
                integral += hist[i]*delta
                if setbreak:
                    break

        return integral

    def normalize_density(self):
        integral = self.integrate(self.hist, self.edges)
        print("normalizing event duration distribution by factor: {:f}".format(integral))
        self.hist /= integral
        return 
         
    def histogram(self, durations, weights, binwidth=1, lastiter=None,  
                  correction=True, **kwargs):
        lb = 0
        ub = numpy.ceil(durations.max()) 
        #edges = numpy.arange(lb, ub+binwidth, binwidth, dtype=float)
        edges = numpy.arange(lb, lastiter+binwidth, binwidth, dtype=float)
        print(edges)
        hist, _ = numpy.histogram(durations, weights=weights, bins=edges,
                                  density=True)

        print(correction)
        if correction:
            halfwidth = binwidth/2
            factors = 1/numpy.arange(lastiter-halfwidth, lb-halfwidth, 
                                     -1*binwidth, dtype=float)
            hist = hist*factors#[:hist.shape[0]] 
        print(kwargs)
        self.hist = hist
        self.edges = edges
        self.normalize_density()
         
        return

    def plot_hist(self, outpath='durations.pdf', color='black', 
                  log=False, ax=None):
        matplotlib.rcParams['font.size'] = 20
        linewidth=1.5
        
        if ax is None:
            fig, ax = pyplot.subplots() 
            fig.set_size_inches(9.68,8.2)
        else:
            fig = pyplot.gcf()
        tauinns = .002
        self.edges = self.edges*tauinns
        if log:
            ax.plot(numpy.repeat(self.edges, 2), numpy.log(convert_to_step(self.hist)), 
                    color=color, linewidth=3)
        else:
            ax.plot(numpy.repeat(self.edges, 2), convert_to_step(self.hist), color=color, linewidth=3)
        for kw in ('top', 'right'):
            ax.spines[kw].set_visible(False)
        for kw in ('bottom', 'left'):
            ax.spines[kw].set_linewidth(linewidth)
        ax.xaxis.set_ticks_position('bottom')
        ax.yaxis.set_ticks_position('left')
        ax.tick_params(direction='out', width=linewidth)
        ax.set_xlabel('Event Duration Time (ns)', size=28)
        ax.set_ylabel('Probability', size=28)
        ax.set_yticks([])
        ax.tick_params(labelsize=28)
        pyplot.savefig(outpath)


def main():

    pathlist = ['./direct.h5']
    h = DurationHistogram()
    h.from_list(pathlist, correction=True, fstate=0, lastiter=100, binwidth=10)
    h.plot_hist(color='green')
    

if __name__ == "__main__":
    main()
