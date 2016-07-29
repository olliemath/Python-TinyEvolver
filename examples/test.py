from tinyevolver import Population
from random import uniform

proto = [1.0 for _ in range(100)]
bounds = [(0, uniform(0, 10)) for _ in range(100)]


def fit(genes):
    return sum(genes)


pop = Population(proto, bounds, fit)
pop.populate(500)
pop.evolve(100)
