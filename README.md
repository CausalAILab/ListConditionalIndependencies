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

To run some examples, try running the following commands:

```
python3 main.py lmp graphs/paper/fig1b.txt
```

1. First argument: `gmp` or `lmp`. `gmp` lists all conditional independencies invoked by the global Markov property. 'lmp' lists all conditional independencies invoked by the ordered local Markov property.
2. Second argument: `graphs/paper/fig1b.txt`. the path to a file that contains all necessary information, such as graph, query, and constraints (i.e., `I` and `R`). Please check the formatting for details.

## Formatting of the input file

Consider `graphs/paper/fig1b.txt` as an example.

*&#60;NODES&#62;*

Each line represents the name of a variable/node (e.g., `A` and `E`).

*&#60;EDGES&#62;*

Each line describes an edge. Two types of edges are supported:

1. Directed edge: `A -> E` represents a directed edge from `A` to `E`.
2. Bidirected edge: `E -- F` means there exists some unmeasured confounder (i.e., latent variable) between `E` and `F`.