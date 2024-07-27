import matplotlib.pyplot as plt
import numpy as np

from matplotlib.animation import FuncAnimation

# np.random.seed(19680807)

n = 25
start_range = 15
vel_range = 1
mass_max = 1
mass_min = 1
G = 2.5
length = 500
fig_size = 15

path = np.zeros(shape=(n, length, 3))
pos = np.random.uniform(-start_range, start_range, size=(n, 3))
vel = np.random.uniform(-vel_range, vel_range, size=(n, 3))
mass = np.random.uniform(mass_min, mass_max, size=(n))
deleted = []

def mag(v):
    return np.sqrt(v[0]**2+v[1]**2+v[2]**2)

def update(num, pos=pos):
    ax.cla()
    t = num/10
    dt = 0.1
    for i in range(n):   
        a = 0
        for j in range(n):
            if j == i and j not in deleted:
                ()
            elif i not in deleted:
                r = pos[j] - pos[i]
                if mag(r) > mass[j]**(1/3)+mass[i]**(1/3):
                    a += r*G*mass[j]/(mag(r)**3)
                else:
                    vel[i] = (mass[i]*vel[i]+mass[j]*vel[j])/(mass[i]+mass[j])
                    mass[i] += mass[j]
                    mass[j] = 0
                    deleted.append(j)
            else:
                vel[i] = 0
                    
        vel[i] = vel[i]+a*dt
        pos[i] = pos[i]+vel[i]*dt
    for i in range(n):
        path[i][num] = pos[i]
        ax.scatter(pos[i][0], pos[i][1], pos[i][2], s=100*mass[i]**(1/3), marker="o")
        ax.plot([pos[0] for pos in path[i][0:num]], [pos[1] for pos in path[i][0:num]], [pos[2] for pos in path[i][0:num]])

    # ax.set_xlim(-fig_size, fig_size)
    # ax.set_ylim(-fig_size, fig_size)
    # ax.set_zlim(-fig_size, fig_size)


fig = plt.figure(dpi=100)
ax = fig.add_subplot(projection='3d')

ani = FuncAnimation(fig = fig, func = update, frames = length, interval = 10, repeat = False)

plt.show()