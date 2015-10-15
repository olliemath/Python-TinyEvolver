from tinyevolver import Population
import random
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

random.seed(1234)

"""
    For this example we're going to try fiting a power of x to some data:
    so e.g. d(t) = ax^n + b should resonably approximate some data
    depending on t.
"""

# We want n to be integer, and a,b to be floats, so
prototype = [1.0, 1, 1.0]
# And we restrict the possible genes to these intervals:
bounds = [(0.0, 1.0), (0, 3), (0, 5.0)]

# How fit an individual is will depend on how well it approximates the
# data. So let's cook up some data:
times = range(20)
data = [0.5 * time ** 2 + 1.0 + random.uniform(0, 10) for time in times]


def fitness(ind):
    curve = [ind[0] * time ** ind[1] + ind[2] for time in times]
    square_error = [(f - d) ** 2 for f, d in zip(curve, data)]
    # More error = less fit
    try:
        return 20.0 / sum(square_error)
    except ZeroDivisionError:
        return float('inf')


# Now to populate and evolve:
p = Population(prototype, bounds, fitness)
p.populate()
p.evolve()

# Let's see how we did:
if plt:
    best_ind = p.best
    best_fit = [best_ind[0] * time ** best_ind[1] + best_ind[2] for time in times]
    plt.plot(times, data)
    plt.plot(times, best_fit)
    plt.show()
