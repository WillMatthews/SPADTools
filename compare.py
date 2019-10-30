#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import spadtools

#TARGET_BER = np.exp(-10)
TARGET_BER = 
SEARCH_SPACE = np.linspace(1, 50, 1000)

print(spadtools.get_ns0(TARGET_BER, 0))
exit()

def main():

    spads = spadtools.csv_to_spads(fin="./parameters.csv")

    for i, spad in enumerate(spads):

        spadtools.get_max_counts(spad)
        p = 0.99 # ???? This is "pulse falling percentage" see Long's thesis 109
        spadtools.get_bandwidth(spad,p)

        print("\nSPAD",i+1, spad["name"],"\n==================")

        print((spad["max_count"] / spadtools.get_ns0(TARGET_BER, 0))*10**-9, "GRUBBY HACK")
        spad["sensitivity"] = None
        for numgig in SEARCH_SPACE:
            symbol_time = 1 / (numgig * 10**9) # 10Gbps
            old_sensitivity = spad["sensitivity"]
            spad["sensitivity"] = spadtools.get_sensitivity(spad, symbol_time, TARGET_BER)
            if spad["sensitivity"] is None:
                print(numgig, "Gbps...", old_sensitivity)
                break
        else:
            print("Data Rate >", max(SEARCH_SPACE),"Gbps")


if __name__ == "__main__":
    main()
