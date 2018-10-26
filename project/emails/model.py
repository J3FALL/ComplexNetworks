import matplotlib.pyplot as plt
import networkx as nx

from project.emails.distributions import average_degree
from project.emails.distributions import degrees_distribution
from project.emails.distributions import dump_graph
from project.emails.distributions import graph_from_gephi_edge_list

FIGURES_PATH = 'figures/models/'


def simple_barabasi_albert(graph, edges):
    nodes = len(graph.nodes())
    ba = nx.barabasi_albert_graph(nodes, edges)
    return ba


def extended_barabasi_albert(graph):
    nodes = len(graph.nodes())
    p = 0.837
    q = 0.002
    # this will take awhile-awhile-awhile
    ba = nx.extended_barabasi_albert_graph(n=nodes, m=1, p=p, q=q)
    dump_graph(ba, 'data/extended_ba.csv')


def extended_ba_distributions(graph):
    ba = nx.read_edgelist('data/extended_ba.csv')

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

    plt.savefig(FIGURES_PATH + 'extended_ba_degrees.png')


def compare_degrees_distributions(source_graph):
    avg_edges = average_degree(source_graph)
    print("Average degree: %.3f" % avg_edges)

    labels = []
    degs = []
    for edges in [2, 5, 10, 15]:
        deg_x, deg_y = degrees_distribution(simple_barabasi_albert(source_graph, edges), show=False, return_values=True)

        labels.append("Barabasi-Albert, m = %d" % edges)
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


g = graph_from_gephi_edge_list("data/reduced_graph.csv")
extended_ba_distributions(g)
