#!/usr/bin/env python
from durationcorrection import DurationCorrection
import h5py
import numpy

tau = 1
concentration = 1

def rateanalysis(lastiter, directh5path, istate, fstate, timepoints_per_iteration):
    dc = DurationCorrection.from_files([directh5path], istate, fstate, lastiter=lastiter)
    correction = dc.correction(lastiter, timepoints_per_iteration)

    with h5py.File(directh5path, 'r') as directh5:
        raw_rate = directh5['rate_evolution'][lastiter-1][istate][fstate]['expected']
    raw_rate = raw_rate/(tau*concentration)
    rate = raw_rate*correction
    return raw_rate, rate

def main():
    # number of iterations in the simulation
    n_iterations = 2000
    # path to the w_direct output files
    directh5path = './direct.h5'
    # number of timepoints per iteration; since the last timepoint of one 
    # iteration overlaps with the first timepoint of the next, we typically
    # have an odd number here (like 11 or 21 or 51).
    timepoints_per_iteration = 3

    # buffer to hold the corrected rate values; 
    raw_rates = numpy.zeros(n_iterations)
    rates = numpy.zeros(n_iterations)
    # loop through all iterations
    for i in range(n_iterations):
        print("iter %d"%(i + 1))
        # calculate corrected rate using data up to iteration iiter
        # and store the result in the buffer
        raw_rates[i], rates[i] = rateanalysis(i + 1, directh5path, 1, 0, timepoints_per_iteration)

    # calculate the mean and sem for both raw and corrected rates
#    raw_rates_mean = numpy.mean(raw_rates, axis=1)
#    raw_rates_sem = numpy.std(raw_rates, axis=1)/numpy.sqrt(n_simulations)
#    rates_mean = numpy.mean(rates, axis=1)
#    rates_sem = numpy.std(rates, axis=1)/numpy.sqrt(n_simulations)

    # save result with numpy
    numpy.save('raw_rates.npy', raw_rates)
    numpy.save('rates.npy', rates)

if __name__ == "__main__":
    main()
