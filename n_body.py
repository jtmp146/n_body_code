import numpy as np
from multiprocessing import Pool
import time as t
import os

# For testing
# np.random.seed(156110)

# start_seed = np.random.randint(low=1000000, size=1)
# np.random.seed(start_seed)
# print(f"Start seed: {start_seed}")

n = 25
start_range = 15
vel_range = 1
mass_max = 1
mass_min = 1
G = 2.5
length = 10000
processes = 4

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

def merge_ij(i, j, init_mass_i, mass, init_vel_i, vel):
    print(f"Merger of mass {i} ({init_mass_i}) and mass {j} ({mass[j]})")
    if init_mass_i > mass[j]:
        mass_i = init_mass_i + mass[j]
        vel_i = (init_mass_i*init_vel_i+mass[j]*vel[j])/(mass_i)
    elif init_mass_i < mass[j]:
        mass_i = 0.0
        vel_i = np.array([0.0, 0.0, 0.0])
    else:
        if i > j:
            mass_i = init_mass_i + mass[j]
            if mass_i != 0:
                vel_i = (init_mass_i*init_vel_i+mass[j]*vel[j])/(mass_i)
            else:
                vel_i = 0
        else:
            mass_i = 0.0
            vel_i = np.array([0.0, 0.0, 0.0])
    # print(f"Mass of mass {i}: {mass_i}")
    print(f"\tMass {i} change: {mass_i-init_mass_i}")
    return mass_i, vel_i

def merge_i(i, init_vel_i, init_mass_i, merger, mass, vel):
    mass_i = init_mass_i
    vel_i = init_vel_i
    for j in merger:
        if i != j and mass[i] != 0:
            if mass[i] > mass[j]:
                mass_i += mass[j]
                vel_i = (mass_i*vel_i+mass[j]*vel[j])/mass_i
            elif mass[i] < mass[j]:
                mass_i = 0.0
                vel_i = [0.0, 0.0, 0.0]
                break
            else:
                if i > j:
                    mass_i += mass[j]
                    vel_i = (mass_i*vel_i+mass[j]*vel[j])/mass_i
                else:
                    mass_i = 0.0
                    vel_i = [0.0, 0.0, 0.0]
                    break
    return mass_i, vel_i

def concat_mergers(mergers):
    new_mergers = set()
    for merger1 in mergers:
        for merger2 in mergers:
            set1 = set(merger1)
            set2 = set(merger2)
            if not set1.isdisjoint(set2):
                merger1 = tuple(set1.union(set2))
            else:
                ()
        new_mergers.add(merger1)
    if new_mergers == mergers:
        return new_mergers
    else:
        return concat_mergers(new_mergers)

def step_i(args):
    i, pos, vel, mass, dt, mergers = args
    vel_i = vel[i]+a(i, pos, mass)*dt
    mass_i = mass[i]
    pos_i = pos[i]+vel_i*dt

    # for merger in mergers:
    #     if i in merger:
    #         j = merger[int(merger.index(i) != 1)]
    #         mass_i, vel_i = merge_ij(i, j, mass_i, mass, vel_i, vel)
    #     else:
    #         ()

    for merger in mergers:
        if i in merger:
            mass_i, vel_i = merge_i(i, vel_i, mass_i, merger, mass, vel)

    merger_i = []
    for j in range(n):
        r = mag(pos[j] - pos[i])
        d = mass[i]**(1/3)+mass[j]**(1/3)
        if r < d and j != i:
            merger_i.append(j)

    if len(merger_i) > 0:
        merger_i.append(i)

    result = (i, pos_i, vel_i, mass_i, tuple(merger_i))
    return result

if __name__ == '__main__':
    start = t.time()
    with Pool(processes) as pool:
        dt = 0.1

        if os.path.exists("n_body.txt"):
            os.remove("n_body.txt")
        
        f = open("n_body.txt", "a")

        for frame in range(length):
            total_mass = np.sum(mass)
            old_mergers = mergers
            mergers = concat_mergers(mergers)
            tasks = [(i, pos, vel, mass, dt, mergers) for i in range(n)]
            results = pool.map(step_i, tasks)
            mergers = set()
            for i, pos_i, vel_i, mass_i, new_merger in results:
                pos[i] = pos_i
                vel[i] = vel_i
                mass[i] = mass_i
                mergers.add(new_merger)
            if total_mass != np.sum(mass):
                print(f"Frame {frame}")
                print(f"Mass change: {np.sum(mass)-total_mass}")
                print(f"Total Mergers: {old_mergers}")
            f.write(csv(pos, mass))
            # print()
        f.close()
    stop = t.time()
    print("Runtime:", stop-start)