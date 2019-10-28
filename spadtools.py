#!/usr/bin/python3

import numpy as np
import pickle
import csv


def get_sensitivity(spad, T):
    # input A, FF, PDE(eff) = PDE_max, tdead, tpulse, BER_target, Nspad)
    FF = 1 ## do we even have a filling factor ?????
    A = spad["area"] * 10 ** -6 ## we want this in mm2
    PDE = spad["pde"]
    Nspad = spad["numspad"]
    tdead = spad["deadtime"]


    old_PDE = None

    while True:
        pass
        # get Nb from equation 6.1:
        Nb = PDE/FF * T * A * 1.5 * 10**9

        # find number of SPADs that will fire within single symbol duration, bit one:
        PP = get_pwr_penalty(rsb)
        Ns = PP * Ns0

        # get PDE_eff:
        x_param = tdead * Ns / (T * Nspad)
        PDE_eff = PDE_max * np.exp(-x_param)

        if old_PDE is not None:
            difference = np.abs(PDE_eff - old_PDE) / PDE_eff
            if difference < 0.01: # changed less than a percent ?
                get_intensity(Ns, PP, spad)

        if is_saturated(Ns, T, spad):
            return None

        old_PDE = PDE_eff



def to_csv(fin="./.spadcompare.pickle",fout="./csv_out.csv"):
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
    elif rsb < 2:
        return a * np.exp(b * rsb) + b * np.exp(d * rsb) + k
    elif rsb >= 2:
        return p1*rsb + p2




if __name__ == "__main__":
    print("this file is not to be run directly - please import as use that way")
    exit()
