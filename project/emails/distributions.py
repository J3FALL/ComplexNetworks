import ast
from collections import Counter
import csv
from itertools import repeat
import math
import multiprocessing
from multiprocessing import Pool
import os
from typing import (
    Dict,
    List,
    Optional,
    Tuple
)

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from project.emails import common

Edge = Tuple[int, int]


def graph_instance() -> nx.Graph:
    g = nx.Graph()
    g.add_edges_from(edges_from_file(common.GRAPH_PATH))
    return g


def edges_from_file(path: str) -> List[Edge]:
    edges: List[Edge] = []
    with open(path, 'r') as file:
        for line in file.readlines()[1:]:
            node_from, node_to = map(int, line.split('\t'))
            edges.append((node_from, node_to))
    return edges


def log_binning(counter_dict: Dict, bin_count: int = 35) -> Tuple[float, float]:
    keys = counter_dict.keys()
    values = counter_dict.values()

    max_x = math.log10(max(keys))
    max_y = math.log10(max(values))
    max_base = max([max_x, max_y])

    min_x = math.log10(min(filter(lambda v: v > 0, keys)))

    bins = np.logspace(min_x, max_base, num=bin_count)

    bin_means_y = (np.histogram(list(keys), bins, weights=list(values))[0] /
                   np.histogram(list(keys), bins)[0])
    bin_means_x = (np.histogram(list(keys), bins, weights=list(keys))[0] /
                   np.histogram(list(keys), bins)[0])

    return bin_means_x, bin_means_y


def degrees_distribution(graph: nx.Graph, show: bool = False,
                         return_values: bool = False) -> Optional[Tuple[float, float]]:
    degs = sorted(list(dict(graph.degree([node for node in graph.nodes()])).values()), reverse=True)

    deg_x, deg_y = log_binning(dict(Counter(degs)), 50)

    if show:
        plt.figure()
        plt.scatter(deg_x, deg_y, c='r', marker='s', s=25, label='')
        plt.xscale('log')
        plt.yscale('log')
        plt.title('Degrees Distribution')
        plt.xlabel('k')
        plt.ylabel('Count')
        plt.show()
        plt.savefig(os.path.join(common.FIGURES_FOLDER, 'degrees_distribution.png'))

    if return_values:
        return deg_x, deg_y
    return None


def average_degree(graph: nx.Graph) -> float:
    degs = list(dict(graph.degree([node for node in graph.nodes()])).values())
    return sum(degs) / len(graph.nodes())


def giant_components_distribution(graph: nx.Graph, dump_reduced: bool = False) -> None:
    fractions = []

    components = sorted(nx.connected_component_subgraphs(graph), key=len, reverse=True)

    if dump_reduced:
        dump_graph(components[0], path=common.REDUCED_GRAPH_PATH)

    for sub in components:
        fraction = len(sub.nodes()) / len(graph.nodes())
        print(f'Component fraction: {round(fraction, 5)} with nodes: {len(graph.nodes())}; edges: {len(sub.edges())}')
        fractions.append(fraction)

    idxs = np.arange(len(fractions))

    fractions_to = 10

    plt.bar(idxs[:fractions_to], fractions[:fractions_to], width=0.5, color='b', label='Fraction of nodes')
    plt.title('Nodes distribution by components')
    plt.ylabel('Fraction')
    plt.yscale('log')
    plt.xticks(idxs[:fractions_to])
    plt.savefig(os.path.join(common.FIGURES_FOLDER, 'components_distribution.png'))


def clustering_distribution_from_gephi(path: Optional[str] = None) -> None:
    if path is None:
        path = common.GEPHI_METRICS

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
    plt.savefig(os.path.join(common.FIGURES_FOLDER, 'clustering_distribution.png'))


def betweenness_distribution_from_gephi(path: Optional[str] = None) -> None:
    if path is None:
        path = common.GEPHI_METRICS

    with open(path) as file:
        reader = csv.DictReader(file, delimiter=',')
        btw = [float(line['betweenesscentrality']) for line in reader]

    plt.figure()
    btw_x, btw_y = log_binning(dict(Counter(btw)), 70)
    plt.scatter(btw_x, btw_y, c='r', marker='s', s=25, label='')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Betweenness centrality distribution')
    plt.xlabel('Betweenness centrality')
    plt.ylabel('Count')
    plt.savefig(os.path.join(common.FIGURES_FOLDER, 'betweenness_distribution.png'))


def dump_graph(graph: nx.Graph, path: str) -> None:
    nx.write_edgelist(graph, path, data=False)


def graph_from_gephi_edge_list(path: str) -> nx.Graph:
    with open(path, 'rb') as file:
        next(file, '')
        graph = nx.read_edgelist(file, nodetype=int)
        return graph


def all_paths_from(graph: nx.Graph, from_idx: int) -> List[List[float]]:
    nodes = graph.nodes()
    print(f'nodes: {from_idx}/{len(nodes)}')
    distances: List[float] = []
    for to_idx in range(from_idx + 1, len(nodes)):
        try:
            distances.append(nx.shortest_path_length(graph, nodes[from_idx], nodes[to_idx]))
        except nx.NetworkXException:
            print(f'No path for ({from_idx}, {to_idx})')

    return [distances]


def calculate_shortest_paths(graph: nx.Graph) -> None:
    cpu_count = multiprocessing.cpu_count()
    print(f'CPU count: {cpu_count}')
    with Pool(multiprocessing.cpu_count()) as p:
        # this will take awhile
        distances = p.starmap(all_paths_from, zip(repeat(graph), [i for i in range(len(graph.nodes()))]))

    print(len(distances))

    with open(os.path.join(common.DATA_FOLDER, 'dist.txt'), 'w') as file_handler:
        for item in distances:
            file_handler.write(f'{item}\n')


def shortest_paths_distribution() -> None:
    dist_by_val: Counter = Counter()

    with open(os.path.join(common.DATA_FOLDER, 'dist.txt'), 'r') as file:
        idx = 0
        for line in file:
            if idx % 10 == 0 and idx != 0:
                print(idx)
            data = ast.literal_eval(line)[0]
            for dist in data:
                dist_by_val[dist] += 1
            # print(dist_by_val)
            idx += 1

    dist_x, dist_y = log_binning(dict(dist_by_val), 50)

    plt.figure()
    plt.scatter(dist_x, dist_y, c='r', marker='s', s=25, label='')
    plt.yscale('log')
    plt.title('Distance Distribution')
    plt.xlabel('d')
    plt.ylabel('Count')
    plt.savefig(os.path.join(common.FIGURES_FOLDER, 'distances_distribution.png'))


def assortativity_distribution(graph: nx.Graph) -> None:
    assorts = sorted(nx.average_degree_connectivity(graph).items())
    assort_x, assort_y = log_binning(dict(assorts), 40)

    plt.figure()
    plt.scatter(assort_x, assort_y, c='r', marker='s', s=25, label='')
    plt.title('Assortativity')
    plt.xlabel('k')
    plt.ylabel('$<k_{nn}>$')
    plt.savefig(os.path.join(common.FIGURES_FOLDER, 'assortativity.png'))


def power_law(graph: nx.Graph) -> float:
    degrees = sorted(list(dict(graph.degree([node for node in graph.nodes()])).values()))
    degree_min = 2
    total_sum = sum([math.log(deg / degree_min) for deg in degrees])
    return 1 + len(degrees) * pow(total_sum, -1)


def pearson_correlation(graph: nx.Graph) -> float:
    return nx.degree_pearson_correlation_coefficient(graph)


if __name__ == '__main__':
    g = graph_from_gephi_edge_list(common.REDUCED_GRAPH_PATH)
    # assortativity_distribution(g)
    print(power_law(g))
    print(pearson_correlation(g))
