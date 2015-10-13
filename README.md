# Python-TinyEvolver
### A simple, tiny engine for creating genetic algorithms

TinyEvolver is a framework for creating genetic algorithms written in pure python.
It aims to let you write sensible evolutionary algorithms in as few steps as possible
using a prototype system to extrapolate generation, mutation and mating of individuals
from a simple example.

TinyEvolver was developed for scientists and researchers who want to utilize genetic
algorithms in models and applications, but not necessarily become researchers in
genetic/evolutionary algorithms themselves. You define the things that are really
unique to your problem and TinyEvolve does the rest.

The source code for TinyEvolve is inspired, at least in part, by the Deap module, but
we've made conscious decisions to tailor our module towards simplicity and lightness.
Simple doesn't mean featureless - individuals can have genes of mixed type, populations
can be generated on the fly or from old data, and one can evolve many populations at
once with multiprocessing. 
