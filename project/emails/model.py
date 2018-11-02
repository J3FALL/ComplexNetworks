import os
from typing import (
    List,
    Tuple
)

import matplotlib.pyplot as plt
import networkx as nx

from project.emails import common
from project.emails.distributions import (
    average_degree,
    degrees_distribution,
    dump_graph,
    graph_from_gephi_edge_list
)


def simple_barabasi_albert(graph: nx.Graph, edges_count: int) -> nx.Graph:
    nodes = len(graph.nodes())
    ba = nx.barabasi_albert_graph(nodes, edges_count)
    return ba


def extended_barabasi_albert(graph: nx.Graph, path: str) -> None:
    nodes = len(graph.nodes())
    p = 0.837
    q = 0.002
    # this will take awhile-awhile-awhile
    ba = nx.extended_barabasi_albert_graph(n=int(nodes / 10), m=1, p=p, q=q)
    dump_graph(ba, path)


def extended_ba_distributions(graph: nx.Graph) -> None:
    ba = nx.read_edgelist(common.EXTENDED_BA_PATH)

    ba_deg_x, ba_deg_y = degrees_distribution(ba, show=False, return_values=True)
    src_deg_x, src_deg_y = degrees_distribution(graph, show=False, return_values=True)

    plt.figure()

    plt.scatter(ba_deg_x, ba_deg_y, marker='s', s=25, label='Extended Barabasi-Albert')
    plt.scatter(src_deg_x, src_deg_y, marker='s', s=25, label='Source graph')
    plt.xscale('log')
    plt.yscale('log')
    plt.title('Degrees Distribution')
    plt.xlabel('k')
    plt.ylabel('Count')
    plt.legend()

    plt.savefig(os.path.join(common.FIGURES_FOLDER, 'models', 'extended_ba_degrees.png'))


def compare_degrees_distributions(source_graph: nx.Graph) -> None:
    avg_edges = average_degree(source_graph)
    print(f'Average degree: {round(avg_edges, 3)}')

    labels = []
    degs: List[Tuple[float, float]] = []
    for edges in [2, 5, 10, 15]:
        deg_x, deg_y = degrees_distribution(simple_barabasi_albert(source_graph, edges), show=False, return_values=True)

        labels.append(f'Barabasi-Albert, m = {edges}')
        degs.append((deg_x, deg_y))

    plt.figure()
    src_deg_x, src_deg_y = degrees_distribution(source_graph, show=False, return_values=True)
    plt.plot(src_deg_x, src_deg_y, linestyle='--', linewidth=3, color='purple', label='Source graph')
    for deg, label in zip(degs, labels):
        deg_x, deg_y = deg

        plt.scatter(deg_x, deg_y, marker='s', s=25, label=label)

    plt.xscale('log')
    plt.yscale('log')
    plt.title('Degrees Distribution')
    plt.xlabel('k')
    plt.ylabel('Count')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    g = graph_from_gephi_edge_list(common.REDUCED_GRAPH_PATH)
    extended_ba_distributions(g)
