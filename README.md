# Python-TinyEvolver
### A simple, tiny engine for creating genetic algorithms

TinyEvolver is a framework for creating genetic algorithms written in pure python.
It aims to let you write sensible evolutionary algorithms in as few steps as possible
using a prototype system to extrapolate generation, mutation and mating of individuals
from a simple example.

TinyEvolver was developed for scientists and researchers who want to utilize genetic
algorithms in models and applications, but not necessarily become researchers in
genetic/evolutionary algorithms themselves. You define the things that are really
unique to your problem and TinyEvolver does the rest.

The source code for TinyEvolver is inspired, at least in part, by the DEAP module, but
we've made conscious decisions to tailor our module towards simplicity and lightness.
But simple doesn't mean featureless - individuals can have genes of mixed type, populations
can be generated on the fly or from old data, and one can evolve many populations at
once with multiprocessing. 

## Installation

## Example
```python
from tinyevolver.core import Population, Evolve

prototype = [False for _ in range(100)]
p = Population(prototype=prototype, gene_bounds=None, fitness_func=sum)

p.populate()
Evolve(p)

print p.best.genes
```

## Documentation
TinyEvolve contains 3 classes: Individual, Population and IslandModel. A Population is a collection of Individuals and an IslandModel is a collection of Populations - both of these classes have methods for evolving.

### Individual
Users should not need to create an instance of this class directly.

Attributes: 
- `individual.genes` a 1D-array or flat list of genes.
- `individual.fitness` the individual's fitness - may or may not be present.
- `individual.valid` is True only if `individual.fitness` is present. 

Methods:
- Individuals have many of the methods of lists: you can get/set their genes with indices or slices, iterate over them, put them into `len`, copy them, and put them into any other Python function requiring only these.

### Population
Create an instance with `Population(prototype, gene_bounds, fitness_func)`, where
- `prototype` is a flat list of booleans, integers and floats whose types individuals' genes should have (namely boolean, float or integer).
- `gene_bounds` is either None or a list of lower/upper bounds for the genes.
- `fitness_func` takes a flat list of genes and returns a numeric value representing the individual's fitness.

Attributes:
- `population.best` the individual with the highest fitness.
- `population.individuals` the full list of individuals in the population.

Methods:
- Populations have many of the methods of lists: you can get/set their individuals with indices or slices, iterate over them, put them into `len`, copy them, or put them into any other Python function requiring only these.
- `population.populate([popsize, base_population])` if no `base_population` is passed then this will generate the required number of individuals for the population using its `prototype` and `gene_bounds`. If a family of list-like objects is passed as a `base_population` then the population is populated with these instead.
- `population.evolve([ngen, matepb, mutpb, indpb, verbose])` this should only be called after the class has been populated. It evolves `ngen` generations, where individuals have a probability `matepb` of mating, `mutpb` of mutating. `indpb` controlls the variability of an individual's genes upon mutation. Set `verbose` to False to avoid printing details of the evolution.

### IslandModel
Create an IslandModel instance with `IslandModel(poplist)` where `poplist` is a list of `Population` objects.

Attributes:
- `islandmodel.best` the best individual from all the individual populations
- `islandmodel.islands` a list containg the class' populations

Methods:
- `islandmodel.amalg_pop()` this returns the islands amalgamated into a single large population
- `islandmodel.select_pop()` this selects a population from across the islands whose size is that of a single island
- `islandmodel.evolve([ngen, matepb, mutpb, indpb, verbose, mig_freq])` this evolves all the islands, with individuals migrating between islands every `mig_freq` generations. See the `evolve` method for the `Population` class.
- `islandmodel.multi_evolve([ngen, matepb, mutpb, indpb, verbose, mig_freq])` this is the same as the evolve method, but uses multiprocessing
