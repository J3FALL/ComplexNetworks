import csv
from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np


def create_graph():
    users, repos, edges = load_graph()
    fix_ids(users, repos, edges)

    g = nx.Graph()
    g.add_edges_from(edges)
    return g, users, repos, edges


def dump_graph_to_csv(edges, file_name):
    with open(file_name, 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for e in edges:
            filewriter.writerow([e[0], e[1]])


def fix_csv(file_name):
    with open(file_name, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        name = file_name.split('.')[0]
        f = open(name + "_fixed.csv", 'w', newline='')
        writer = csv.writer(f)
        for row in reader:
            if len(row) != 0:
                writer.writerow(row)


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
    # plt.xscale('symlog')
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


def reduce_graph(g, users, repos):
    users_reduced = reduce_users(g, users)
    repos_reduced = reduce_repos(g, repos)

    nodes = users_reduced + repos_reduced

    sub = g.subgraph(nodes)
    print(sub.number_of_nodes())
    print(sub.number_of_edges())

    user_degree_distribution(sub, users_reduced)
    return sub


def reduce_users(g, users):
    degs = g.degree(users)

    reduced = []
    for user in degs.keys():
        if degs[user] >= 5 and degs[user] <= 50:
            reduced.append(user)

    return reduced


def reduce_repos(g, repos):
    degs = g.degree(repos)

    reduced = []
    for repo in degs.keys():
        if degs[repo] >= 5 and degs[repo] <= 100:
            reduced.append(repo)

    return reduced


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
        # print("Component diameter: %d" % diameter(g.subgraph(c)))


def clustering(g):
    cl = nx.clustering(g)
    values = np.array(sorted(cl.values()))
    cum_func = np.cumsum(values)

    print(sorted(cum_func / np.max(cum_func), reverse=True))


# fix_csv()

g, users, repos, edges = create_graph()
#
print("Nodes: %d" % g.number_of_nodes())
print("Edges: %d" % g.number_of_edges())

# dump_graph_to_csv(edges)

# user_degree_distribution(g, users)
# repo_degree_distribution(g, repos)

# reduce_users(g, users)
# reduce_repos(g, repos)
sub = reduce_graph(g, users, repos)
dump_graph_to_csv(sub.edges(), 'reduced.csv')
fix_csv('reduced.csv')
# dump_graph_to_csv(sub.edges())
# components(g)
# distance_distribution(g)
# clustering(g)
