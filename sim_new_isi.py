#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt


def init():
    numspad = 10000
    dt = 0.1e-9
    tdead = 15e-9
    simtime = 100e-6
    bittime = 2e-9

    light_power = 0
    bit_power = 0.01

    spads = np.ones(numspad)
    incident_light = np.ones(int(simtime/dt))

    # Generate Binary Data
    bitpattern = [1,0,1,0,1,1,1,1,0,0,0,0,1,1,0,0,1,1,1,0,1,0,0,0,1,0]
    lbp = len(bitpattern)
    saperbit = int(np.ceil(bittime/dt))
    numbits = simtime/bittime
    bitpattern_reps = numbits/(lbp*saperbit)

    bitpattern = np.tile(bitpattern, int(np.ceil(bitpattern_reps)))
    bitpattern = np.repeat(bitpattern,saperbit)
    bitpattern = np.repeat(bitpattern,saperbit)
    bitpattern = bitpattern[:len(incident_light)]

    light = incident_light * light_power + bitpattern * bit_power
    return {"bitpattern":bitpattern, "incident_light":light, "saperbit":saperbit,
            "numspad":numspad, "dt":dt, "tdead":tdead, "simtime":simtime,
            "bittime":bittime, "light_power":light_power,"bit_power":bit_power,
            "spads":spads}


def sim_spad(sim):
    light = sim["incident_light"]
    numspad = sim["numspad"]
    dt = sim["dt"]
    bittime = sim["bittime"]
    spads = sim["spads"]
    deadtime = sim["tdead"]

    fired = np.zeros(len(light))
    for i, l in enumerate(light):
        spads = [s+deadtime/dt if s<1 else 1 for s in spads]
        probtofire = l*dt/bittime
        wanttofire = np.random.choice([0,1], size=(len(spads),), p=[(1-probtofire), probtofire])
        for j,(s,f) in enumerate(zip(spads,wanttofire)):
            if s < 1 and f == 1:
                spads[j] = 0
            if 1 <= s and f == 1:
                spads[j] = 0
                fired[i] += 1
        if i % 1000 == 0:
            print(i/len(light))

    return(fired)



def main():
    sim = init()
    fired = sim_spad(sim)
    plt.figure()
    plt.plot(fired)
    plt.show()


main()
