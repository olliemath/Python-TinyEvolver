from tinyevolver import Population, IslandModel
import cPickle as pickle

"""
    This is a repeat of example 1, except that we have a saved population
    we want to evolve further. To prevent it going down an evolutionary
    dead-end or if new information comes in, we might want to evolve
    a second population and intermingle / select the best from both.
    This is the island model.
"""

prototype = [False for _ in range(100)]
islands = [Population(prototype, None, sum) for _ in range(2)]

# We load some saved data.
with open('data.pkl', 'rb') as f:
    data = pickle.load(f)

# We put the data in the first island:
islands[0].populate(base_population=data)
# and randomly populate the second:
islands[1].populate()

i = IslandModel(islands)

# The island model can be single-threaded or use multiprocessing to
# evolve. On Windows, multiprocessing requires the following check.
if __name__ == "__main__":

    i.multi_evolve()
    print "Best individual had fitness", i.best.fitness
