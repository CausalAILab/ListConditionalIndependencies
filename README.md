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
python3 main.py graphs/list1.txt
```

1. First argument: `graphs/list1.txt`. the path to a file that contains all necessary information, such as graph. Please check the formatting for details.

## Formatting of the input file

Consider `graphs/list1.txt` as an example.

*&#60;NODES&#62;*

Each line represents the name of a variable/node (e.g., `A` and `B`).

*&#60;EDGES&#62;*

Each line describes an edge. Two types of edges are supported:

1. Directed edge: `A -> B` represents a directed edge from `A` to `B`.
2. Bidirected edge: `u -- H` means there exists some unmeasured confounder (i.e., latent variable) between `u` and `H`.