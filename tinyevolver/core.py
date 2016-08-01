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
from __future__ import print_function, division
try:
    from itertools import izip
except ImportError:
    izip = zip
    xrange = range

from array import array
from copy import copy
import random


class Individual(object):
    """
    An 'indivudal' class. Behaves like/is initialised with an array/list
    of genes, but also contains a fitness and a 'valid' attribute: which
    indicates whether the current fitness applies to the current genes.
    """

    __slots__ = ["genes", "fitness", "valid"]

    def __init__(self, gene_list):
        self.genes = gene_list
        self.fitness = None
        self.valid = False

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
            new.valid = True
        return new


# Generators for individual genes
def generator(gene_type, bounds):
    if gene_type is bool:
        return bool(random.getrandbits(1))
    elif gene_type is int:
        return random.randint(*bounds)
    elif gene_type is float:
        return random.uniform(*bounds)

    raise TypeError("Prototype genes must be float, int or boolean.")


# Helper function for generating arrays
def typecode(gene):
    if type(gene) is bool:
        return 'b'
    elif type(gene) is int:
        return 'i'
    elif type(gene) is float:
        return 'd'

    raise TypeError("Prototype genes must be float, int or boolean.")


# Mating functions - gene by gene
def bool_mate(gene1, gene2, n, cutoff):
    if n <= cutoff:
        return gene2, gene1
    return gene1, gene2


def int_mate(gene1, gene2, n, cutoff):
    if n <= cutoff:
        return gene2, gene1
    return gene1, gene2


def float_mate(gene1, gene2, a, b):
    return a * gene1 + b * gene2, b * gene1 + a * gene2


# Mutating functions - gene by gene
def bool_mutator(gene, indpb):
    if random.random() < indpb:
        return not gene
    return gene


def int_mutator(gene, bounds):
    naive = int(gene + random.normalvariate(0, 1))
    return max(min(naive, bounds[1]), bounds[0])


def float_mutator(gene, bounds, gen, ngen, scoping):
    if random.random() < 0.5:
        return gene + (bounds[1] - gene) * random.random() * (1 - gen / ngen) ** scoping
    return gene - (gene - bounds[0]) * random.random() * (1 - gen / ngen) ** scoping


# Population class with methods for generate, mate, mutate
class Population(object):
    """
    Population to contain Indivuduals and methods for evolution.
    :param prototype: A flat list of float, integer or boolean genes.
    :param gene_bounds: A list of pairs (l, u) of bounds for the selection/mutation
        of genes
    :param fitness_func: A function which takes a flat list of genes and returns an
        fitness value (key) with which to order individuals. Individuals with HIGHER
        fitness will be selected over those with lower fitness.

    Methods:
        populate - add Individuals to this class
        evolve - evolve the individuals using the generated select, mate, mutate functions
    Attributes:
        individuals - a list of Individual instances
        best - the fittest individual of all time
    """

    def __init__(self, prototype, gene_bounds, fitness_func):
        self.individuals = []
        self.popsize = 0
        self._prototype = prototype
        self._typelist = list(map(type, prototype))
        self._typeset = set(self._typelist)
        self._indsize = len(prototype)
        self._fitness = fitness_func
        self.best = None

        if gene_bounds is None:
            self._bounds = [(-1, 1) for _ in xrange(self._indsize)]
        else:
            if len(gene_bounds) != len(prototype):
                raise AttributeError("len(prototype) != len(bounds)")
            self._bounds = gene_bounds

        if len(self._typeset) == 1:
            self._typecode = typecode(prototype[0])
        else:
            self._typecode = None

    def _generator(self):
        return [generator(type(g), bounds) for g, bounds in
                izip(self._prototype, self._bounds)]

    def populate(self, popsize=300, base_population=None):
        """
        Add Individuals to the population.
        :param base_population: if not None, the popsize variable will be
            ignored and members of this object used as individuals. This
            should be a Population or a list of iterables containing genes.
        :param popsize: if base_population is None, then this is the number
            of Individuals that will be generated ab initio for the
            Population.
        """
        if base_population:
            self.popsize = len(base_population)
            if self._typecode is not None:
                self.individuals = [Individual(array(self._typecode, ind))
                                    for ind in base_population]
            else:
                self.individuals = [Individual(list(ind)) for ind in base_population]

        else:
            self.popsize = popsize
            if self._typecode:
                self.individuals = [Individual(array(self._typecode, self._generator()))
                                    for _ in xrange(popsize)]
            else:
                self.individuals = [Individual(self._generator()) for _ in
                                    xrange(self.popsize)]

        self._evaluate()

    def _mate(self, ind1, ind2):
        cutoff = random.randint(1, self._indsize - 1)
        a = random.random()
        b = 1 - a
        for n, (gene1, gene2, genetype) in enumerate(izip(ind1, ind2, self._typelist)):
            if genetype is float:
                ind1[n], ind2[n] = float_mate(gene1, gene2, a, b)
            elif genetype is int:
                ind1[n], ind2[n] = int_mate(gene1, gene2, n, cutoff)
            elif genetype is bool:
                ind1[n], ind2[n] = bool_mate(gene1, gene2, n, cutoff)

    def _mutate(self, ind, gen, ngen, indpb, scoping):
        for n, (gene, genetype) in enumerate(izip(ind, self._typelist)):
            if genetype is float:
                ind[n] = float_mutator(gene, self._bounds[n], gen, ngen, scoping)
            elif genetype is int:
                ind[n] = int_mutator(gene, self._bounds[n])
            elif genetype is bool:
                ind[n] = bool_mutator(gene, indpb)

    def _evaluate(self):
        for ind in self.individuals:
            if not ind.valid:
                ind.fitness, ind.valid = self._fitness(ind), True

        # Also update the record of the best individual
        best = max(self.individuals, key=lambda ind: ind.fitness)
        if self.best is None or best.fitness > self.best.fitness:
            self.best = copy(best)

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

    def evolve(self, ngen=40, matepb=0.3, mutpb=0.2, indpb=0.05,
               scoping=0, tournsize=3, verbose=True):
        """
        Evolve the population in place
        :param ngen: Positive integer - number of generations to evolve
        :param matepb: Float between 0 and 1 - probability of individual mating
        :param mutpb: Float between 0 and 1 - probability of individual mutation
        :param indpb: Float between 0 and 1 - probability of individual boolean
            genes flipping. Has no effect for other types of genes.
        :param scoping:  Float non-negative - decrease in variability of genes as
            time goes on. Has no effect for other types of genes.
        :param tournsize: Positive integer - size of random pools to select best
            individuals from for next generation.
        :param verbose: Boolean - print statistics to screen (this may slow the evolution)
        """
        for gen in xrange(ngen):
            self.individuals = select(self, tournsize=tournsize)
            for ind1, ind2 in izip(self[::2], self[1::2]):
                if random.random() < matepb:
                    self._mate(ind1, ind2)
                    ind1.valid = False
                    ind2.valid = False
                if random.random() < mutpb:
                    self._mutate(ind1, gen, ngen, indpb, scoping)
                    ind1.valid = False
                if random.random() < mutpb:
                    self._mutate(ind2, gen, ngen, indpb, scoping)
                    ind2.valid = False
            self._evaluate()

            if verbose:
                fits = [ind.fitness for ind in self]
                mean = sum(fits) / len(fits)
                sqdev = [(f - mean) ** 2 for f in fits]
                print("--- Generation %d ---" % gen)
                print(
                    "    Fitest: %f --- Variance: %f " %
                    (max(fits), sum(sqdev) / len(sqdev))
                )

    def step(self, ngen=40, gen=0, matepb=0.3, mutpb=0.2, indpb=0.05,
             scoping=0, tournsize=3, verbose=True):
        """
        This is similar to the 'evolve' method, but evolves the population exactly one
        generation. The ngen and gen parameters are required for scoping
        (see Population.evolve for further details).
        """

        self.individuals = select(self, tournsize=tournsize)
        for ind1, ind2 in izip(self[::2], self[1::2]):
            if random.random() < matepb:
                self._mate(ind1, ind2)
                ind1.valid = False
                ind2.valid = False
            if random.random() < mutpb:
                self._mutate(ind1, gen, ngen, indpb, scoping)
                ind1.valid = False
            if random.random() < mutpb:
                self._mutate(ind2, gen, ngen, indpb, scoping)
                ind2.valid = False
        self._evaluate()

        if verbose:
            fits = [ind.fitness for ind in self]
            mean = float(sum(fits)) / len(fits)
            sqdev = [(f - mean) ** 2 for f in fits]
            print(
                "    Fitest: %f --- Variance: %f" % (max(fits), sum(sqdev) / len(sqdev))
            )


# Select best individuals
# Defined separately for use with Island class
def select(pop, tournsize=3, newsize=None):
    if newsize is None:
        newsize = len(pop)
    return [
        copy(max(random.sample(list(pop), tournsize), key=lambda ind: ind.fitness))
        for _ in xrange(newsize)
    ]
