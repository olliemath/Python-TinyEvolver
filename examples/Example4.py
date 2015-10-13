from tinyevolver.core import Population, Evolve
import numpy as np

"""
    This is a more complex example which tries to fit a polynomial to a
    noisy sine curve.
    We want an equation of the form a1 + a2 * x + a2 * x ** 2 + ..., so
    our individuals' genes will be the coefficients (floats) for this
    expression.
"""


prototype = [0.0 for _ in range(6)]  # this goes up to x^5
bounds = [(-1.0, 1.0) for _ in range(6)]

# Construct the noisy sine curve to be approximated
xs = np.linspace(0, 3)
ys = np.sin(xs) + np.random.normal(0.0, 0.1, 50)


# An individual with a geater mean-absolute-error is less fit:
def fitness(ind):
    return -np.mean(np.abs(ys - sum(ind[n] * xs ** n for n in range(6))))


# Now we're good to go:
p = Population(prototype, bounds, fitness)
p.populate(500)
Evolve(p, ngen=50)


# If you have matplotlib installed, we can plot the best result:
try:
    import matplotlib.pyplot as plt
    best_ind = p.best
    plt.plot(xs, ys)
    plt.plot(xs, sum(best_ind[n] * xs ** n for n in range(6)))
    plt.show()

except ImportError:
    pass
