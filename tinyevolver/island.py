from __future__ import print_function
from copy import copy
import random

from core import Population, Select, Step
from multiprocessing import Pipe, Process, Queue
from collections import deque


def Migrate(poplist, num_migrants):
    """ Migrates individuals between populations in poplist. """
    popsize = poplist[0].popsize

    for n in range(len(poplist)):
        migrant_indices = random.sample(range(popsize), num_migrants)
        for i in migrant_indices:
            poplist[n][i], poplist[n-1][i] = poplist[n-1][i], poplist[n][i]


def MigratePipe(island, num_migrants, pipe_in, pipe_out):
    """ This implements the migrate function along pipes in a multiprocessing setup. """
    migrant_indices = random.sample(range(island.popsize), num_migrants)
    emigrants = [copy(island[n]) for n in migrant_indices]

    pipe_out.send(emigrants)
    buf = pipe_in.recv()

    for n, immigrant in zip(migrant_indices, buf):
        island[n] = immigrant


class IslandModel(object):
    """ A class which takes a list of Population objects and returns
        methods for simultaneously evolving / cross-pollinating them.
        The kind of individual must be homogeneous accross islands:
        that is, they are required to have the same number of genes
        and the N-th gene of an individual on one island must have the
        same Type as the N-th gene of an individual on a different
        island.
        This is useful for periodically introducting 'fresh blood'
        into a saved population - preventing what might be an
        evolutionary cul-de-sac. """

    def __init__(self, poplist):
        if len(poplist) < 2:
            raise ValueError("At least two populations required for this model")
        else:
            self.islands = poplist
            self.num_islands = len(poplist)

    @property
    def best(self):
        candidates = [p.best for p in self.islands]
        return max(candidates, key=lambda ind: ind.fitness)

    def select_pop(self, tournsize=3):
        """ This selects a single output population (of the corect size)
            from all of the islands as a whole. This is good for e.g.
            saving a single population for future use. """
        proto_pop = self.islands[0]
        out_pop = Population(proto_pop.prototype, proto_pop.bounds, proto_pop.fitness)

        # Select the individuals for the output
        individuals = []
        for pop in self.islands:
            individuals += [copy(ind) for ind in pop.individuals]
        out_pop.populate(base_population=Select(individuals, tournsize, newsize=len(proto_pop)))

        return out_pop

    def amalg_pop(self):
        """ This amalgamates all the islands into one very large population
            and reutrns it. """
        proto_pop = self.islands[0]
        out_pop = Population(proto_pop.prototype, proto_pop.bounds, proto_pop.fitness)

        individuals = []
        for pop in self.islands:
            individuals += [copy(ind) for ind in pop.individuals]
        out_pop.populate(individuals)

        return out_pop

    def evolve(self, ngen=40, matepb=0.3, mutpb=0.2, indpb=0.05, verbose=True, mig_freq=5):
        """ This evolves the islands and periodically cross-pollinates them. """
        for gen in range(ngen):
            if verbose:
                print("--- Generation {} ---".format(gen))
            for pop in self.islands:
                Step(pop, ngen, gen, matepb, mutpb, indpb, verbose)
            if gen % mig_freq == 0:
                Migrate(self.islands, mig_freq)

    def _multi_evolve(self, pop, ngen, matepb, mutpb, indpb, verbose, mig_freq,
                      proc_no, pipe_in, pipe_out, result_queue):
        # Evolves and periodically puts/gets migrants from pipes

        for gen in range(ngen):
            if verbose:
                print("--- Island {}: ".format(proc_no))
            Step(pop, ngen, gen, matepb, mutpb, indpb, verbose)
            if gen % mig_freq == 0:
                MigratePipe(pop, mig_freq, pipe_in, pipe_out)

        if verbose:
            print("Evolution done: returning population to queue.")
        result_queue.put({'pop': list(pop), 'best': pop.best})

    def multi_evolve(self, ngen=40, matepb=0.3, mutpb=0.2, indpb=0.05, verbose=True, mig_freq=5):
        """ This is a multiprocessing version of the evolve method, assigning each island its
            own process. If running on Windows this needs to be called from inside a "__main__"
            function. Even on 'nix it might not work in the interactive interpreter. """
        pipes = [Pipe(False) for _ in range(self.num_islands)]
        pipes_in = deque(pipe[0] for pipe in pipes)
        pipes_out = deque(pipe[1] for pipe in pipes)
        pipes_in.rotate(1)
        pipes_out.rotate(-1)

        q = Queue()

        processes = [
            Process(
                target=self._multi_evolve,
                args=(self.islands[i], ngen, matepb, mutpb, indpb, verbose, mig_freq, i, pipe_in, pipe_out, q)
            )
            for i, (pipe_in, pipe_out) in enumerate(zip(pipes_in, pipes_out))
        ]

        for proc in processes:
            proc.start()

        new_pops = [q.get() for proc in processes]

        for proc in processes:
            proc.join()

        for N, island in enumerate(self.islands):
            island.individuals = new_pops[N]['pop']
            island.best = new_pops[N]['best']