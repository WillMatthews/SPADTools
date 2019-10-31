#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import spadtools

TARGET_BER = 10**-3
SEARCH_SPACE = np.linspace(0.5, 500, 100000)

print(spadtools.get_ns0(TARGET_BER, 0))

def main():

    spads = spadtools.csv_to_spads(fin="./parameters.csv")

    for i, spad in enumerate(spads):

        spadtools.get_max_counts(spad)
        p = 0.99 # ???? This is "pulse falling percentage" see Long's thesis 109
        spadtools.get_bandwidth(spad,p)

        print("\nSPAD", spad["name"],"\n==================")

        print('{0:.2f}'.format((spad["max_count"] / spadtools.get_ns0(TARGET_BER, 0))*10**-9), "GRUBBY HACK")
        spad["hack_data_rate"] = (spad["max_count"] / spadtools.get_ns0(TARGET_BER, 0))*10**-9
        spad["sensitivity"] = None
        for numgig in SEARCH_SPACE:
            symbol_time = 1 / (numgig * 10**9) # 10Gbps
            old_sensitivity = spad["sensitivity"]
            spad["sensitivity"] = spadtools.get_sensitivity(spad, symbol_time, TARGET_BER)
            if spad["sensitivity"] is None:
                if old_sensitivity is not None:
                    print('{0:.2f}'.format(numgig), "Gbps...", old_sensitivity)
                    spad["max_data_rate"] = numgig
                    spad["sensitivity"] = old_sensitivity
                else:
                    print("Data Rate <", min(SEARCH_SPACE),"Gbps")
                break
        else:
            print("Data Rate >", max(SEARCH_SPACE),"Gbps")


    spadtools.spads_to_csv(spads)

    hackrates, realrates = [], []
    names = []
    photons, intensity = [], []
    for i, spad in enumerate(spads):
        hackrates.append(spad["hack_data_rate"])
        realrates.append(spad["max_data_rate"])
        names.append(spad["name"])
        photons.append(spad["sensitivity"][1][1])
        #intensity.append(spad["sensitivity"][0])
        if i == 0:
            intense = spad["sensitivity"][0]
            intensity.append(1)
        else:
            intensity.append(spad["sensitivity"][0]/intense)

    x = np.array([x for x in range(len(hackrates))])
    ax = plt.subplot(111)
    print(hackrates)
    print(realrates)
    ax.bar(x-0.2, hackrates, width=0.4, color='b', align='center', label="No ISI")
    ax.bar(x+0.2, realrates, width=0.4, color='g', align='center', label="With ISI PP")
    plt.xticks(x, names)
    plt.xlabel("Device")
    plt.ylabel("Data Rate (Gbps)")
    plt.title("SiPM Predicted Data Rates")
    plt.grid()
    plt.legend()

    plt.figure()
    plt.bar(x, photons, width=0.4, color="r", align="center",)
    plt.xlabel("Device")
    plt.ylabel("Photons per Bit (ONE)")
    plt.title("SiPM Predicted Photons per Bit")
    plt.grid()
    plt.xticks(x, names)

    plt.figure()
    plt.bar(x, intensity, width=0.4, color="g", align="center",)
    plt.xlabel("Device")
    plt.ylabel("Light Intensity Wm^-2")
    plt.title("SiPM Predicted Required Light Intensity")
    plt.grid()
    plt.xticks(x, names)


    plt.show()



if __name__ == "__main__":
    main()
