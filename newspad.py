#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import spadtools
from scipy import constants

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

    plt.show(block=False)


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
    spad["pde"] = 30
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
    spad["pde"] = 14
    spad["peakwavelength"] = 420 * 10**(-9)
    Ep = constants.h * constants.c / spad["peakwavelength"]
    spad["photon_energy"] = Ep
    return spad




def main():
    spads = spadtools.csv_to_spads(fin="./parameters.csv")

    spads.append(Jseries(16))
    spads.append(Jseries(64))
    spads.append(Bseries())

    process_spads(spads)
    spadtools.spads_to_csv(spads)
    plot_performance(spads)
    input("Press any Key to Continue...")


if __name__ == "__main__":
    main()
