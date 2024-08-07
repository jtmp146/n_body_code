import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from multiprocessing import Pool
import time as t
import os

# np.random.seed(19680807)

n = 25
start_range = 15
vel_range = 1
mass_max = 1
mass_min = 1
G = 2.5
length = 500

path = np.zeros(shape=(n, length, 3))
pos = np.random.uniform(-start_range, start_range, size=(n, 3))
vel = np.random.uniform(-vel_range, vel_range, size=(n, 3))
mass = np.random.uniform(mass_min, mass_max, size=(n))
deleted = []

def size(mass_i):
    return 200*mass_i**(1/3)

def v_str(v):
    return f"{v[0]} {v[1]} {v[2]}" 

def csv(pos, mass):
    line = ",".join([v_str(pos[i]).replace("[", "").replace("]", "")+" {}".format(size(mass[i])) for i in range(n)])
    return line+"\n"

def remove(arr, i):
    print(arr.shape, i)
    shape = (arr.shape[0]-1, arr.shape[1:])
    arr2 = np.zeros(shape=shape)
    arr2[:i] = arr[:i]
    arr2[i:] = arr[i+1:]
    return arr2

def a(i, pos, mass):
    pos_i = pos[i]
    pos_j = np.delete(pos, i, 0)
    mass_j = np.delete(mass, i, 0)
    r = pos_j - pos_i
    r3 = np.sum(r**2, axis=1)**(3/2)
    a_i = G*np.sum(r*(mass_j/r3)[:,np.newaxis], axis=0)
    return a_i

def step_i(args):
    i, pos, vel, mass, dt = args
    vel_i = vel[i]+a(i, pos, mass)*dt
    pos_i = pos[i]+vel_i*dt
    mass_i = mass[i]
    return (i, pos_i, vel_i, mass_i)

if __name__ == '__main__':
    start = t.time()
    with Pool(5) as pool:
        dt = 0.1

        if os.path.exists("n_body.txt"):
            os.remove("n_body.txt")
        
        f = open("n_body.txt", "a")

        for frame in range(length):
            tasks = [(i, pos, vel, mass, dt) for i in range(n)]
            results = pool.map(step_i, tasks)
            for i, pos_i, vel_i, mass_i in results:
                pos[i] = pos_i
                vel[i] = vel_i
                mass[i] = mass_i
            f.write(csv(pos, mass))
        f.close()
    stop = t.time()
    print("Runtime:", stop-start)