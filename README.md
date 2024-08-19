# ListConditionalIndependencies
Implementation of the algorithm for listing all conditional independencies implied by a causal model.

## How to install

Please run the following commands to install the package:

```
pip install -r requirements.txt
pip install -e .
```

## How to run

To run some examples, try running the following command:

```
python3 main.py clmp graphs/paper/fig5a.txt
```

## Arguments

1. First argument: `gmp`, `lmp`, or `clmp`.
- `gmp`: The global Markov property (runs the algorithm ListGMP)
- `lmp`: The ordered local Markov property (runs the algorithm ListCIBF)
- `clmp`: The c-component local Markov property (runs the algorithm ListCI)

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

There are two scripts to run experiments:
- `experiment_graph.py`: Parses a text file containing graph information, constructs a graph, and run experiments.

To run some examples, try running the following command:

```
python3 experiment_graph.py graphs/paper/fig1b.txt
```

## Arguments

1. First argument: `graphs/paper/fig1b.txt`. The path to a text or BIF file.

The supported algorithms are: [`gmp`, `lmp`, `clmp`]. By default, two algorithms [`lmp`, `clmp`] will run, but you may modify the `algorithms` variable in `experiment_graph.py` to change the sets of algorithms to run.