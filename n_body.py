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

def csv(pos):
    line = ""
    for vector in pos:
        line += str(vector).replace("[", "").replace("]", "")+","
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

def update(num):
    ax.cla()
    dt = 0.1
    t = num*dt
    tasks = [(i, pos, vel, mass) for i in range(n)]
    results = []
    if __name__ == '__main__':
        with Pool(4) as pool:
            results = pool.map(update_i, tasks)
    for i, pos_i, vel_i in results:
        pos[i] = pos_i
        vel[i] = vel_i
        path[i][num] = pos[i]
        ax.scatter(pos[i][0], pos[i][1], pos[i][2], s=100*mass[i]**(1/3), marker="o")
        ax.plot([pos[0] for pos in path[i][0:num]], [pos[1] for pos in path[i][0:num]], [pos[2] for pos in path[i][0:num]])

if __name__ == '__main__':
    with Pool(5) as pool:
        start = t.time()
        dt = 0.1

        if os.path.exists("n_body.txt"):
            os.remove("n_body.txt")
        
        f = open("n_body.txt", "a")

        f.write("frame, position\n")
        for frame in range(length):
            tasks = [(i, pos, vel, mass, dt) for i in range(n)]
            results = pool.map(step_i, tasks)
            for i, pos_i, vel_i, mass_i in results:
                pos[i] = pos_i
                vel[i] = vel_i
                mass[i] = mass_i
            f.write(csv(pos))
    f.close()
    stop = t.time()
    print("Runtime:", stop-start)

# fig = plt.figure(dpi=100)
# ax = fig.add_subplot(projection='3d')

# ani = FuncAnimation(fig = fig, func = update, frames = length, interval = 10, repeat = False)

# plt.show()