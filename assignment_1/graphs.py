import matplotlib.pyplot as plt
import networkx as nx


def draw(g):
    nx.draw(g, with_labels=True)

    plt.show()


def degree_distribution(g):
    degrees = nx.degree(g)
    deg_distr = {}
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
    plt.title("Degree distribution")
    plt.xlabel("Degree")
    plt.ylabel("Count")
    plt.show()


def distance_distribution(g):
    distances = nx.shortest_path_length(g)
    dd = {}
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
    plt.title("Distance distribution")
    plt.xlabel("Distance")
    plt.ylabel("Count")
    plt.show()


def clustering(g):
    cl = nx.clustering(g)
    plt.plot(cl.keys(), cl.values())
    plt.title("Clustering coefficient distribution")
    plt.ylabel("Clustering coefficient")
    plt.xlabel("Node index")
    plt.show()


g = nx.Graph()
g.add_edges_from([(1, 2), (2, 3), (3, 4), (3, 5), (3, 6), (4, 6), (5, 6)])

draw(g)

# degree_distribution(g)
# distance_distribution(g)
clustering(g)
