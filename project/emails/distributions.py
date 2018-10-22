import csv
import multiprocessing
from collections import Counter
from itertools import repeat
from multiprocessing import Pool

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

FILE_PATH = 'data/emails.txt'
FIGURES_PATH = 'figures/'

import math


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


def drop_zeros(a_list):
    return [i for i in a_list if i > 0]


def log_binning(counter_dict, bin_count=35):
    keys = counter_dict.keys()
    values = counter_dict.values()

    max_x = math.log10(max(keys))
    max_y = math.log10(max(values))
    max_base = max([max_x, max_y])

    min_x = math.log10(min(drop_zeros(keys)))

    bins = np.logspace(min_x, max_base, num=bin_count)

    bin_means_y = (np.histogram(list(keys), bins, weights=list(values))[0] /
                   np.histogram(list(keys), bins)[0])
    bin_means_x = (np.histogram(list(keys), bins, weights=list(keys))[0] /
                   np.histogram(list(keys), bins)[0])

    return bin_means_x, bin_means_y


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


def betweenness_distribution_from_gephi(path="data/gephi_metrics.csv"):
    btw = []
    with open(path) as file:
        reader = csv.DictReader(file, delimiter=',')
        for line in reader:
            btw.append(float(line['betweenesscentrality']))

    plt.figure()
    btw_x, btw_y = log_binning(dict(Counter(btw)), 70)
    plt.scatter(btw_x, btw_y, c='r', marker='s', s=25, label='')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Betweenness centrality distribution')
    plt.xlabel('Betweenness centrality')
    plt.ylabel('Count')
    plt.savefig(FIGURES_PATH + "betweenness_distribution.png")


def dump_graph(graph, path):
    nx.write_edgelist(graph, path, data=False)


def graph_from_gephi_edge_list(path):
    with open(path, 'rb') as file:
        next(file, '')
        graph = nx.read_edgelist(file, nodetype=int)
        return graph


def all_paths_from(graph, from_idx):
    nodes = graph.nodes()
    print("nodes: %d/%d" % (from_idx, len(nodes)))
    distances = []
    for to_idx in range(from_idx + 1, len(nodes)):
        try:
            dist = nx.shortest_path_length(graph, nodes[from_idx], nodes[to_idx])
            distances.append(dist)
        except nx.NetworkXException:
            print("No path for (%d %d)" % (from_idx, to_idx))
    return [distances]


def shortest_paths_distribution(graph):
    print(multiprocessing.cpu_count())
    p = Pool(multiprocessing.cpu_count())
    # this will take awhile
    distances = p.starmap(all_paths_from, zip(repeat(graph), [i for i in range(len(graph.nodes()))]))

    p.close()
    p.join()

    print(len(distances))
    to_file(distances)


def to_file(distances):
    with open("data/dist.txt", 'w') as file_handler:
        for item in distances:
            file_handler.write("{}\n".format(item))


if __name__ == '__main__':
    g = graph_from_gephi_edge_list("data/reduced_graph.csv")
    shortest_paths_distribution(g)
