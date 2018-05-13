from collections import Counter

import matplotlib.pyplot as plt
import networkx as nx


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
    degs = sorted(g.degree(users).values(), reverse=True)
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
    degs = sorted(g.degree(repos).values(), reverse=True)
    degs_count = Counter(degs)
    deg, cnt = zip(*degs_count.items())

    plt.scatter(deg, cnt, s=3)
    plt.title("Repos degree distribution")
    plt.xlabel('Degree (d)')
    plt.ylabel('Frequency')
    plt.xscale('symlog')
    plt.yscale('symlog')
    plt.show()


g, users, repos = create_graph()

user_degree_distribution(g, users)
repo_degree_distribution(g, repos)
