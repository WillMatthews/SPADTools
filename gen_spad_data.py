#!/usr/bin/python3
"""Generates the CSV of SPAD parameters"""

from scipy import constants
import matplotlib.pyplot as plt
import numpy as np
import spadtools


names     = ["J(TSV)*","J**", "J", "J*", "C*", "C", "C", "C", "C", "C", "C", "C"]
costs     = [57.2, 19.30, -1, -1, 43.38, -1, -1, -1, -1, -1, -1] # gbp
areas     = [9, 9, 16, 36, 1, 1, 1, 13, 3, 3, 6] # mm^2
pitches   = [20, 35, 35, 35, 10, 20, 35, 20, 35, 50, 35]
numspads  = [14410, 5676, 9260, 22292, 2880, 1296, 504, 10998, 4774, 2668, 18980] # integer
deadtimes = [15, 45, 48, 50, 5, 23, 82, 23, 82, 159, 95] # nano
op_widths = [1.4, 1.5, 1.7, 3, 0.6, 0.6, 0.6, 1.5, 1.5, 1.5, 3.2] #nano
pdes      = [38, 50, 50, 50, 18, 31, 41, 31, 41, 47, 41] # pct
peakwls   = [420, 420, 420, 420, 420, 420, 420, 420, 420, 420, 420] #nano

spads = []
itervar = 1
for name, cost, area, pitch, numspad, deadtime, op_width, pde, peakwavelength in zip(names, costs, areas, pitches, numspads, deadtimes, op_widths, pdes, peakwls):
    spad = {}
    spad["name"] = str(itervar) + ": " + name
    spad["cost"] = cost
    spad["area"] = area * 10**(-6) # m^2
    spad["pitch"]  = pitch
    spad["numspad"] = numspad
    spad["deadtime"] = deadtime * 10**(-9)
    spad["pulsetime"] = op_width * 10**(-9)
    spad["pde"] = pde
    spad["peakwavelength"] = peakwavelength * 10**(-9)
    Ep = constants.h * constants.c / spad["peakwavelength"]
    spad["photon_energy"] = Ep
    spads.append(spad)
    itervar += 1

spadtools.spads_to_csv(spads, fout="./parameters.csv")


plt.figure()
Ldark = 0 # assume perfect zero dark count
xmax = 10**-5
L = np.linspace(0, xmax, 10000)
for i, spad in enumerate(spads):
    ## 3.13 long thesis
    num    = spad["numspad"]
    alpha  = spad["pde"] * spad["area"]/Ep
    T      = 1  # observation time... (1 sec)?
    tau    = spad["deadtime"]
    counts = num * alpha * T * (L + Ldark) / (1 + alpha * tau * (L+Ldark))
    asymptote_counts = T * num / tau
    spad["max_count"] = asymptote_counts
    spad["L"] = L
    spad["Ldark"] = Ldark
    spad["counts"] = counts
    col=plt.cm.nipy_spectral((i+1)/len(spads))
    plt.plot(L, counts, c=col, label=spad["name"])
    plt.hlines(asymptote_counts, 0, xmax, color=col, linestyle="--")
plt.grid()
plt.title("Count rate vs intensity of incident light on SiPMs")
plt.legend()
plt.show()

