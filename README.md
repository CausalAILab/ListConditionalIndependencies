# ListConditionalIndependencies
Implementation of the algorithm for listing all conditional independencies implied by a causal model.

## How to install

Please run the following commands to install the package:

```
git clone https://github.com/CausalAILab/ListConditionalIndependencies.git
cd ListConditionalIndependencies
pip install -r requirements.txt
pip install -e .
```

## How to run

To run some examples, try running the following command:

```
python3 main.py listci graphs/paper/fig1b.txt
```

## Arguments

1. First argument: `gmp`, `lmp`, `lmpp`, or `listci`.
- `gmp`: The global Markov property
- `lmp`: The ordered local Markov property
- `lmpp`: The augmented ordered local Markov property
- `listci`: The augmented ordered local Markov property (poly-delay)

2. Second argument: `graphs/paper/fig1b.txt`. The path to a text file that contains graph information, such as nodes and edges of a graph. Please check the formatting for details.

## Format of the graph file

Consider `graphs/paper/fig1b.txt` as an example.

*&#60;NODES&#62;*

Each line represents the name of a variable/node (e.g., `A` and `E`).

*&#60;EDGES&#62;*

Each line describes an edge. Two types of edges are supported:

1. Directed edge: `A -> E` represents a directed edge from `A` to `E`.
2. Bidirected edge: `E -- F` means there exists some unmeasured confounder (i.e., latent variable) between `E` and `F`.

## How to run experiments

There are two scripts that runs experiments:
- `experiment_graph.py`: Parses a text file containing graph information, constructs a graph, and run experiments.
- `experiment_bif.py`: Parses a BIF file (BIF stands for Bayesian Interchange Format), constructs a graph, and run experiments.

To run some examples, try running the following command:

```
python3 experiment_graph.py graphs/paper/fig1b.txt
```

or

```
python3 experiment_bif.py bif/sm/asia.bif
```

## Arguments

1. First argument: `graphs/paper/fig1b.txt` or `bif/sm/asia.bif`. The path to a text or BIF file.

The supported algorithms are: [`gmp`, `lmp`, `lmpp`, `listci`]. By default, two algorithms [`lmp`, `listci`] will run, but you may modify the `algorithms` variable in `experiment_graph.py` or `experiment_bif.py` to change the sets of algorithms to run.

## BIF format details

https://www.cs.washington.edu/dm/vfml/appendixes/bif.htm