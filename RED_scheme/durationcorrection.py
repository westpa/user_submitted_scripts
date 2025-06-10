#!/usr/bin/env python
import h5py
import numpy

'''
Calculate factor to correct for nonzero durations of barrier crossings. The
event duration distribution is estimated from observed event durations,
accounting for the fact that the probability of observing an event of a given
duration is not proportional to the duration of that event.

After specifying data to the DurationCorrection class via ``from_files``, call
``correction`` to return the correction factor

        __                              __  -1
        |  t=theta  tau=t                |
        |    |\      |\                  |
        |    |       | ~                 |
        |    |       | f(tau) dtau dt    |
        |   \|      \|                   |
        |   t=0    tau=0                 |
        |_                              _|

where
   ~`                        ^
   f(tau) is proportional to f(tau)/(theta-tau), and is normalized to
                    ^
integrate to 1, and f(tau) is sum of the weights of walkers with
duration time tau.
'''

class DurationCorrection(object):
    @staticmethod
    def from_files(kinetics_files, istate, fstate, lastiter=None, **kwargs):
        weights = []
        durations = []
        for path in kinetics_files: 
            with h5py.File(path, 'r') as kinetics_file:
                if lastiter is not None:
                    dataset = kinetics_file['durations'][:lastiter]
                else:
                    dataset = kinetics_file['durations']

            torf = numpy.logical_and(dataset['istate'] == istate, dataset['fstate'] == fstate)
            torf = numpy.logical_and(dataset['weight'] > 0, torf)
            
            w = dataset['weight'][torf]
            d = dataset['duration'][torf]
            d[d<0] = numpy.where(torf)[0][d<0]
            weights.extend(w)
            durations.extend(d)

        return DurationCorrection(durations, weights)

    def __init__(self, durations, weights):
        self.weights = numpy.array(weights)
        self.durations = numpy.array(durations)

    def correction(self, maxduration, timepoints):
        '''
        Return the correction factor
            
        __                              __  -1
        |  t=theta  tau=t                |
        |    |\      |\                  |
        |    |       | ~                 |
        |    |       | f(tau) dtau dt    |      * maxduration
        |   \|      \|                   |
        |   t=0    tau=0                 |
        |_                              _|

        where
           ~`                        ^
           f(tau) is proportional to f(tau)/(theta-tau), and is normalized to
                            ^
        integrate to 1, and f(tau) is sum of the weights of walkers with
        duration time tau.

        ---------
        Arguments
        ---------
        maxduration: the maximum duration time that could have been observed in
            the simulation, which is usually equal to the length of the
            simulation. This should be in units of tau.
        timepoints: The number of timepoints per iteration, including the first
            and last timepoints. For example, a simulation with outputs every
            1 ps and tau=20 ps should have timepoints=21.
        '''
        dtau = 1./(timepoints-1)

        #      ~
        # find f(tau)
        taugrid = numpy.arange(0, maxduration, dtau, dtype=float)
        f_tilde = numpy.zeros(len(taugrid), dtype=float)
        for i, tau in enumerate(taugrid):
            matches = numpy.logical_and(self.durations >= tau, self.durations < tau + dtau)
            f_tilde[i] = self.weights[matches].sum()/(maxduration-tau+1)
        
        if f_tilde.sum() != 0:
            f_tilde /= f_tilde.sum()*dtau

        self.f_tilde = f_tilde

        # now integrate f_tilde twice
        # integral1[t/dtau] gives the integral of f_tilde(tau) dtau from 0 to t
        integral1 = numpy.zeros(f_tilde.shape)
        for i, tau in enumerate(taugrid):
            if i > 0:
                integral1[i] = numpy.trapz(f_tilde[:i+1], taugrid[:i+1])
        self.F_tilde = integral1
        integral2 = numpy.trapz(integral1, taugrid)

        if integral2 == 0:
            return 0.
        return maxduration/integral2
