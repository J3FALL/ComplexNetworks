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


load_graph()
