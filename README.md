# Integer Linear Programming Models and Greedy Heuristic for the Minimum Weighted Independent Dominating Set Problem

## Contents
- doc - contains the paper;
- instances - contains the two groups of instances used in the paper;
- src - contains Python source code of all algorithms presented in the paper;
- test - contains all results presented in the paper;
- stats_data - contains results of all compared algorithms;
- cd_plots - contains critical difference plots.

## Requirements
- Python 3
- Networkx
- sortedcontainers

### ILP
- CPLEX
- Docplex

### Statistics
- scipy
- scikit_posthocs
- matplotlib
- pandas

## Usage
```python ilp.py [-m {new1,new2}] [-i IN_DIR_PATH] [-s INSTANCES_SUBSET] [-o OUT_DIR_PATH] [-v]```

```python greedy.py [-i IN_DIR_PATH] [-s INSTANCES_SUBSET] [-o OUT_DIR_PATH]```

Use ```-h``` option for more information about the arguments.