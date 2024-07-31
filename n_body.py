import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from multiprocessing import Pool

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

def mag(v):
    return np.sqrt(v[0]**2+v[1]**2+v[2]**2)

def remove(arr, i):
    shape = (arr.shape[0]-1, arr.shape[1:])
    arr2 = np.zeros(shape=shape)
    arr2[:i] = arr[:i]
    arr2[i:] = arr[i+1:]
    return arr2

def a(i, pos, mass):
    a = 0
    pos_i = pos[i]
    pos_j = remove(pos, i)
    mass_j = remove(pos, i)
    r = pos_j - pos_i
    r3 = np.sum(r**2, axis=1)**(3/2)
    a = G*np.sum(r*(mass_j/r3)[:,np.newaxis], axis=0)
    return a

def update_i(args):
    i, pos1, vel1, mass = args
    vel = vel1+a(i, pos1, mass)*dt
    pos = pos1+vel*dt
    return i, pos, vel

def update(num, pos=pos):
    ax.cla()
    dt = 0.1
    t = num*dt
    tasks = [(i, pos, vel, mass) for i in range]
    for i in range(n):   
        vel[i] = vel[i]+a(i)*dt
        pos[i] = pos[i]+vel[i]*dt
    for i in range(n):
        path[i][num] = pos[i]
        ax.scatter(pos[i][0], pos[i][1], pos[i][2], s=100*mass[i]**(1/3), marker="o")
        ax.plot([pos[0] for pos in path[i][0:num]], [pos[1] for pos in path[i][0:num]], [pos[2] for pos in path[i][0:num]])


fig = plt.figure(dpi=100)
ax = fig.add_subplot(projection='3d')

ani = FuncAnimation(fig = fig, func = update, frames = length, interval = 10, repeat = False)

plt.show()