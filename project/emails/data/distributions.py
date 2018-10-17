def edges_from_file(path):
    edges = []
    with open(path, 'r') as file:
        for line in file.readlines()[1:]:
            node_from, node_to = map(int, line.split("\t"))
            edges.append([node_from, node_to])
    return edges


print(edges_from_file('emails.txt'))
