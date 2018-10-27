import random

import networkx as nx


def graph_from_gephi_edge_list(path):
    with open(path, 'rb') as file:
        next(file, '')
        graph = nx.read_edgelist(file, nodetype=int)
        return graph


def fail(graph):
    n = random.choice(list(graph.nodes()))
    graph.remove_node(n)


def attack_degree(src_graph):
    # to modify the source graph you have to unfreeze it by creating a new graph
    graph = nx.Graph(src_graph)
    degrees = dict(graph.degree())
    max_degree = max(degrees.values())
    max_keys = [k for k, v in degrees.items() if v == max_degree]
    graph.remove_node(max_keys[0])

    return graph


def diameter_and_avg_path_length(graph):
    max_path_length = 0
    total = 0.0
    for n in graph:
        path_length = nx.single_source_shortest_path_length(graph, n)
        total += sum(path_length.values())
        if max(path_length.values()) > max_path_length:
            max_path_length = max(path_length.values())
    try:
        avg_path_length = total / (graph.order() * (graph.order() - 1))
    except ZeroDivisionError:
        avg_path_length = 0.0
    return max_path_length, avg_path_length


def giant_component_fraction(graph):
    components = sorted(nx.connected_component_subgraphs(graph), key=len, reverse=True)
    biggest_ga = components[0]

    return biggest_ga.size() / (len(graph.nodes()) * 1.0)


from tqdm import tqdm


def robustness_by_attack(src_graph, nodes_to_remove, measure_frequency):
    diameters_history = []
    path_len_history = []
    ga_fraction_history = []

    print("---- Starting Robustness Check ---- \n")

    graph = src_graph
    for iteration in tqdm(range(nodes_to_remove)):
        graph = attack_degree(graph)

        if iteration % measure_frequency == 0:
            diameter, avg_path_len = diameter_and_avg_path_length(graph)
            ga_fraction = giant_component_fraction(graph)

            diameters_history.append(diameter)
            path_len_history.append(avg_path_len)
            ga_fraction_history.append(ga_fraction)

    print("---- Done: Robustness Check ---- \n")

    print(diameters_history)
    print(path_len_history)
    print(ga_fraction_history)

    dump_history("data/robustness/attack/attack_history.txt", diameters_history, path_len_history, ga_fraction_history)


def robustness_by_fail(src_graph, number_of_runs, nodes_to_remove, measure_frequency):
    diameters_history = []
    path_len_history = []
    ga_fraction_history = []

    print("---- Starting Robustness Check ---- \n")

    for _ in tqdm(range(number_of_runs)):
        graph = src_graph

        diameters_on_run = []
        paths_on_run = []
        ga_on_run = []

        for iteration in tqdm(range(nodes_to_remove)):
            graph = attack_degree(graph)

            if iteration % measure_frequency == 0:
                diameter, avg_path_len = diameter_and_avg_path_length(graph)
                ga_fraction = giant_component_fraction(graph)

                diameters_on_run.append(diameter)
                paths_on_run.append(avg_path_len)
                ga_on_run.append(ga_fraction)

        diameters_history.append(diameters_on_run)
        path_len_history.append(paths_on_run)
        ga_fraction_history.append(ga_on_run)

    print("---- Done: Robustness Check ---- \n")

    print(diameters_history)
    print(path_len_history)
    print(ga_fraction_history)

    dump_history("data/robustness/fail/fail_history.txt", diameters_history,
                 path_len_history, ga_fraction_history, fail_mode=True)


def dump_history(file_path, diameters, paths, ga_fractions, fail_mode=False):
    import io
    file = io.open(file_path, 'w')

    if not fail_mode:
        for param in [diameters, paths, ga_fractions]:
            file.write("%s\n" % (" ".join([str(val) for val in param])))
    else:
        for run in range(len(diameters)):
            file.write('%d\n' % run)
            file.write("%s\n" % (" ".join([str(val) for val in diameters[run]])))
            file.write("%s\n" % (" ".join([str(val) for val in paths[run]])))
            file.write("%s\n" % (" ".join([str(val) for val in ga_fractions[run]])))


if __name__ == '__main__':
    g = graph_from_gephi_edge_list("data/reduced_graph.csv")
    # sub = g.subgraph([idx for idx in range(50)])

    robustness_by_attack(g, int(0.9 * len(g.nodes())), 50)
    robustness_by_fail(g, 5, int(0.9 * len(g.nodes())), 50)
