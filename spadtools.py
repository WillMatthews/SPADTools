#!/usr/bin/python3

import numpy as np
import pickle
import csv
from scipy import constants
import matplotlib.pyplot as plt

def get_sensitivity(spad, T, target_BER):
    # input A, FF, PDE(eff) = PDE_max, tdead, tpulse, BER_target, Nspad)
    FF = 1 ## do we even have a filling factor ?????
    A = spad["area"] * 10 ** -6 ## we want this in mm2
    PDE_max = spad["pde"]
    Nspad = spad["numspad"]
    tdead = spad["deadtime"]

    rsb = 1/ (T*spad["bandwidth"])
    old_PDE = None

    PDE = PDE_max
    while True:
        # get Nb from equation 6.1: (BACKGROUND COUNTS..)
        Nb = PDE/FF * T * A * 1.5 * 10**9

        # find number of SPADs that will fire within single symbol duration, bit one:
        Ns0 = get_ns0(target_BER, Nb)

        PP = get_pwr_penalty(rsb)
        Ns = PP * Ns0

        # get PDE_eff:
        x_param = tdead * Ns / (T * Nspad)
        PDE_eff = PDE_max * np.exp(-x_param)

        if old_PDE is not None:
            frac_difference = np.abs(PDE_eff - old_PDE) / PDE_eff
            if frac_difference < 0.01: # changed less than a percent ?
                intensity = get_intensity(Ns0, T, spad)
                break

        if is_saturated(Ns, T, spad):
            return None

        old_PDE = PDE_eff

    return (intensity, (Ns0, Ns))



def get_ns0(BER, background):
    if background < 2:
        ## use poisson limit
        return - np.log(2 * BER)
    else:
        ## use gaussian model
        raise Exception("unimplemented")



def get_intensity(count, T, spad):
    wavelength = 420 * 10**(-9)
    Ep = constants.h * constants.c / wavelength
    alpha = spad["pde"] * spad["area"]/Ep
    Lhat = (1/alpha) * 1/( (spad["numspad"] * T / count) - spad["deadtime"]  ) # L + Ldark
    return Lhat


def pickle_to_csv(fin="./.spadcompare.pickle",fout="./csv_out.csv"):
    with open("fname", "rb") as f:
        spads = pickle.load(f)

    with open("./csv_out.csv", "w") as f:
        titlerow = list(spads[0].keys())
        writer = csv.writer(f)
        writer.writerow(titlerow)
        for spad in spads:
            row_out = []
            for key in spad.keys():
                row_out.append(spad[key])
            writer.writerow(row_out)


def spads_to_csv(spads,fout="./csv_out.csv"):
    with open("./csv_out.csv", "w") as f:
        titlerow = list(spads[0].keys())
        writer = csv.writer(f)
        writer.writerow(titlerow)
        for spad in spads:
            row_out = []
            for key in spad.keys():
                row_out.append(spad[key])
            writer.writerow(row_out)


def is_saturated(Ns, T, spad):
    maxN = spad["max_count"] * T
    if Ns > maxN:
        return True
    else:
        return False


def get_pwr_penalty(rsb,scheme="OOK"):
    if scheme == "OOK":
        a = 0.07691
        b = -0.6276
        c = 0.944
        d = 0.1012
        k = -0.02
        p1 = 0.1658
        p2 = 0.827
    elif scheme == "4PAM":
        raise Exception

    if rsb < 1:
        return 1
    elif rsb < 2 and rsb > 1:
        return (a * np.exp(b * rsb) + c * np.exp(d * rsb) + k)
    elif rsb >= 2:
        return p1*rsb + p2


if __name__ == "__main__":

    rsbs = np.linspace(0, 10, 1000)

    pps = [get_pwr_penalty(r) for r in rsbs]
    plt.plot(rsbs, pps)
    plt.show()


    print("this file is not to be run directly - please import as use that way")
    exit()
