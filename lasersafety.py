#!/usr/bin/python3

# https://onlinelibrary.wiley.com/doi/pdf/10.1002/9781118688977.app1

def wl2mpe(wl, t):
    T1, CA, CC = 1000000, 1000000, 1000000
    T1 = 10*10**(20*(wl-0.450))

    if wl >= 0.4:
        if wl <= 0.7:
            CA = 1
        elif wl <= 1.050:
            CA = 10**(2*(wl-0.700))
        elif wl <= 1.400:
            CA = 5

    if wl >= 0.40:
        if wl <= 0.45:
            CB = 1
        elif wl <= 0.6:
            CB = 10**(20*(wl-0.45))

    if wl >= 1.050:
        if wl <= 1.150:
            CC = 1
        elif wl <= 1.200:
            CC = 10**(18*(wl-1.150))
        elif wl <= 1.400:
            CC = 8

    if wl <= 0.180:
        return None
    if wl <= 0.302:
        return (3*10**-3)
    if wl <= 0.303:
        return (4*10**-3)
    if wl <= 0.304:
        return (6*10**-3)
    if wl <= 0.305:
        return (10*10**-3)
    if wl <= 0.306:
        return (16*10**-3)
    if wl <= 0.307:
        return (25*10**-3)
    if wl <= 0.308:
        return (40*10**-3)
    if wl <= 0.309:
        return (63*10**-3)
    if wl <= 0.310:
        return 0.1
    if wl <= 0.311:
        return 0.16
    if wl <= 0.312:
        return 0.25
    if wl <= 0.313:
        return 0.4
    if wl <= 0.314:
        return 0.63
    if wl <= 0.4:
        if t <= 18*10**-6:
            return (0.56*t**0.25)
        else:
            return 1
    if wl <= 0.7:
        if t <= 18*10**-6:
            return ((1.8*t**0.75)*10**-3)
        if t <= 10:
            return 1
        if wl <= 0.45 and t <= 100:
            return (10**-2)
        if wl <= 0.5 and t <= T1:
            return t*10**-3
        if wl <= 0.5 and t <= 100:
            return (CB*10**-2)
        if wl <= 0.5:
            return t*CB*10**-4
        else:
            return t*10**-3
    if wl <= 1.050:
        if t <= 18*10**-6:
            return (5*CA*10**-7)
        elif t <= 10:
            return ((10**-3)*1.8*CA*t**0.75)
        else:
            return t*CA*10**-3
    if wl <= 1.400:
        if t <= 50*10**-6:
            return (5*CC*10**-6)
        if t <= 10:
            return (10**-3)*(9*CA*t**0.75)
        else:
            return t*5*CC*10**-3
    if wl <= 1.500:
        if t <= 10**-3:
            return 0.1
        if t <= 10:
            return (0.56*t**0.25)
        else:
            return 0.1*t
    if wl <= 1.8:
        if t <= 10:
            return 1
        else:
            return 0.1*t
    if wl <= 2.6:
        if t <= 10**-3:
            return 1
        if t <= 10:
            return (0.56*t**0.25)
        else:
            return t*0.1*10**-3
    if wl <= 1000:
        if t <= 10**-7:
            return (1*10**-2)
        if t <= 10:
            return (0.56*t**0.25)
        else:
            return 0.1*t


def test():
    import numpy as np
    import matplotlib.pyplot as plt

    t_max = 3*10**4
    t_min = 10**-8
    ts = np.logspace(t_min, t_max, 10)
    ts = [t_max]

    wls = np.linspace(0.18, 1, 100000)
    plt.figure()
    for t in ts:
        mpes = [wl2mpe(wl, t) for wl in wls]
        plt.plot(wls, mpes)

    plt.grid()
    plt.ylabel("Light Intensity Wm^-2")
    plt.xlabel("Wavelength/um")
    plt.title("MPE for 8 hour exposure")

    plt.show()


def get_mpe(wl):
    return(1E-1)
    return wl2mpe(wl*1E6,3*10**4)/(3*10**4)


def main():
    test()
    print("this file is not to be run directly - please import as use that way")


if __name__ == "__main__":
    main()
