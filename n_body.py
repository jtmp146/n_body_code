import numpy as np
from multiprocessing import Pool
import time as t
import os

# For testing
# np.random.seed(156110)

# Simulation parameters
n = 25
x_range = 15
y_range = 15
z_range = 15
vel_range = 1
mass_max = 1
mass_min = 1
G = 2.5
length = 10000
processes = 4
spinning = False

def mag(v):
    """Calculate magnitude of vector

    Args:
        v (numpy.ndarray): Vector

    Returns:
        float: Magnitude of vector
    """    
    return np.sum(v**2)**0.5

def size(mass_i):
    """Calculate size of particle with given mass

    Args:
        mass_i (float): Particle mass

    Returns:
        float: Size of particle (for plotting)
    """    
    return 100*mass_i**(1/3)

def v_str(v):
    """Write 3D vector as a string

    Args:
        v (numpy.ndarray): Vector (e.g. [x, y, z])

    Returns:
        str: String representation of vector (e.g. "x y z") or input casted to string if not a 3D array
    """    
    if len(v) == 3:
        result = f"{v[0]} {v[1]} {v[2]}"
    else:
        result = str(v)
    return  result

def csv(pos, mass):
    """Save one timestep of simulation as a CSV

    Args:
        pos (numpy.ndarray): Positions of masses at timestep
        mass (numpy.ndarray): Masses of masses at timestep

    Returns:
        str: line of CSV just written
    """    
    line = ",".join([v_str(pos[i]).replace("[", "").replace("]", "")+f" {size(mass[i])}" for i in range(n)])
    return line+"\n"

def a(i, pos, mass):
    """Calculates acceleration of ith mass

    Args:
        i (int): Index of mass for which to calculate acceleration
        pos (numpy.ndarray): Positions of masses at timestep
        mass (numpy.ndarray): Masses of masses at timestep

    Returns:
        numpy.ndarray: Acceleration vector for ith mass
    """    
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

def merge_i(i, merger, mass, vel):
    """Calculate mass and velocity of ith mass after a merger with other masses

    Args:
        i (int): Index of mass
        merger (set): Set of all masses taking part in the merger
        mass (numpy.ndarray): Masses of masses at timestep
        vel (numpy.ndarray): Velocities of masses at timestep

    Returns:
        tuple: New mass and velocity of ith mass
    """    
    mass_i = mass[i]
    if mass[i] != 0.0:
        for j in merger:
            if i != j:
                if mass[i] > mass[j]:
                    biggest = True
                elif mass[i] < mass[j]:
                    biggest = False
                    break
                else:
                    if i > j:
                        biggest = True
                    else:
                        biggest = False
                        break
    else:
        biggest = False

    if biggest:
        mass_i = np.sum([mass[j] for j in merger])
        vel_i = np.sum([vel[j]*mass[j] for j in merger], axis=0)/mass_i
    else:
        mass_i = 0
        vel_i = [0.0, 0.0, 0.0]
    return mass_i, vel_i

def concat_mergers(mergers):
    """Combine detected merger events so no mass is involved in two mergers in a single timestep

    Args:
        mergers (list): array of merger sets

    Returns:
        list: array of merger sets that have been concatenated as described
    """    
    new_mergers = set()
    for merger1 in mergers:
        for merger2 in mergers:
            if not merger1.isdisjoint(merger2):
                merger1 = merger1.union(merger2)
            else:
                ()
        new_mergers.add(merger1)
    if new_mergers == mergers:
        return new_mergers
    else:
        return concat_mergers(new_mergers)

def step_i(args):
    """Perform one simulation timestep on ith mass

    Args:
        args (tuple): Index of mass, its initial conditions, size of timestep and list of all merger events at this timestep

    Returns:
        tuple: Index of mass, conditions after timestep, set of masses ith mass will have to merge with in next timestep
    """    
    i, pos, vel, mass, dt, mergers = args
    vel_i = vel[i]+a(i, pos, mass)*dt
    mass_i = mass[i]
    pos_i = pos[i]+vel_i*dt

    for merger in mergers:
        if i in merger:
            mass_i, vel_i = merge_i(i, merger, mass, vel)

    merger_i = []
    for j in range(n):
        r = mag(pos[j] - pos[i])
        d = mass[i]**(1/3)+mass[j]**(1/3)
        if r < d and j != i:
            merger_i.append(j)

    if len(merger_i) > 0:
        merger_i.append(i)

    result = (i, pos_i, vel_i, mass_i, frozenset(merger_i))
    return result

# Randomized setup
x = np.random.uniform(-x_range, x_range, size=n)
y = np.random.uniform(-y_range, y_range, size=n)
z = np.random.uniform(-z_range, z_range, size=n)
pos = np.stack((x, y, z), axis=1)
vel = np.random.uniform(-vel_range, vel_range, size=(n, 3))
mass = np.random.uniform(mass_min, mass_max, size=(n))
mergers = set()

# Spinning setup
if spinning:
    pos[0] = [0.0, 0.0, 0.0]
    vel[0] = [0.0, 0.0, 0.0]
    mass[0] = n*10

    for i in range(1,n):
        ax = [0, 0, 1]
        unit_v = np.cross(pos[i], ax)/mag(np.cross(pos[i], ax))
        vel[i] = unit_v*((G*mass[0]/mag(pos[i]))**0.5)

if __name__ == '__main__':
    start = t.time()
    with Pool(processes) as pool:
        dt = 0.1

        if os.path.exists("n_body.txt"):
            os.remove("n_body.txt")
        
        f = open("n_body.txt", "a")
        
        init_momentum = np.sum(vel*mass[:,np.newaxis], axis=0)
        init_mass = np.sum(mass)

        for frame in range(length):
            total_mass = np.sum(mass)
            mergers = concat_mergers(mergers)
            tasks = [(i, pos, vel, mass, dt, mergers) for i in range(n)]
            results = pool.map(step_i, tasks)
            mergers = set()
            for i, pos_i, vel_i, mass_i, new_merger in results:
                pos[i] = pos_i
                vel[i] = vel_i
                mass[i] = mass_i
                mergers.add(new_merger)
            f.write(csv(pos, mass))
        f.close()
        print(f"Initial momentum: {init_momentum}. Initial mass: {init_mass}")
        print(f"Momentum change: {np.sum(vel*mass[:,np.newaxis], axis=0)-init_momentum}. Mass change: {np.sum(mass)-init_mass}")
    stop = t.time()
    print("Runtime:", stop-start)