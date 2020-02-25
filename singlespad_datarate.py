#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import spadtools
from scipy import constants
from lasersafety import get_mpe

PLOT_RELATIVE = (False, 1)
TARGET_BER = 10**-3
SEARCH_SPACE = np.array([600,800,1000,1200,1400,1600,1800,2000,2200,2400]) * 1/1000

print("\n"*8, "{0:.2f}".format(spadtools.get_ns0(TARGET_BER, 0)), "photons typically required at Poisson Limit")


def process_spad(spads, numgig):
    for i, spad in enumerate(spads):

        spadtools.get_max_counts(spad)
        p = 0.5 # ???? This is "pulse falling percentage" see Long's thesis 109
        spadtools.get_bandwidth(spad, p)

        print("\nSPAD", spad["name"],"\n==================")

        print('{0:.2f}'.format((spad["max_count"] / spadtools.get_ns0(TARGET_BER, 0))*10**-9), "Gbps... NO ISI UPPER BOUND")
        spad["hack_data_rate"] = (spad["max_count"] / spadtools.get_ns0(TARGET_BER, 0))*10**-9
        spad["sensitivity"] = None
        if not spad["hack_data_rate"] < numgig:
            symbol_time = 1 / (numgig * 10**9) # 10Gbps
            spad["sensitivity"] = spadtools.get_sensitivity(spad, symbol_time, TARGET_BER)
            print(spad["sensitivity"])
            print('{0:.2f}'.format(numgig), "Gbps...", "{0:.2f}".format(spad["sensitivity"][1][1]),"photons per bit one")
            spad["max_data_rate"] = numgig
        else:
            print("Not Possible")


def intensity2ppb(spads):
    for spad in spads:
        if spad["sensitivity"] is None:
            continue
        area = spad["area"]
        symbol_time = 1/(spad["max_data_rate"]*10**9)

        photons_per_bit = spad["sensitivity"][1][1]
        photon_energy = spad["photon_energy"]
        watts_per_metresq = spad["sensitivity"][0]
        symbol_energy_m2 = watts_per_metresq * area
        photons_per_metresq = symbol_time * symbol_energy_m2/photon_energy


        #print(area * symbol_time * spadtools.get_intensity(spad["sensitivity"][1][1], symbol_time, spad)/photon_energy)
        print(photon_energy)
        #print(spad["name"], "\t", watts_per_metresq*1E9*(1E-4) , "nW/cm2\t", photons_per_metresq, "photons per msq per symbol time")
        print(spad["name"], "\t", "{:.4e}".format(watts_per_metresq*1E9*(1E-4)) , "nW/cm2\t", photons_per_metresq, "photons landing on spad per symbol time")
        print(spad["name"], "\t", "{:.4e}".format(watts_per_metresq), "Wm^-2")
        print(spad["sensitivity"])
        #print("SymE = ", symbol_energy_m2)


def main():
    wavelength = 405E-9
    spads = spadtools.csv_to_spads(fin="./parameters.csv")

    for spad in spads:
        spad["photon_energy"] = constants.h * constants.c / wavelength

    cleanspads = []
    for spad in spads:
        if "30035" in spad["name"]:
            cleanspads.append(spad)

    spads = cleanspads

    drs = []
    det_phs = []
    ins = []
    for dr in SEARCH_SPACE:
        process_spad(spads, dr)
        intensity2ppb(spads)
        drs.append(dr)
        det_phs.append(spads[0]["sensitivity"][1][1])
        ins.append(spads[0]["sensitivity"][0])


    print("\n"*8)
    print(drs)
    print(det_phs)
    print(ins)
    input("Press any Key to Continue...")


if __name__ == "__main__":
    main()
