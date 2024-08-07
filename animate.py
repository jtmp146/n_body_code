import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

with open("n_body.txt") as data:
    lines = data.readlines()

length, n = [int(val) for val in lines[0].replace("\n", "").split(",")]
pos = np.empty(shape=(length, n, 3))
size = np.empty(shape=(length, n))

for i in range(1, length+1):
    points = lines[i].split(",")
    for j in range(n):
        x, y, z, s = [float(val) for val in points[j].split(" ")]
        pos[i-1][j] = [x, y, z]
        size[i-1][j] = s

def update(num, pos=pos):
    ax.cla()
    pos_step = pos[num]
    size_step = size[num]
    for i in range(n):
        pos = pos_step[i]
        ax.scatter(pos[0], pos[1], pos[2], s=size_step[i], marker="o")

fig = plt.figure(dpi=100)
ax = fig.add_subplot(projection='3d')

ani = FuncAnimation(fig = fig, func = update, frames = length, interval = 10, repeat = False)

plt.show()