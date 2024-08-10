import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from multiprocessing import Pool
import time as t
import os

# np.random.seed(19680807)

n = 2
start_range = 15
vel_range = 0
mass_max = 1
mass_min = 1
G = 2.5
length = 500

pos = np.random.uniform(-start_range, start_range, size=(n, 3))
vel = np.random.uniform(-vel_range, vel_range, size=(n, 3))
mass = np.random.uniform(mass_min, mass_max, size=(n))
mergers = set()

def size(mass_i):
    return 200*mass_i**(1/3)

def mag(v):
    return np.sqrt(v[0]**2+v[1]**2+v[2]**2)

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
        a_i = 0
    return a_i

def merge_ij(i, j, mass):
    if mass[i] > mass[j]:
        mass_i = mass[i] + mass[j]
        vel_i = (mass[i]*vel[i]+mass[j]*vel[j])/(mass_i)
    elif mass[i] < mass[j]:
        mass_i = 0.0
        vel_i = 0.0
    else:
        if i > j:
            mass_i = mass[i] + mass[j]
            vel_i = (mass[i]*vel[i]+mass[j]*vel[j])/(mass_i)
        else:
            mass_i = 0.0
            vel_i = 0.0
    return mass_i, vel_i

def step_i(args):
    i, pos, vel, mass, dt, mergers = args
    for merger in mergers:
        if i in merger:
            mass_i, vel_i = merge_ij(merger[0], merger[1], mass)
            break
        else:
            vel_i = vel[i]+a(i, pos, mass)*dt
            mass_i = mass[i]
    pos_i = pos[i]+vel_i*dt
    for j in range(pos.shape[0]):
        r = mag(pos[j] - pos[i])
        if 
    result = (i, pos_i, vel_i, mass_i, new_mergers)
    return result

if __name__ == '__main__':
    start = t.time()
    with Pool(5) as pool:
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