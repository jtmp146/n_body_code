import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

fig_size = 15
fix_axes = False
show_frames = False
start = 100
length = 100
source = "n_body.txt"

with open(source) as data:
    lines = data.readlines()

point_hist = []

for line in lines:
    points = line.split(",")
    point_step = []
    for point in points:
        x, y, z, s = [float(val) for val in point.split(" ")]
        point_step.append([x, y, z, s])
    point_hist.append(point_step)

n = len(point_hist[0])

def update(num):
    ax.cla()
    frame = num+start
    points = point_hist[frame]
    if show_frames:
        print(f"Frame {frame}")
    for i in range(len(points)):
        point = points[i]
        # if i != 12 and i != 4:
        #     ax.scatter(point[0], point[1], point[2], s=point[3], marker="o")
        # else:
        ax.scatter(point[0], point[1], point[2], s=point[3], marker="o")
        if num > 0:
            path = [points[i] for points in point_hist[:frame+1]]
            ax.plot([pos[0] for pos in path], [pos[1] for pos in path], [pos[2] for pos in path])

        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_title(f"Motion of {n} massive bodies under gravity")

    if fix_axes:
        ax.set_xlim(-fig_size, fig_size)
        ax.set_ylim(-fig_size, fig_size)
        ax.set_zlim(-fig_size, fig_size)

fig = plt.figure(dpi=100)
ax = fig.add_subplot(projection='3d')


ani = FuncAnimation(fig = fig, func = update, frames = length, interval = 0, repeat = False)

plt.show()