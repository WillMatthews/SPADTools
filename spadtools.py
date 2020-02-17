#!/usr/bin/python3

import numpy as np
import pickle
import csv
from scipy import constants
import matplotlib.pyplot as plt



def get_rate_vs_photons(spad, photon_range, search_space, target_ber=10**-3):

    spad["intensity"] = {}
    for ppb in photon_range:
        spad["intensity"][ppb] = {}
        get_max_counts(spad)
        p = 0.5 # ???? This is "pulse falling percentage" see Long's thesis 109
        get_bandwidth(spad, p)

        print("\nSPAD", spad["name"],"\n==================")

        print('{0:.2f}'.format(((spad["max_count"] / ppb))*10**-9), "Gbps... NO ISI UPPER BOUND")
        spad["intensity"][ppb]["hack_data_rate"] = (spad["max_count"] / ppb)*10**-9
        spad["intensity"][ppb]["sensitivity"] = None
        for numgig in search_space:
            symbol_time = 1 / (numgig * 10**9) # 10Gbps
            old_sensitivity = spad["intensity"][ppb]["sensitivity"]
            spad["intensity"][ppb]["sensitivity"] = get_sensitivity(spad, symbol_time, target_ber, custom=True, customcount=ppb)
            if spad["intensity"][ppb]["sensitivity"] is None:
                if old_sensitivity is not None:
                    print('{0:.2f}'.format(numgig), "Gbps...", "{0:.2f}".format(old_sensitivity[1][1]),"photons per bit one")
                    spad["intensity"][ppb]["max_data_rate"] = numgig
                    spad["intensity"][ppb]["sensitivity"] = old_sensitivity
                else:
                    print("Data Rate <", min(search_space),"Gbps")
                break
        else:
            break


def get_max_data_rate(spad, search_space, target_ber=10**-3):

    get_max_counts(spad)
    p = 0.5 # ???? This is "pulse falling percentage" see Long's thesis 109
    get_bandwidth(spad, p)

    print("\nSPAD", spad["name"],"\n==================")

    print('{0:.2f}'.format((spad["max_count"] / get_ns0(target_ber, 0))*10**-9), "Gbps... NO ISI UPPER BOUND")
    spad["hack_data_rate"] = (spad["max_count"] / get_ns0(target_ber, 0))*10**-9
    spad["sensitivity"] = None
    for numgig in search_space:
        symbol_time = 1 / (numgig * 10**9) # 10Gbps
        old_sensitivity = spad["sensitivity"]
        spad["sensitivity"] = get_sensitivity(spad, symbol_time, target_ber)
        if spad["sensitivity"] is None:
            if old_sensitivity is not None:
                print('{0:.2f}'.format(numgig), "Gbps...", "{0:.2f}".format(old_sensitivity[1][1]),"photons per bit one")
                spad["max_data_rate"] = numgig
                spad["sensitivity"] = old_sensitivity
            else:
                print("Data Rate <", min(search_space),"Gbps")
            break
    else:
        print("Data Rate >", max(search_space),"Gbps")


def get_sensitivity(spad, T, target_BER, scheme="OOK", custom=False, customcount=0):
    # input A, FF, PDE(eff) = PDE_max, tdead, tpulse, BER_target, Nspad)
    FF = 0.8  ## do we even have a filling factor ?????
    A = spad["area"] #* 10 **-6 ## we want this in mm2
    PDE_max = spad["pde"]
    Nspad = spad["numspad"]
    tdead = spad["deadtime"]
    rsb = 1 / (T*spad["bandwidth"])
    #print(spad)

    # Initialise Variables
    old_PDE = None
    PDE_eff = PDE_max
    itervar = 0
    satcount= 1
    while True:
        itervar += 1

        Nb = get_background(PDE_eff, FF, T, A)

        # find number of SPADs that will fire within single symbol duration, bit one:
        Ns0 = get_ns0(target_BER, Nb, custom=custom, customcount=customcount)

        PP = get_pwr_penalty(rsb, scheme=scheme)
        Ns = PP * Ns0

        # get PDE_eff:
        x_param = tdead * Ns / (T * Nspad)
        PDE_eff = PDE_max * np.exp(-x_param)

        if old_PDE is not None:
            frac_difference = np.abs(PDE_eff - old_PDE) / PDE_eff
            if frac_difference < 10**-10: # changed less than a percent ?
                intensity = counts_to_intensity(Ns, T, spad)
                #print(Ns, T, intensity)
                break

        if is_saturated(Ns, Nb, T, spad):
            satcount += 1
            #print(itervar, "IS SATURATED, NOT BREAKING")
            if satcount > 50:
                return None
            return None

        old_PDE = PDE_eff

    return (intensity, (Ns0, Ns))


def get_background(PDE_eff, FF, T, A):
    # get Nb from equation 6.1: (BACKGROUND COUNTS FOR A SPAD IN SYMBOL PERIOD T)
    Nb = (PDE_eff/FF) * T * A * 1.5 * 10**9
    return Nb


def get_ns0(BER, background, custom=False, customcount=0): #TODO Add Gaussian and Poisson models.
    if background > 0.01:
        print("Background count high!! Exercise caution with result")
    return - np.log(2 * BER)

    if not custom:
        if background < 0.01:
            ## use poisson limit
            return - np.log(2 * BER)
        elif background < 2:
            ## use poisson model
            raise Exception("Unimplemented!")
        else:
            ## use gaussian model
            raise Exception("Unimplemented!")
    else:
        return customcount




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
    with open(fout, "w") as f:
        titlerow = list(spads[0].keys())
        writer = csv.writer(f)
        writer.writerow(titlerow)
        for spad in spads:
            row_out = []
            for key in spad.keys():
                row_out.append(spad[key])
            writer.writerow(row_out)


def csv_to_spads(fin="./parameters.csv"):
    spads = []
    with open(fin, "r") as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i is not 0:
                try:
                    spad = {}
                    spad["name"] = row[0]
                    spad["cost"] = row[1]
                    spad["area"] = float(row[2])
                    spad["pitch"]  = float(row[3])
                    spad["numspad"] = int(row[4])
                    spad["deadtime"] = float(row[5])
                    spad["pulsetime"] = float(row[6])
                    spad["pde"] = float(row[7])
                    spad["peakwavelength"] = float(row[8])
                    spad["photon_energy"] = float(row[9])
                    spads.append(spad)
                except IndexError:
                    print("csv_to_spads encountered IndexError")
    return spads


def is_saturated(Ns, Nb,  T, spad):
    maxN = spad["max_count"] * T
    if (Ns + Nb) > maxN:
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
        a = 0.088
        b = -1.383
        c = 0.9122
        d = 0.1086
        k = -0.01
        p1 = 0.1902
        p2 = 0.7765

    if rsb < 0:
        return 1
    elif rsb < 2:
        return (a * np.exp(b * rsb) + c * np.exp(d * rsb) + k)
    elif rsb >= 2:
        return p1*rsb + p2


def get_bandwidth(spad, p):
    spad["bandwidth"] = -np.log(1-p) / (2 * np.pi * spad["pulsetime"])


def get_max_counts(spad):
    #3.13 long thesis
    num = spad["numspad"]
    alpha = spad["pde"] * spad["area"]/spad["photon_energy"]
    T     = 1  # observation time... (1 sec)?
    tau   = spad["deadtime"]
    asymptote_counts = T * num / tau
    spad["max_count"] = asymptote_counts


def intensity_to_counts(spad, L, Ldark):
    #3.13 long thesis
    num = spad["numspad"]
    Ep = spad["photon_energy"]
    alpha = spad["pde"] * spad["area"]/(Ep*num)
    T     = 1  # observation time... (1 sec)?
    tau   = spad["deadtime"]
    counts = num * alpha * T * (L + Ldark) / (1 + alpha * tau * (L+Ldark))
    asymptote_counts = T * num / tau
    spad["max_count"] = asymptote_counts
    return counts


def counts_to_intensity(count, T, spad):

    dtmult = spad["numspad"]
    Ep = spad["photon_energy"]
    alpha = spad["pde"] * spad["area"]/(Ep*spad["numspad"])
    Lhat = (1/alpha) * 1/((spad["numspad"] * T / count) - spad["deadtime"]) # L + Ldark
    #print("INTENSITY:", "dead",spad["deadtime"], "num",spad["numspad"])
    #print("PDE",spad["pde"], "Ep",spad["photon_energy"],"A",spad["area"])
    #print(ocount, Lhat, T, Lhat*spad["area"] * oT/Ep)
    #print("Est Pwr Long:", Lhat)
    #print("Est Pwr me:", (1/spad["area"]) * spad["photon_energy"]*count*(1/T))
    return Lhat #  in watts per metre squared


def get_safe_area(illum_area, flux_rx):
    #illum_area metres squared transmit area
    #flux_rx in watts per metre squared
    tx_power = illum_area * flux_rx
    print("TX Power:", tx_power, "W")

    max_flux = 30/30000 # 30/t for MPE (WATTS PER METRE SQUARED)
    print("Max Allowed Power at a Pupil below MPE is:", max_flux, "Wm^-2")
    pupil_area = np.pi * ((0.5*10**-3)**2)/5 # piD^2/4

    tx_area = tx_power / max_flux
    print("TX Area:", tx_area * 10**6, "cm^2")
    return tx_area


if __name__ == "__main__":

    rsbs = np.linspace(0, 10, 1000)

    pps = [get_pwr_penalty(r) for r in rsbs]
    plt.plot(rsbs, pps)
    plt.show()

    print("this file is not to be run directly - please import as use that way")
    exit()
