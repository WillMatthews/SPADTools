#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import spadtools

PLOT_RELATIVE = (False, 1)
TARGET_BER = 10**-3
SEARCH_SPACE = np.linspace(0.1, 500, 100000)

print("\n"*8, "{0:.2f}".format(spadtools.get_ns0(TARGET_BER, 0)), "photons typically required at Poisson Limit")



def process_spads(spads):
    for i, spad in enumerate(spads):
        spadtools.get_max_data_rate(spad, SEARCH_SPACE)


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


def main():
    spads = spadtools.csv_to_spads(fin="./parameters.csv")
    process_spads(spads)
    spadtools.spads_to_csv(spads)
    plot_performance(spads)
    input("Press any Key to Continue...")


if __name__ == "__main__":
    main()
