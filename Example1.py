from tinyevolver import Population

"""
    In this example we consider individuals consisting entirely of random
    booleans. The more 'True's the better (fitter) the individual.
"""

# Our prototype individual is a list of (arbitrary) boolean geans
prototype = [False for _ in range(100)]

# This statement initialises a population class with appropriate methods.
p = Population(prototype=prototype, gene_bounds=None, fitness_func=sum)

# Create the desired number of individuals in the class:
p.populate(popsize=300)

# Evolve! It's as simple as that.
p.evolve(verbose=True)
