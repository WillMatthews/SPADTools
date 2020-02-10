#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import spadtools
from scipy import constants
from lasersafety import get_mpe

PLOT_RELATIVE = (False, 1)
TARGET_BER = 10**-3
SEARCH_SPACE = np.linspace(0.1, 500, 100000)

print("\n"*8, "{0:.2f}".format(spadtools.get_ns0(TARGET_BER, 0)), "photons typically required at Poisson Limit")


def process_spads(spads):
    for i, spad in enumerate(spads):

        spadtools.get_max_counts(spad)
        p = 0.5 # ???? This is "pulse falling percentage" see Long's thesis 109
        spadtools.get_bandwidth(spad, p)

        print("\nSPAD", spad["name"],"\n==================")

        print('{0:.2f}'.format((spad["max_count"] / spadtools.get_ns0(TARGET_BER, 0))*10**-9), "Gbps... NO ISI UPPER BOUND")
        spad["hack_data_rate"] = (spad["max_count"] / spadtools.get_ns0(TARGET_BER, 0))*10**-9
        spad["sensitivity"] = None
        for numgig in SEARCH_SPACE:
            symbol_time = 1 / (numgig * 10**9) # 10Gbps
            old_sensitivity = spad["sensitivity"]
            spad["sensitivity"] = spadtools.get_sensitivity(spad, symbol_time, TARGET_BER)
            if spad["sensitivity"] is None:
                if old_sensitivity is not None:
                    print('{0:.2f}'.format(numgig), "Gbps...", "{0:.2f}".format(old_sensitivity[1][1]),"photons per bit one")
                    spad["max_data_rate"] = numgig
                    spad["sensitivity"] = old_sensitivity
                else:
                    print("Data Rate <", min(SEARCH_SPACE),"Gbps")
                break
        else:
            print("Data Rate >", max(SEARCH_SPACE),"Gbps")


def plot_performance(spads):
    hackrates, realrates = [], []
    names = []
    photons, intensity = [], []

    spad = spads[PLOT_RELATIVE[1]-1]
    initial = (spad["sensitivity"][0], spad["sensitivity"][1][1], spad["hack_data_rate"], spad["max_data_rate"])

    for i, spad in enumerate(spads):
        names.append(spad["name"])
        if PLOT_RELATIVE[0]:
            if i == PLOT_RELATIVE[1] - 1:
                intensity.append(1)
                hackrates.append(1)
                realrates.append(1)
                photons.append(1)
            else:
                hackrates.append(spad["hack_data_rate"] / initial[2])
                realrates.append(spad["max_data_rate"] / initial[3])
                photons.append(spad["sensitivity"][1][1] / initial[1])
                intensity.append(spad["sensitivity"][0] / initial[0])
        else:
            hackrates.append(spad["hack_data_rate"])
            realrates.append(spad["max_data_rate"])
            photons.append(spad["sensitivity"][1][1])

            intensity.append(spad["sensitivity"][0])

    x = np.array([x for x in range(len(hackrates))])
    ax = plt.subplot(111)
    ax.bar(x-0.2, hackrates, width=0.4, color='b', align='center', label="No ISI")
    ax.bar(x+0.2, realrates, width=0.4, color='g', align='center', label="With ISI PP")
    plt.xticks(x, names)
    plt.xlabel("Device")
    if PLOT_RELATIVE[0]:
        plt.ylabel("Data Rate relative to SPAD " + str(PLOT_RELATIVE[1]))
    else:
        plt.ylabel("Data Rate (Gbps)")
    plt.title("SiPM Predicted Data Rates")
    plt.grid()
    plt.legend()

    plt.figure()
    plt.bar(x, photons, width=0.4, color="r", align="center",)
    plt.xlabel("Device")
    if PLOT_RELATIVE[0]:
        plt.ylabel("Photons per Bit relative to SPAD " + str(PLOT_RELATIVE[1]))
    else:
        plt.ylabel("Photons per Bit (ONE)")
    plt.title("SiPM Predicted Photons per Bit")
    plt.grid()
    plt.xticks(x, names)

    plt.figure()
    plt.bar(x, intensity, width=0.4, color="g", align="center",)
    plt.xlabel("Device")
    if PLOT_RELATIVE[0]:
        plt.ylabel("Light intensity relative to SPAD " + str(PLOT_RELATIVE[1]))
    else:
        plt.ylabel("Light Intensity Wm^-2")
    plt.title("SiPM Predicted Required Light Intensity")
    plt.grid()
    plt.xticks(x, names)

    plt.draw()
    plt.pause(0.001)


def Jseries(pixels):
    spad = {}
    # fill factor 0.62
    spad["name"] = str(99) + ": " + "I" + str(pixels)
    spad["cost"] = -1
    spad["area"] = pixels * 9 * 10**(-6) # m^2
    spad["pitch"]  = 20
    spad["numspad"] = 14410 * pixels
    spad["deadtime"] = 15 * 10**(-9)
    spad["pulsetime"] = 1.4 * 10**(-9)
    spad["pde"] = 30/100
    spad["peakwavelength"] = 420 * 10**(-9)
    Ep = constants.h * constants.c / spad["peakwavelength"]
    spad["photon_energy"] = Ep
    return spad


def Bseries():
    spad = {}
    # fill factor 0.62
    spad["name"] = str(59) + ": " + "B-10u"
    spad["cost"] = -1
    spad["area"] = 1 * 10**(-6) # m^2
    spad["pitch"]  = 20
    spad["numspad"] = 2880
    spad["deadtime"] = 10 * 10**(-9)
    spad["pulsetime"] = 0.7 * 10**(-9)
    spad["pde"] = 14/100
    spad["peakwavelength"] = 420 * 10**(-9)
    Ep = constants.h * constants.c / spad["peakwavelength"]
    spad["photon_energy"] = Ep
    return spad


def plot_satcurves(spads_all):
    plt.figure()
    Ldark = 0 # assume perfect zero dark count
    xmax = 10**-5
    L = np.linspace(0, xmax, 10000)
    for i, spad in enumerate(spads_all):
        ## 3.13 long thesis
        num = spad["numspad"]
        alpha = spad["pde"] * spad["area"]/(3 * 1.6*10**-19)
        T     = 1  # observation time... (1 sec)?
        tau   = spad["deadtime"]
        counts = num * alpha * T * (L + Ldark) / (1 + alpha * tau * (L+Ldark))
        asymptote_counts = T * num / tau
        spad["max_count"] = asymptote_counts
        spad["L"] = L
        spad["Ldark"] = Ldark
        spad["counts"] = counts
        col=plt.cm.nipy_spectral((i+1)/len(spads_all))
        plt.plot(L, counts, c=col, label=spad["name"])
        plt.hlines(asymptote_counts, 0, xmax, color=col, linestyle="--")
    plt.grid()
    plt.title("Count rate vs intensity of incident light on SiPMs")
    plt.legend()
    plt.show()


def intensity2ppb(spads):
    for spad in spads:
        area = spad["area"]
        watts_per_metresq = spad["sensitivity"][0]
        photons_per_bit = spad["sensitivity"][1][1]
        photon_energy = spad["photon_energy"]
        symbol_time = 1/(spad["max_data_rate"]*10**9)
        photons_per_metresq = symbol_time * watts_per_metresq/photon_energy

        print(spad["name"], "\t", watts_per_metresq*1E9*(1E-4) , "nW/cm2\t", photons_per_metresq, "photons per msq per symbol time")


def main():
    wavelength = 375E-9
    spads = spadtools.csv_to_spads(fin="./parameters.csv")

    spads.append(Jseries(16))
    spads.append(Jseries(64))
    spads.append(Bseries())

    for spad in spads:
        spad["photon_energy"] = constants.h * constants.c / wavelength

    process_spads(spads)
    spadtools.spads_to_csv(spads)
    intensity2ppb(spads)
    plot_performance(spads)
    plot_satcurves(spads)
    input("Press any Key to Continue...")


if __name__ == "__main__":
    main()
