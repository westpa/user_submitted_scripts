#!/usr/bin/env python
import h5py
import numpy
'''
Calculate factor to correct for nonzero durations of barrier crossings. The
event duration distribution is estimated from observed event durations,
accounting for the fact that the probability of observing an event of a given
duration is not proportional to the duration of that event.

After specifying data to the DurationCorrection class via ``from_list``, call
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
    def __init__(self):
        pass

    def from_list(self, kinetics_path_list, fstate, lastiter=2000, **kwargs):
        weights = []
        durations = []
        for path in kinetics_path_list: 
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
