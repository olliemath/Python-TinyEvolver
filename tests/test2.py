from tinyevolver import Population
from random import uniform, seed
seed(1234)


prototype = [1] + [1.0 for _ in range(100)]
bounds = [(0, 1)] + [(uniform(0, 10), uniform(0, 10)) for _ in range(100)]


def fitness(ind):
    return sum(ind)


# Now for the evolution
p = Population(prototype, bounds, fitness)
p.populate(popsize=500)
p.evolve(100)
