import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

fig_size = 15
fix_axes = True

with open("n_body.txt") as data:
    lines = data.readlines()

point_hist = []

for line in lines:
    points = line.split(",")
    point_step = []
    for point in points:
        x, y, z, s = [float(val) for val in point.split(" ")]
        point_step.append([x, y, z, s])
    point_hist.append(point_step)

def update(num):
    ax.cla()
    points = point_hist[num]
    for i in range(len(points)):
        point = points[i]
        ax.scatter(point[0], point[1], point[2], s=point[3], marker="o")
        if num > 0:
            path = [points[i] for points in point_hist[:num+1]]
            ax.plot([pos[0] for pos in path], [pos[1] for pos in path], [pos[2] for pos in path])

    if fix_axes:
        ax.set_xlim(-fig_size, fig_size)
        ax.set_ylim(-fig_size, fig_size)
        ax.set_zlim(-fig_size, fig_size)

fig = plt.figure(dpi=100)
ax = fig.add_subplot(projection='3d')

ani = FuncAnimation(fig = fig, func = update, frames = len(lines), interval = 0, repeat = False)

plt.show()