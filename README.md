# ListConditionalIndependencies
Implementation of the algorithms for listing all conditional independencies implied by a causal model.

## How to install

Please run the following commands to install the package:

```
pip3 install -r requirements.txt
pip3 install -e .
```

## How to run a listing algorithm

To run some examples, try running the following command:

```
python3 main.py clmp graphs/paper/fig5a.txt
```

### Arguments

1. First argument: `gmp`, `lmp`, or `clmp`.
- `gmp`: The global Markov property (runs the algorithm ListGMP)
- `lmp`: The ordered local Markov property (runs the algorithm ListCIBF)
- `clmp`: The c-component local Markov property (runs the algorithm ListCI)

2. Second argument: `graphs/paper/fig5a.txt`. The path to a text file that contains graph information, such as nodes and edges of a graph. Please check the formatting for details.

### Format of the graph file

Consider `graphs/paper/fig1b.txt` as an example.

*&#60;NODES&#62;*

Each line represents the name of a variable/node (e.g., `A` and `E`).

*&#60;EDGES&#62;*

Each line describes an edge. Two types of edges are supported:

1. Directed edge: `A -> E` represents a directed edge from `A` to `E`.
2. Bidirected edge: `E -- F` means there exists some unmeasured confounder (i.e., latent variable) between `E` and `F`.


## How to test a model against observational data

Try running the following command:

```
python3 test_model.py graphs/sachs/graph_gt.txt datasets/sachs/dataset.csv
```

The example tests a ground-truth graph provided by experts (11 nodes and 17 edges) against a real-world protein signaling dataset (853 samples) by (Sachs et al. 2005).

### Arguments

1. First argument: `graphs/sachs/graph_gt.txt`. The path to a graph file.
2. Second argument: `datasets/sachs/dataset.csv`. The path to a dataset file.

## How to run experiments

The following scripts are used to run experiments shown in Appendix E.

1. Appendix E.1: Comparison of ListCI and two other algorithms - ListGMP and ListCIBF.
    - Running bnlearn instances (with varying projection levels) over three algorithms. The original bnlearn instances are available [here](https://www.bnlearn.com/bnrepository/).

    Try running the following command:

    ```
    python3 run_bnlearn_graph.py clmp graphs/bnlearn/sm/asia.txt
    ```

    When the experiment finishes, a report file named `bnlearn_report_asia_clmp.csv` will be generated.

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

2. Appendix E.2: Analysis of C-LMP
    - Running experiments over random graphs to understand the total number of valid CIs invoked by C-LMP.

    The following provides the list of scripts. The scripts take no argument. A report file will be generated once the experiment finishes.
    * run_case1.py
    * run_case1_mu.py
    * run_case1_invalid.py
    * run_case2.py
    * run_case2_mu.py
    * run_case3.py
    
    The list of commands goes as follows:

    ```
    python3 run_case1.py
    ```

    A report file named `case1_report.csv` will be generated.

    ```
    python3 run_case1_mu.py
    ```

    A report file named `case1_mu_report.csv` will be generated.

    ```
    python3 run_case1_invalid.py
    ```

    A report file named `case1_invalid_CIs_report.csv` will be generated.

    ```
    python3 run_case2.py
    ```

    A report file named `case2_report.csv` will be generated.

    ```
    python3 run_case2_mu.py
    ```

    A report file named `case2_mu_report.csv` will be generated.

    ```
    python3 run_case3.py
    ```

    A report file named `case3_report.csv` will be generated.

    ### Parameters of a report file

    * `n`: number of nodes.
    * `m`: number of edges.
    * `md`: number of directed edges.
    * `mu`: number of bidirected edges.
    * `# CI`: number of CIs invoked by a Markov property.
    * `runtime:` running time of an algorithm in seconds (rounded to the nearest second).
    * `s`: size of the largest c-component.
    * `# S`: number of ancestral sets.
    * `# S+`: number of maximal ancestral sets (MASs).

## References

- Scutari, M. 2010. Learning Bayesian Networks with the bnlearn R Package. Journal of Statistical Software, 35(3): 1–22.
- Sachs, K.; Perez, O.; Pe’er, D.; Lauffenburger, D. A.; and Nolan, G. P. 2005. Causal protein-signaling networks derived from multiparameter single-cell data. Science, 308(5721): 523–529.