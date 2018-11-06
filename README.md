# Complex Network

[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)

This repository contains all scripts that were developed during Complex Networks course studying.

The main goal of the project was to take some "real network" and to analyse its structure and properties, such as:
* Average values and distributions of the network metrics: in/out degrees, shortest paths lengths, diameter, clustering coefficient.
* Centrality of the network ?
* What are the communities in the network?
* Which model describes the network? 
* Robustness of the network.
* Propagation through the network.

As a network to study Enron email communication network provided by [SNAP] was taken.
Network metrics were obtained mostly using [NetworkX] framework and [Gephi].
To model the network simple and extended Barabasi-Albert model were taken.
Propagation studying were performed with simple SIR-model.

All resulted figures (most of its were log-binned) can be found in [figures](project/figures/) project directory.


## Lessons We've learned while studying Complex Networks
All this network science stuff is really time-consuming, so be prepared to figure out how to minimize your calculations.
The following guys deserve a special attention:
* Despite that NetworkX provides shortest paths calculations out of the box, it is not well suitable for large networks. Thus, the best advices would be:
  * To divide the source network by components and to calculate the metrics separately.
  * To parallelize the calculations and wait some time.
  * Do not use NetworkX for this purpose.
* Betweenness and diameter is much easier to obtain from Gephi.
* Robustness by failure (i.e. each step a node to be attacked is choosing randomly) would take a long time.


[SNAP]:
https://snap.stanford.edu/data/email-Enron.html
[NetworkX]:
https://networkx.github.io/
[Gephi]:
https://gephi.org/



## Install requirements

```bash
(venv)$ pip install -r requirements.txt
```


## Test

```
(venv)$ pip isntall -r requirements-test.txt
(venv)$ flake8 .
(venv)$ mypy projects/emails
```
