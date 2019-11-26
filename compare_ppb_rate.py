#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import spadtools

PLOT_RELATIVE = (False, 1)
TARGET_BER = 10**-3
SEARCH_SPACE = np.linspace(0.1, 500, 100000)

MIN_BIT_ONE = spadtools.get_ns0(10**-3, 0)
PHOTON_RANGE = np.linspace(MIN_BIT_ONE, 100 * MIN_BIT_ONE, 1000)

print("\n"*8, "{0:.2f}".format(spadtools.get_ns0(TARGET_BER, 0)), "photons typically required at Poisson Limit")



def process_spads(spads):
    for i, spad in enumerate(spads):
        spadtools.get_rate_vs_photons(spad, PHOTON_RANGE, SEARCH_SPACE)
        break


def plot_performance(spads):
    hackrates, realrates = [], []
    names = []
    photons, intensity = [], []

    spad = spads[PLOT_RELATIVE[1]-1]

    hdr=[]
    idr=[]
    lis=[]
    for p in PHOTON_RANGE:
        hr=spad["intensity"][p]["hack_data_rate"] # hack DR
        ir=spad["intensity"][p]["max_data_rate"] # isi DR
        li=spad["intensity"][p]["sensitivity"][0] # light intensity
        hdr.append(hr)
        idr.append(ir)
        lis.append(li)

    hdr = np.array(hdr)
    idr = np.array(idr)
    lis = np.array(lis)

    plt.plot(PHOTON_RANGE, hdr, label="hack data rate")
    plt.plot(PHOTON_RANGE, idr, label="max isi data rate")
    plt.legend()
    plt.xlabel("Photons Per Bit ONE")
    plt.ylabel("Data Rate")
    plt.grid()


    plt.figure()
    plt.plot(lis, hdr, label="hack data rate")
    plt.plot(lis, idr, label="max isi data rate")
    plt.xlabel("Light Intensity at RX")
    plt.ylabel("Data Rate")
    plt.grid()
    plt.legend()
    plt.show()

def main():
    spads = spadtools.csv_to_spads(fin="./parameters.csv")
    process_spads(spads)
    spadtools.spads_to_csv(spads)
    plot_performance(spads)
    input("Press any Key to Continue...")


if __name__ == "__main__":
    main()
