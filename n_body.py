import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from multiprocessing import Pool
import time as t
import os

# For testing
# np.random.seed(19680807)

n = 25
start_range = 10
vel_range = 1
mass_max = 1
mass_min = 1
G = 2.5
length = 700
processes = 3

pos = np.random.uniform(-start_range, start_range, size=(n, 3))
vel = np.random.uniform(-vel_range, vel_range, size=(n, 3))
mass = np.random.uniform(mass_min, mass_max, size=(n))
mergers = set()

def size(mass_i):
    return 100*mass_i**(1/3)

def mag(v):
    return np.sum(v**2)**0.5

def v_str(v):
    if len(v) == 3:
        result = f"{v[0]} {v[1]} {v[2]}"
    else:
        result = str(v)
    return  result

def csv(pos, mass):
    line = ",".join([v_str(pos[i]).replace("[", "").replace("]", "")+f" {size(mass[i])}" for i in range(n)])
    return line+"\n"

def remove(arr, i):
    print(arr.shape, i)
    shape = (arr.shape[0]-1, arr.shape[1:])
    arr2 = np.zeros(shape=shape)
    arr2[:i] = arr[:i]
    arr2[i:] = arr[i+1:]
    return arr2

def a(i, pos, mass):
    if mass[i] != 0:
        pos_i = pos[i]
        pos_j = np.delete(pos, i, 0)
        mass_j = np.delete(mass, i, 0)
        r = pos_j - pos_i
        r3 = np.sum(r**2, axis=1)**(3/2)
        a_i = G*np.sum(r*(mass_j/r3)[:,np.newaxis], axis=0)
    else:
        a_i = np.array([0.0, 0.0, 0.0])
    return a_i

def merge_ij(i, j, mass, vel):
    if mass[i] > mass[j]:
        mass_i = mass[i] + mass[j]
        vel_i = (mass[i]*vel[i]+mass[j]*vel[j])/(mass_i)
    elif mass[i] < mass[j]:
        mass_i = 0.0
        vel_i = np.array([0.0, 0.0, 0.0])
    else:
        if i > j:
            mass_i = mass[i] + mass[j]
            if mass_i != 0:
                vel_i = (mass[i]*vel[i]+mass[j]*vel[j])/(mass_i)
            else:
                vel_i = 0
        else:
            mass_i = 0.0
            vel_i = np.array([0.0, 0.0, 0.0])
    return mass_i, vel_i

def step_i(args):
    i, pos, vel, mass, dt, mergers = args
    vel_i = vel[i]+a(i, pos, mass)*dt
    mass_i = mass[i]
    pos_i = pos[i]+vel_i*dt

    for merger in mergers:
        if i in merger:
            j = merger[int(merger.index(i) != 1)]
            mass_i, vel_i = merge_ij(i, j, mass, vel)
            break
        else:
            ()

    new_mergers = []
    for j in range(pos.shape[0]):
        if i != j:
            r = mag(pos[j] - pos[i])
            d = mass[i]**(1/3)+mass[j]**(1/3)
            if r < d:
                if i > j:
                    new_mergers.append((i,j))
                else:
                    new_mergers.append((j,i))
    result = (i, pos_i, vel_i, mass_i, new_mergers)
    return result

if __name__ == '__main__':
    start = t.time()
    with Pool(processes) as pool:
        dt = 0.1

        if os.path.exists("n_body.txt"):
            os.remove("n_body.txt")
        
        f = open("n_body.txt", "a")

        for frame in range(length):
            tasks = [(i, pos, vel, mass, dt, mergers) for i in range(n)]
            results = pool.map(step_i, tasks)
            for i, pos_i, vel_i, mass_i, new_mergers in results:
                pos[i] = pos_i
                vel[i] = vel_i
                mass[i] = mass_i
                for merger in new_mergers:
                    mergers.add(merger)
            f.write(csv(pos, mass))
        f.close()
    stop = t.time()
    print("Runtime:", stop-start)