""" This is part of Python TinyEvolver Copyright (C) 2015 Oliver Margetts

    This script is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

from array import array
from copy import copy
import random


class Individual(object):
    """ An 'indivudal' class. Behaves like/is initialised with an array/list of genes,
        but also contains methods for setting/getting/deleting fitness. """
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
    def mutator(ind, N, gen, ngen, indpb, scoping):
        if random.random() < indpb:
            return not ind[N]
        return ind[N]
    return mutator


def IntMutate(bounds):
    def mutator(ind, N, gen, ngen, indpb, scoping):
        naive = int(ind[N] + random.normalvariate(0, 1))
        return max(min(naive, bounds[1]), bounds[0])
    return mutator


def FloatMutate(bounds):
    def mutator(ind, N, gen, ngen, indpb, scoping):
        if random.random() < 0.5:
            return ind[N] + (bounds[1] - ind[N]) * random.random() * (1 - gen / ngen) ** scoping
        return ind[N] - (ind[N] - bounds[0]) * random.random() * (1 - gen / ngen) ** scoping
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
    """ Population to contain Indivuduals and methods for evolution.
        Arguments:
            prototype - a flat list of float, integer or boolean genes
            bounds - a list of pairs (l, u) of bounds for the selection/mutation of genes
            fitness_func - a function which takes a flat list of genes and returns a numeric fitness value
        Methods:
            populate - add Individuals to this class
            evolve - evolve the individuals using the generated select, mate, mutate functions
        Attributes:
            individuals - a list of Individual instances
            best - the fittest individual of all time
    """
            
    def __init__(self, prototype, gene_bounds, fitness_func):
        self.individuals = []
        self._prototype = prototype
        self._indsize = len(prototype)
        if gene_bounds:
            if len(gene_bounds) != len(prototype):
                raise ValueError("len(prototype) != len(bounds)")
            else:
                self._bounds = gene_bounds
        else:
            self._bounds = [None for _ in range(self._indsize)]
        self._fitness = fitness_func
        self._typecode = typecodes[type(prototype[0])] if len(set([type(g) for g in prototype])) == 1 else None
        self._generators = [Generator(g, self._bounds[N]) for N, g in enumerate(prototype)]
        self._maters = [Mater(g) for g in prototype]
        self._mutators = [Mutator(g, self._bounds[N]) for N, g in enumerate(prototype)]
        self.best = None

    def _generator(self):
        return [self._generators[N]() for N in range(self._indsize)]

    def populate(self, popsize=300, base_population=None):
        """ Add Individuals to the population.
            Arguments:
                base_population - if not null, the popsize variable will be ignored and members of this object used as individuals. This should be a Population or a list of items able to be coerced to Individuals.
                popsize - if base_population is null, then this is the number of Individuals that will be generated ab initio for the Population.
        """        
        if base_population:
            self.popsize = len(base_population)
            if self._typecode:
                self.individuals = [Individual(array(self._typecode, ind)) for ind in base_population]
            else:
                self.individuals = [Individual(list(ind)) for ind in base_population]
        else:
            self.popsize = popsize
            if self._typecode:
                self.individuals = [Individual(array(self._typecode, self._generator())) for _ in range(popsize)]
            else:
                self.individuals = [Individual(self._generator()) for _ in range(self.popsize)]
        self._evaluate()

    def _mate(self, ind1, ind2):
        cutoff = random.randint(1, self._indsize-1)
        a = random.random()
        b = 1 - a
        for N in range(self._indsize):
            ind1[N], ind2[N] = self._maters[N](ind1, ind2, N, a, b, cutoff)
        del ind1.fitness
        del ind2.fitness

    def _mutate(self, ind, gen, ngen, indpb, scoping):
        for N in range(self._indsize):
            ind[N] = self._mutators[N](ind, N, gen, ngen, indpb, scoping)

    def _evaluate(self):
        for ind in self.individuals:
            if not ind.valid:
                ind.fitness = self._fitness(ind)
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
        new = Population(self._prototype, self._bounds, self._fitness)
        new.populate(base_population=[copy(ind) for ind in self.individuals])
        return new

    def evolve(self, ngen=40, matepb=0.3, mutpb=0.2, indpb=0.05, scoping=0, tournsize=3, verbose=True):
        """ Evolve the population in place
            Arguments:
                ngen - Positive integer - number of generations to evolve
                matepb - Float between 0 and 1 - probability of individual mating
                mutpb - Float between 0 and 1 - probability of individual mutation
                indpb - Float between 0 and 1 - probability of individual boolean genes flipping
                scoping - Float non-negative - more positive means a greater decrease in variability of genes as time goes on
                tournsize - Positive integer - size of random pools to select best individuals from
                verbose - Boolean - print statistics to screen (note: this may slow the evolution)
        """
        for gen in range(ngen):
            self.individuals = Select(self, tournsize=tournsize)
            for ind1, ind2 in zip(self[::2], self[1::2]):
                if random.random() < matepb:
                    self._mate(ind1, ind2)
                    del ind1.fitness
                    del ind2.fitness
                if random.random() < mutpb:
                    self._mutate(ind1, gen, ngen, indpb, scoping)
                    del ind1.fitness
                if random.random() < mutpb:
                    self._mutate(ind2, gen, ngen, indpb, scoping)
                    del ind2.fitness
            self._evaluate()

            if verbose:
                fits = [ind.fitness for ind in self]
                mean = float(sum(fits)) / len(fits)
                sqdev = [(f - mean) ** 2 for f in fits]
                print("--- Generation %d ---" % gen)
                print("    Fitest: %f --- Variance: %f " % (max(fits), sum(sqdev) / len(sqdev)))

    def step(self, ngen=40, gen=0, matepb=0.3, mutpb=0.2, indpb=0.05, scoping=0, tournsize=3, verbose=True):
        """ This is similar to the 'evolve' method, but evolves the population exactly one generation. 
            The ngen and gen parameters are required for scoping (see Population.evolve). """
        self.individuals = Select(self, tournsize=tournsize)
        for ind1, ind2 in zip(self[::2], self[1::2]):
            if random.random() < matepb:
                self._mate(ind1, ind2)
                del ind1.fitness
                del ind2.fitness
            if random.random() < mutpb:
                self._mutate(ind1, gen, ngen, indpb, scoping)
                del ind1.fitness
            if random.random() < mutpb:
                self._mutate(ind2, gen, ngen, indpb, scoping)
                del ind2.fitness
        self._evaluate()

        if verbose:
            fits = [ind.fitness for ind in self]
            mean = float(sum(fits)) / len(fits)
            sqdev = [(f - mean) ** 2 for f in fits]
            print("    Fitest: %f --- Variance: %f" % (max(fits), sum(sqdev) / len(sqdev)))


# Select best individuals
def Select(pop, tournsize=3, newsize=None):
    if newsize is None:
        newsize = len(pop)
    return [
        copy(max(random.sample(list(pop), tournsize), key=lambda ind: ind.fitness))
        for _ in range(newsize)
    ]
