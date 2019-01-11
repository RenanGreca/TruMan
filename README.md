# TruMan: Trust Management for Vehicular Networks

TruMan is a trust management model designed for vehicular networks and other mobile ad-hoc wireless networks. The code in this repository was used to simulate and evaluate the model, which was developed during my master's degree studies at the Federal University of Paraná, Brazil. The project also led to a paper, which was presented and published at the ISCC 2018, in Natal, Brazil.

## Documents

MSc dissertation:
- [Download PDF](https://github.com/RenanGreca/TruMan/raw/master/docs/TruMan%20Trust%20Management%20for%20Vehicular%20Networks%20(dissertation).pdf)
- [UFPR Archive](https://www.acervodigital.ufpr.br/handle/1884/57615)

Paper presented at ISCC 2018:
- [Download PDF](https://github.com/RenanGreca/TruMan/raw/master/docs/TruMan%20Trust%20Management%20for%20Vehicular%20Networks%20(article).pdf)
- [IEEE Xplore](https://ieeexplore.ieee.org/abstract/document/8538683)

# Dependencies

## [The ONE simulator](http://akeranen.github.io/the-one/) (and therefore Java)

Network simulator that generates the mobility data for the algorithm. This simulator is recommended because contains the implementation for the [Working Day Movement Model](https://dl.acm.org/citation.cfm?id=1374695).

Furthermore, we have added our own report module to the simulator, called AdjacencyReport, which outputs the pairs of nodes that are within communication range of each other at a certain interval. **This module is available on [our fork of the ONE repository](https://github.com/RenanGreca/the-one)**.

Other network simulators can be used, as long as it is possible to produce a result similar to the output of `process_report.py` (see below).

## [SNAP.py](https://snap.stanford.edu/snappy/)

SNAP is a network analysis tool for python that is used to interact with graphs and networks in the algorithm. It was chosen due to a particularly memory-efficient implementation.

Due to SNAP, TruMan requires Python 2.7.

## Required Python packages:

  - snap
  - multiprocessing
  - numpy

# Usage

1. Prepare mobility configuration by editing `working_day.txt` or `small_working_day.txt`.

2. Run The ONE. This runs a simulation of 24 hours of mobility and stores reports containing pairs of nodes within communication range at each timestamp. Multiple scenarios can be run in sequence.

    ```./one.sh -b 1 ../TruMan/[small_]working_day.txt```

    - `-b`: Number of scenarios to be run (view comments in configuration file).

3. Extract the adjacency snapshots from the report. This separates the report from The ONE (which can be quite large) into smaller files; one for each timestamp.

    ```python process_report.py -r ../the-one/reports -o processed_reports```
    
    - `-i`: Input directory, containing the reports files.
    - `-o`: Output directory, which will contain the processed mobility data, in sub-directories named after the scenarios.

4. Generate the weights. This marks a set of nodes as malicious.

    ```python generate_weights.py -i processed_reports/wdmm_small_50 -o networks -m 10 --draw_graph```

    - `-i`: Input directory containing the processed mobility data.
    - `-o`: Output directory, which will contain the ground truth data for the simulation.
    - `-m`: Percentage of malicious nodes. Valid values: `0.0-50.0` (float).
    - `--draw_graph`: If enabled, generate a PNG file with the graph topology.

5. Run TruMan. The input and output directories should be the same as the previous script.

    ```python trust_snap.py -i processed_reports/wdmm_small_50 -o networks/wdmm_small_50 -p```

    - `-i`: Input directory containing the processed mobility data.
    - `-o`: Output directory, should contain the ground truth data for the simulation. The results are saved in a `results` subdirectory.
    - `-p`: Activate CPU parallelization. Worthwhile when there are many nodes.
    - `-s`: Iterator multiplier. Results might be satisfactory even if not all mobility data is used. Default: 1 (int).
    - `-t`: Strongly connected component threshold. Trust values should be at least this much to be considered positive. Valid values: `0.0-1.0` (float). Default: `0.5`.
    - `-a`: Aging rate. Defines the number of iterations it should take for information to be considered stale. Valid values: `0-` (int).
    - `--draw_graphs`: If enabled, generate a PNG containing the graph topology at each iteration.

6. Generate plot from output.

    ```python python plot-graph-1.py -i networks/20181221/```