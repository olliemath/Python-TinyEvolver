from __future__ import print_function
from array import array
from copy import copy
import random


class Individual(object):
    """ An 'indivudal' class. Behaves like/is initialised with array/list of genes.
        Contains methods for recording fitness. """
    def __init__(self, gene_list):
        self.genes = gene_list
        self._fitness = None
        self._valid = False

    def __getitem__(self, key):
        return self.genes[key]

    def __setitem__(self, key, value):
        self.genes[key] = value

    def __len__(self):
        return len(self.genes)

    def __iter__(self):
        return iter(self.genes)

    def __copy__(self):
        new = Individual(copy(self.genes))
        if self.valid:
            new.fitness = self.fitness
        return new

    @property
    def fitness(self):
        if self._valid:
            return self._fitness
        else:
            raise AttributeError("Individual does not have a valid fitness")

    @fitness.setter
    def fitness(self, value):
        self._fitness = value
        self._valid = True

    @fitness.deleter
    def fitness(self):
        self._fitness = None
        self._valid = False

    @property
    def valid(self):
        return self._valid

    @valid.deleter
    def valid(self):
        self._valid = False


# Generators for individual genes
def BoolGenerator(bounds):
    def generator():
        return bool(random.getrandbits(1))
    return generator


def IntGenerator(bounds):
    def generator():
        return random.randint(*bounds)
    return generator


def FloatGenerator(bounds):
    def generator():
        return random.uniform(*bounds)
    return generator


def Generator(g, bounds):
    if type(g) is bool:
        return BoolGenerator(bounds)
    elif type(g) is int:
        return IntGenerator(bounds)
    elif type(g) is float:
        return FloatGenerator(bounds)
    else:
        raise TypeError("Prototype genes must be float, int or boolean.")

# Helper dict for generating arrays
typecodes = {bool: 'b', int: 'i', float: 'd'}


# Mating functions - gene by gene
def BoolMate(ind1, ind2, N, a=0.5, b=0.5, cutoff=1):
    if N <= cutoff:
        return ind2[N], ind1[N]
    return ind1[N], ind2[N]


def IntMate(ind1, ind2, N, a=0.5, b=0.5, cutoff=1):
    if N <= cutoff:
        return ind2[N], ind1[N]
    return ind1[N], ind2[N]


def FloatMate(ind1, ind2, N, a=0.5, b=0.5, cutoff=1):
    return a * ind1[N] + b * ind2[N], b * ind1[N] + a * ind2[N]


def Mater(g):
    if type(g) is bool:
        return BoolMate
    elif type(g) is int:
        return IntMate
    elif type(g) is float:
        return FloatMate
    else:
        raise TypeError("Prototype genes must be float, int or boolean.")


# Mutating functions - gene by gene
def BoolMutate(bounds):
    def mutator(ind, N, gen, ngen, indpb):
        if random.random() < indpb:
            return not ind[N]
        return ind[N]
    return mutator


def IntMutate(bounds):
    def mutator(ind, N, gen, ngen, indpb):
        if random.random() < 0.5:
            return ind[N] + min(bounds[1]-ind[N], 1)
        return ind[N] - min(ind[N]-bounds[0], 1)
    return mutator


def FloatMutate(bounds):
    def mutator(ind, N, gen, ngen, indpb):
        if random.random() < 0.5:
            return ind[N] + (bounds[1] - ind[N]) * random.random() * (1 - gen / ngen)
        return ind[N] - (ind[N] - bounds[0]) * random.random() * (1 - gen / ngen)
    return mutator


def Mutator(g, bounds):
    if type(g) is bool:
        return BoolMutate(bounds)
    elif type(g) is int:
        return IntMutate(bounds)
    elif type(g) is float:
        return FloatMutate(bounds)
    else:
        raise TypeError("Prototype genes must be float, int or boolean.")


# Population class with methods for generate, mate, mutate
class Population(object):
    def __init__(self, prototype, gene_bounds, fitness_func):
        self.individuals = []
        self.prototype = prototype
        self.indsize = len(prototype)
        if gene_bounds:
            if len(gene_bounds) != len(prototype):
                raise ValueError("len(prototype) != len(bounds)")
            else:
                self.bounds = gene_bounds
        else:
            self.bounds = [None for _ in range(self.indsize)]
        self.fitness = fitness_func
        self.typecode = typecodes[type(prototype[0])] if len(set([type(g) for g in prototype])) == 1 else None
        self.generators = [Generator(g, self.bounds[N]) for N, g in enumerate(prototype)]
        self.maters = [Mater(g) for g in prototype]
        self.mutators = [Mutator(g, self.bounds[N]) for N, g in enumerate(prototype)]
        self.best = None

    def generator(self):
        return [self.generators[N]() for N in range(self.indsize)]

    def populate(self, popsize=300, base_population=None):
        if base_population:
            self.popsize = len(base_population)
            if self.typecode:
                self.individuals = [Individual(array(self.typecode, ind)) for ind in base_population]
            else:
                self.individuals = [Individual(list(ind)) for ind in base_population]
        else:
            self.popsize = popsize
            if self.typecode:
                self.individuals = [Individual(array(self.typecode, self.generator())) for _ in range(popsize)]
            else:
                self.individuals = [Individual(self.generator()) for _ in range(self.popsize)]
        self.evaluate()

    def mate(self, ind1, ind2):
        cutoff = random.randint(1, self.indsize-1)
        a = random.random()
        b = 1 - a
        for N in range(self.indsize):
            ind1[N], ind2[N] = self.maters[N](ind1, ind2, N, a, b, cutoff)
        del ind1.fitness
        del ind2.fitness

    def mutate(self, ind, gen, ngen, indpb):
        for N in range(self.indsize):
            ind[N] = self.mutators[N](ind, N, gen, ngen, indpb)

    def evaluate(self):
        for ind in self.individuals:
            if not ind.valid:
                ind.fitness = self.fitness(ind)
        # Also update the record of the best individual
        best = max(self.individuals, key=lambda ind: ind.fitness)
        if not self.best or best.fitness > self.best.fitness:
            self.best = best

    def __getitem__(self, key):
        return self.individuals[key]

    def __setitem__(self, key, value):
        self.individuals[key] = value

    def __len__(self):
        return len(self.individuals)

    def __iter__(self):
        return iter(self.individuals)

    def __copy__(self):
        new = Population(self.prototype, self.bounds, self.fitness)
        new.populate(base_population=[copy(ind) for ind in self.individuals])
        return new

    def evolve(self, ngen=40, matepb=0.3, mutpb=0.2, indpb=0.05, verbose=True):
        for gen in range(ngen):
            self.individuals = Select(self)
            for ind1, ind2 in zip(self[::2], self[1::2]):
                if random.random() < matepb:
                    self.mate(ind1, ind2)
                if random.random() < mutpb:
                    self.mutate(ind1, gen, ngen, indpb)
                if random.random() < mutpb:
                    self.mutate(ind2, gen, ngen, indpb)
            self.evaluate()

            if verbose:
                fits = [ind.fitness for ind in self]
                mean = float(sum(fits)) / len(fits)
                sqdev = [(f - mean) ** 2 for f in fits]
                print("--- Generation {} ---".format(gen))
                print("    Fitest: {} --- Variance: {} ".format(max(fits), sum(sqdev) / len(sqdev)))

    def step(self, ngen=40, gen=0, matepb=0.3, mutpb=0.2, indpb=0.05, verbose=True):
        """ This evolves the population exactly one generation, and passes the gen/ngen
            parameters to any functions that require it. """
        self.individuals = Select(self)
        for ind1, ind2 in zip(self[::2], self[1::2]):
            if random.random() < matepb:
                self.mate(ind1, ind2)
            if random.random() < mutpb:
                self.mutate(ind1, gen, ngen, indpb)
            if random.random() < mutpb:
                self.mutate(ind2, gen, ngen, indpb)
        self.evaluate()

        if verbose:
            fits = [ind.fitness for ind in self]
            mean = float(sum(fits)) / len(fits)
            sqdev = [(f - mean) ** 2 for f in fits]
            print("    Fitest: {} --- Variance: {} ".format(max(fits), sum(sqdev) / len(sqdev)))


# Select best individuals
def Select(pop, tournsize=3, newsize=None):
    if newsize is None:
        newsize = len(pop)
    return [
        copy(max(random.sample(list(pop), tournsize), key=lambda ind: ind.fitness))
        for _ in range(newsize)
    ]
