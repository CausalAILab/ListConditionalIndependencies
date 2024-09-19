# ListConditionalIndependencies

This repository contains the implementation for the paper ["Testing Causal Models with Hidden Variables in Polynomial Delay via Conditional Independencies"](https://causalai.net/r117.pdf) by Hyunchai Jeong\*, Adiba Ejaz\*, Jin Tian, and Elias Bareinboim. More specifically, the algorithms for listing all conditional independence relations (CIs) implied by a causal model.
\* These authors contributed equally.

## How to install

Please run the following commands to install the package:

```
git clone https://github.com/CausalAILab/ListConditionalIndependencies.git
cd ListConditionalIndependencies
pip3 install -r requirements.txt
pip3 install -e .
```

## How to run a listing algorithm

To run some examples, try running the following command:

```
python3 main.py clmp graphs/paper/fig4b.txt
```

### Arguments

1. First argument: `gmp`, `lmp`, or `clmp`. Specifies a listing algorithm that outputs all CIs invoked by the following property.
- `gmp`: The global Markov property (runs the algorithm ListGMP)
- `lmp`: The ordered local Markov property (runs the algorithm ListCIBF)
- `clmp`: The c-component local Markov property (runs the algorithm ListCI)

2. Second argument: `graphs/paper/fig4b.txt`. The path to a text file that contains graph information, such as nodes and edges of a graph. Please check the formatting for details.

### Format of the graph file

Consider `graphs/paper/fig4b.txt` as an example.

*&#60;NODES&#62;*

Each line represents the name of a variable/node (e.g., `A` and `B`).

*&#60;EDGES&#62;*

Each line describes an edge. Two types of edges are supported:

1. Directed edge: `A -> B` represents a directed edge from `A` to `B`.
2. Bidirected edge: `A -- F` means there exists some unmeasured confounder (i.e., latent variable) between `A` and `F`.


## How to test a model against observational data

Try running the following command:

```
python3 test_model.py graphs/sachs/graph_gt.txt datasets/sachs/dataset.csv
```

The example tests a ground-truth graph provided by experts (11 nodes and 17 edges) against a real-world protein signaling dataset (853 samples) by (Sachs et al. 2005). The details are provided in Appendix F.2 in the paper.

### Arguments

1. First argument: `graphs/sachs/graph_gt.txt`. The path to a graph file.
2. Second argument: `datasets/sachs/dataset.csv`. The path to a dataset file.

## How to run experiments

We consider experiments shown in Appendix F.1 and F.3.

1. Appendix F.1: Comparison of ListCI and two other algorithms - ListGMP and ListCIBF.
    - Running bnlearn instances (with varying projection levels) over three algorithms. The original bnlearn instances are available [here](https://www.bnlearn.com/bnrepository/).

    Try running the following command:

    ```
    python3 run_bnlearn_graph.py clmp graphs/bnlearn/sm/asia.txt
    ```

    When the experiment finishes, a report file named `bnlearn_report_asia_clmp.csv` will be generated. Please check the heading **Parameters of a report file** for more details.

    ### Arguments

    1. First argument: `gmp`, `lmp`, or `clmp`. An algorithm to run.
    2. Second argument: `graphs/bnlearn/sm/asia.txt`. The path to a bnlearn graph file.

    ### Graphs

    All bnlearn graphs are placed in the directory `graphs/bnlearn`. There are three types of graphs, classified based on `n`: number of nodes.

    * Small graphs, `n`: [1,20)

        Placed in `graphs/bnlearn/sm` subdirectory.

    * Medium graphs, `n`: [21,50)

        Placed in `graphs/bnlearn/md` subdirectory.

    * Large graphs, `n`: [51,100)

        Placed in `graphs/bnlearn/lg` subdirectory.

    ### Parameters of a report file

    Measured parameters for all three algorithms.
    * `n`: number of nodes.
    * `m`: number of edges.
    * `md`: number of directed edges.
    * `mu`: number of bidirected edges.
    * `# CI`: number of CIs invoked by a Markov property.
    * `runtime:` running time of an algorithm in seconds (rounded to the nearest second).

    Two additional paramters are measured for ListCIBF.
    * `# S`: number of ancestral sets.
    * `# S+`: number of maximal ancestral sets (MASs).

    One additional paramter is measured for both ListCIBF and ListCI.
    * `s`: size of the largest c-component.

    ### Experiment configuration

    The following parameter may be modified in `run_bnlearn_graph.py` to change experiment settings.

    * `numBatches`: number of batches to run for an experiment. For each single batch, 10 random graphs are generated in total: one graph for each projection level `U` (for `U = 0, 10, ..., 90`). Default is set to `10`, totalling 100 sample graphs. Located at line 355 of `run_bnlearn_graph.py`.
    * `fixOrdering`: If set to `True`, a topological order over variables will be fixed (across all projections) for more consistent results. Default is `True`.
    * `randomSeed`: A random seed to be provided to `random.random()`. Default is `None`.

2. Appendix F.3: Analysis of C-LMP
    - Running experiments over random graphs to understand the total number of valid CIs invoked by C-LMP.

    Try running the following command:

    ```
    python3 run_case.py 1a
    ```

    A report file named `report_case_1a.csv` will be generated.

    ### Arguments

    1. First argument: Any one string from the list `['1a', '1b', '1v', '1r', '2a', '2b', '3a']`.
    - Case 1
        * `1a`: Experiments corresponding to plots shown in Fig. F.3.1.
        * `1v`, `1r`: Fig. F.3.2a and Fig. F.3.2b, respectively.
        * `1b`: Fig. F.3.3.
    - Case 2
        * `2a`: Fig. F.3.4.
        * `2b`: Fig. F.3.5.
    - Case 3
        * `3a`: Fig. F.3.6.
    
    ### Experiment configuration

    The following parameters may be modified to change experiment settings. The mentioned variables are defined below the line: `if __name__ == '__main__':`.

    * `n`: number of nodes.
    * `numBatches`: number of batches to run for an experiment. For each single batch, 10 random graphs are generated. Default is set to `10`, totalling 100 sample graphs.
    * `randomSeed`: A random seed to be provided to `random.random()`. Default is `None`.

## References

- Scutari, M. 2010. Learning Bayesian Networks with the bnlearn R Package. Journal of Statistical Software, 35(3): 1–22.
- Sachs, K.; Perez, O.; Pe’er, D.; Lauffenburger, D. A.; and Nolan, G. P. 2005. Causal protein-signaling networks derived from multiparameter single-cell data. Science, 308(5721): 523–529.