from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def create_graph():
    users, repos, edges = load_graph()
    fix_ids(users, repos, edges)

    g = nx.Graph()
    g.add_edges_from(edges)
    return g, users, repos


def load_graph():
    file_name = "github/data.txt"
    edges = []
    users = {}
    repos = {}
    with open(file_name) as file:
        for line in file:
            user, repo = map(int, line.split(":"))
            edges.append([user, repo])

            users[user] = 1
            repos[repo] = 1

    return users, repos, edges


# Add offsets for each repo id to follow the uniqueness of node ids
def fix_ids(users, repos, edges):
    offset = len(users.keys())

    idx = 0
    for repo in repos.keys():
        repos[repo] = idx + offset
        idx += 1

    for e in edges:
        e[1] = repos[e[1]]


def user_degree_distribution(g, users):
    degs = sorted(list(g.degree(users).values()), reverse=True)
    degs_count = Counter(degs)
    deg, cnt = zip(*degs_count.items())

    plt.scatter(deg, cnt, s=3)
    plt.title("User degree distribution")
    plt.xlabel('Degree (d)')
    plt.ylabel('Frequency')
    plt.xscale('symlog')
    plt.yscale('symlog')
    plt.show()


def repo_degree_distribution(g, repos):
    degs = sorted(list(g.degree(repos).values()), reverse=True)
    degs_count = Counter(degs)
    deg, cnt = zip(*degs_count.items())

    plt.scatter(deg, cnt, s=3)
    plt.title("Repos degree distribution")
    plt.xlabel('Degree (d)')
    plt.ylabel('Frequency')
    plt.xscale('symlog')
    plt.yscale('symlog')
    plt.show()


def distance_distribution(g):
    distances = nx.shortest_path_length(g)

    n = g.number_of_nodes()
    d = list()
    for i in range(1, n):
        for j in range(1, n):
            d.append(distances[i][j])


def diameter(g):
    return nx.diameter(g)


def components(g):
    comps = sorted(nx.connected_components(g), key=len, reverse=True)

    for c in comps:
        print("Component size: %d" % len(c))
        print("Component diameter: %d" % diameter(g.subgraph(c)))


def clustering(g):
    cl = nx.clustering(g)
    values = np.array(sorted(cl.values()))
    cum_func = np.cumsum(values)

    print(sorted(cum_func / np.max(cum_func), reverse=True))


g, users, repos = create_graph()

print("Nodes: %d" % g.number_of_nodes())
print("Edges: %d" % g.number_of_edges())

# user_degree_distribution(g, users)
# repo_degree_distribution(g, repos)
# components(g)
# distance_distribution(g)
clustering(g)
