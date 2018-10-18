import csv
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from project.emails.data.utils import log_binning

FILE_PATH = 'data/emails.txt'
FIGURES_PATH = 'figures/'


def graph_instance():
    g = nx.Graph()
    g.add_edges_from(edges_from_file(FILE_PATH))
    return g


def edges_from_file(path):
    edges = []
    with open(path, 'r') as file:
        for line in file.readlines()[1:]:
            node_from, node_to = map(int, line.split("\t"))
            edges.append([node_from, node_to])
    return edges


def degrees_distribution(graph):
    degs = sorted(graph.degree([node for node in graph.nodes()]).values(), reverse=True)

    deg_x, deg_y = log_binning(dict(Counter(degs)), 50)

    plt.figure()
    plt.scatter(deg_x, deg_y, c='r', marker='s', s=25, label='')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Degrees Distribution')
    plt.xlabel('k')
    plt.ylabel('Count')
    plt.savefig(FIGURES_PATH + 'degrees_distribution.png')


def average_degree(graph):
    degs = list(graph.degree([node for node in graph.nodes()]).values())
    return sum(degs) / len(graph.nodes())


def giant_components_distribution(graph, dump_reduced=False):
    fractions = []

    components = sorted(nx.connected_component_subgraphs(graph), key=len, reverse=True)

    if dump_reduced:
        dump_graph(components[0], path='data/reduced_graph.csv')

    for sub in components:
        print("Component fraction: %.5f with nodes: %d; edges: %d" %
              (len(sub.nodes()) / len(graph.nodes()), len(sub.nodes()), len(sub.edges())))
        fractions.append(len(sub.nodes()) / len(graph.nodes()))

    idxs = np.arange(len(fractions))

    fractions_to = 10

    plt.bar(idxs[:fractions_to], fractions[:fractions_to], width=0.5, color='b', label='Fraction of nodes')
    plt.title('Nodes distribution by components')
    plt.ylabel('Fraction')
    plt.yscale('log')
    plt.xticks(idxs[:fractions_to])
    plt.savefig(FIGURES_PATH + 'components_distribution.png')


def clustering_distribution_from_gephi(path="data/gephi_metrics.csv"):
    clustering_coeffs = []
    with open(path) as file:
        reader = csv.DictReader(file, delimiter=',')
        for line in reader:
            clustering_coeffs.append(float(line['clustering']))

    clustering_coeffs = sorted(clustering_coeffs)
    clust_x, clust_y = log_binning(dict(Counter(clustering_coeffs)), 70)

    plt.scatter(clust_x, clust_y, c='r', marker='s', s=25, label='')
    plt.yscale('log')
    plt.xlim(0, 1.01)
    plt.title('Local clustering coefficient distribution')
    plt.ylabel('Count')
    plt.xlabel('Clustering coefficient')
    plt.savefig(FIGURES_PATH + "clustering_distribution.png")


def dump_graph(graph, path):
    nx.write_edgelist(graph, path, data=False)


# g = graph_instance()
# giant_components_distribution(g)

clustering_distribution_from_gephi()
