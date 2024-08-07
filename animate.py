import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

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
    for point in points :
        ax.scatter(point[0], point[1], point[2], s=point[3], marker="o")

fig = plt.figure(dpi=100)
ax = fig.add_subplot(projection='3d')

ani = FuncAnimation(fig = fig, func = update, frames = len(lines), interval = 0, repeat = False)

plt.show()