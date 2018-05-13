import networkx as nx


def create_graph():
    users, repos, edges = load_graph()
    fix_ids(users, repos, edges)

    g = nx.Graph()
    g.add_edges_from(edges)
    return g


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


g = create_graph()

