from tinyevolver import Population
import random

random.seed(1234)
proto = [1.0 for _ in range(100)]
bounds = [(0, random.uniform(0, 10)) for _ in range(100)]

pop = Population(proto, bounds, sum)
pop.populate(500)
pop.evolve(100)
