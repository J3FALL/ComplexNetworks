from typing import Dict

import matplotlib.pyplot as plt
import networkx as nx


def draw(graph: nx.Graph) -> None:
    nx.draw(graph, with_labels=True)
    plt.show()


def degree_distribution(graph: nx.Graph) -> None:
    degrees = nx.degree(graph)
    deg_distr: Dict[int, int] = dict()
    for key, val in degrees.items():
        # degrees[node[0]] = node[1]

        if val not in deg_distr.keys():
            deg_distr[val] = 1
        else:
            deg_distr[val] += 1

    print(degrees)
    print(deg_distr)

    plt.bar(deg_distr.keys(), deg_distr.values())
    plt.xticks(list(deg_distr.keys()), [1, 2, 3, 4])
    plt.title('Degree distribution')
    plt.xlabel('Degree')
    plt.ylabel('Count')
    plt.show()


def distance_distribution(graph: nx.Graph) -> None:
    distances = nx.shortest_path_length(graph)
    dd: Dict[int, int] = dict()
    for i in range(1, 7):
        for j in range(1, 7):
            if distances[i][j] not in dd.keys():
                dd[distances[i][j]] = 1
            else:
                dd[distances[i][j]] += 1

    dd.pop(0)
    dd = {key: int(val / 2) for key, val in dd.items()}
    plt.bar(dd.keys(), dd.values())
    plt.xticks(list(dd.keys()), [1, 2, 3])
    plt.title('Distance distribution')
    plt.xlabel('Distance')
    plt.ylabel('Count')
    plt.show()


def clustering(graph: nx.Graph) -> None:
    cl: Dict[int, float] = nx.clustering(graph)
    plt.plot(cl.keys(), cl.values())
    plt.title('Clustering coefficient distribution')
    plt.ylabel('Clustering coefficient')
    plt.xlabel('Node index')
    plt.show()


if __name__ == '__main__':
    g = nx.nx.Graph()
    g.add_edges_from([(1, 2), (2, 3), (3, 4), (3, 5), (3, 6), (4, 6), (5, 6)])

    draw(g)

    # degree_distribution(g)
    # distance_distribution(g)
    clustering(g)
