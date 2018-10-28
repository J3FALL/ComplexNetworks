# Copyright (c) 2015-2017 Michael Lees, Debraj Roy
from __future__ import unicode_literals

import random
import sys
from enum import *

import matplotlib.pyplot as plt  # import matplotlib for plotting/drawing grpahs
import networkx as nx

from project.emails.distributions import graph_from_gephi_edge_list

plt.interactive(True)


class State(Enum):
    Succeptible = 0
    Infected = 1
    Removed = 2


def reset(G):
    """
    :param G: The graph to reset
    Initialise/reset all the nodes in the network to be succeptible.
    Used to initialise the network at the start of an experiment
    """
    nx.set_node_attributes(G, name='state', values=State.Succeptible)


def initialise_infection(G, num_to_infect):
    """
    :param G: Graph to infect nodes on
    :param num_to_infect: Number of nodes to infect on G
    Set the state of a random selection of nodes to be infected.
    numToInfect specifices how many infections to make, the nodes
    are chosen randomly from all nodes in the network
    """
    nodes_to_infect = random.sample(G.nodes(), num_to_infect)
    for n in nodes_to_infect:
        G.node[n]['state'] = State.Infected
    return nodes_to_infect


def transmission_model_factory(beta=0.03, alpha=0.05):
    """
    :param beta: specifies the rate of infection (movement from S to I)
    :param alpha: specifies the rate of removal (movement from I to R)
    :returns: a function specifying infection model.
    Creates and returns an instance of a infection model. This allows us
    to create a number of models with different beta and alpha parameters.
    Note that in a single time step an infected node can infect their neighbours
    and then be removed.
    """

    def m(n, G):
        list_of_neighbours_to_infect = []  # list of neighbours will be infect after executing this step
        removeMyself = False  # should I change my state to removed?
        if G.node[n]['state'] == State.Infected:
            # infect susceptible neighbours with probability beta
            for k in G.neighbors(n):
                if G.node[k]['state'] == State.Succeptible:
                    if random.random() <= beta:  # generate random number between 0 and 1
                        list_of_neighbours_to_infect.append(k)
            if random.random() <= alpha:
                removeMyself = True
        return list_of_neighbours_to_infect, removeMyself

    return m


def apply_infection(G, list_of_newly_infected, list_of_newly_removed):
    """
    :param G: The graph on which to operate
    :param list_of_newly_infected: A list of nodes to infect (move from S to I)
    :param list_of_newly_removed: A list of nodes to remove (movement from I to R)
    Applies the state changes to nodes in the network. Note that the transmission model
    actually builds a list of nodes to infect and to remove.
    """
    for n in list_of_newly_infected:
        G.node[n]['state'] = State.Infected
    for n in list_of_newly_removed:
        G.node[n]['state'] = State.Removed


def execute_one_step(G, model):
    """
    :param G: the Graph on which to execute the infection model
    :param model: model used to infect nodes on G
    executes the infection model on all nodes in G
    """
    new_nodes_to_infect = []  # nodes to infect after executing all nodes this time step
    new_nodes_to_remove = []  # nodes to set to removed after this time step
    for n in G:  # for each node in graph,
        i, remove = model(n, G)  # execute transmission model on node n
        new_nodes_to_infect = new_nodes_to_infect + i  # add neigbours of n that are infected
        if remove:  # if I should remove this node? determined by model
            new_nodes_to_remove.append(n)
    apply_infection(G, new_nodes_to_infect, new_nodes_to_remove)


def get_infection_stats(G):
    """
    :param G: the Graph on which to execute the infection model
    :returns: a tuple containing three lists of succeptible, infected and removed nodes.
    Creates lists of nodes in the graph G that are succeptible, infected and removed.
    """
    infected = []  # list of infected nodes
    succeptible = []  # list of succeptible
    removed = []  # list of removed nodes
    for n in G:
        if G.node[n]['state'] == State.Infected:
            infected.append(n)
        elif G.node[n]['state'] == State.Succeptible:
            succeptible.append(n)
        else:
            removed.append(n)
    return succeptible, infected, removed  # return the three lists.


def print_infection_stats(G):
    """
    :param G: the Graph on which to execute the infection model
    Prints the number of succeptible, infected and removed nodes in graph G.
    """
    s, i, r = get_infection_stats(G)
    print("Succeptible: %d Infected: %d Removed %d" % (len(s), len(i), len(r)))


def run_spread_simulation(G, model, initial_infection_count, run_visualise=False):
    """
    :param G: the Graph on which to execute the infection model
    :param model: model used to infect nodes on G
    :param initial_infection_count: Number of nodes to infect on G
    :param run_visualise: if set to true a visual representation of the network
                          will be written to file at each time step
    :returns : a 5-tuple containing, list of S,I,R nodes at end, the end time
               and the list of initially infected nodes (useful for visulisation)
    Runs a single simulation of infection on the graph G, using the specified model.
    An initial infection count is specified to infect a set of nodes.
    The simulation is executed until there are no more infected nodes, that is the
    infection dies out, or everyone ends up removed.
    """
    initially_infected = initialise_infection(G, initial_infection_count)

    s_results = []
    i_results = []
    r_results = []

    dt = 0
    s, i, r = get_infection_stats(G)

    pos = nx.spring_layout(G, k=.75)

    while len(i) > 0:
        execute_one_step(G, model)  # execute each node in the graph once
        dt += 1  # increase time step
        s, i, r = get_infection_stats(G)  # calculate SIR stats of the current time step
        s_results.append(len(s))  # add S counts to our final results
        i_results.append(len(i))  # add I counts to our final results
        r_results.append(len(r))  # add R counts to our final results
        sys.stderr.write('\rInfected: %d time step: %d' % (len(i), dt))
        sys.stderr.flush()
        if run_visualise:  # If run visualise is true, we output the graph to file
            draw_network_to_file(G, pos, dt, initially_infected)
    return s_results, i_results, r_results, dt, initially_infected  # return our results for plotting


def plot_infection(S, I, R, G):
    """
    :param S: time-ordered list from simulation output indicating how succeptible count changes over time
    :param I: time-ordered list from simulation output indicating how infected count changes over time
    :param R: time-ordered list from simulation output indicating how removed count changes over time
    :param G: Graph/Network of statistic to plot
    Creates a plot of the S,I,R output of a spread simulation.
    """
    peak_incidence = max(I)
    peak_time = I.index(max(I))
    total_infected = S[0] - S[-1]

    fig_size = [18, 13]
    plt.rcParams.update({'font.size': 14, "figure.figsize": fig_size})
    xvalues = range(len(S))
    plt.plot(xvalues, S, color='g', linestyle='-', label="S")
    plt.plot(xvalues, I, color='b', linestyle='-', label="I")
    plt.plot(xvalues, R, color='r', linestyle='-', label="R")
    plt.axhline(peak_incidence, color='b', linestyle='--', label="Peak Incidence")
    plt.annotate(str(peak_incidence), xy=(1, peak_incidence + 10), color='b')
    plt.axvline(peak_time, color='b', linestyle=':', label="Peak Time")
    plt.annotate(str(peak_time), xy=(peak_time + 1, 8), color='b')
    plt.axhline(total_infected, color='r', linestyle='--', label="Total Infected")
    plt.annotate(str(total_infected), xy=(1, total_infected + 10), color='r')
    plt.legend()
    plt.xlabel('time step')
    plt.ylabel('Count')
    plt.title('SIR for network size ' + str(G.order()))
    plt.show()


def draw_network_to_file(G, pos, t, initially_infected):
    """
    :param G: Graph to draw to png file
    :param pos: position defining how to layout graph
    :param t: current timestep of simualtion (used for filename distinction)
    :param initially_infected: list of initially infected nodes
    Draws the current state of the graph G, colouring nodes depending on their state.
    The image is saved to a png file in the images subdirectory.
    """
    # create the layout
    states = []
    for n in G.nodes():
        if n in initially_infected:
            states.append(3)
        else:
            states.append(G.nodes[n]['state'].value)
    from matplotlib import colors
    cmap = colors.ListedColormap(['green', 'blue', 'red', 'yellow'])
    bounds = [0, 1, 2, 3]

    # draw the nodes and the edges (all)
    nx.draw_networkx_nodes(G, pos, cmap=cmap, alpha=0.5, node_size=170, node_color=states)
    nx.draw_networkx_edges(G, pos, alpha=0.075)
    plt.savefig("images/g" + str(t) + ".png")
    plt.clf()


def dump_sir_history(path, s, i, r, end_time, initial_infected):
    import io
    file = io.open(path, 'w')
    file.write("%d\n" % end_time)
    for param in [s, i, r, initial_infected]:
        file.write("%s\n" % (" ".join([str(val) for val in param])))


def main():
    g = graph_from_gephi_edge_list("data/reduced_graph.csv")

    # sub = g.subgraph([idx for idx in range(500)])

    m = transmission_model_factory(0.05, 0.03)
    number_initial_infections = 20
    reset(g)  # initialise all nodes to succeptible
    S, I, R, endtime, ii = run_spread_simulation(g, m, number_initial_infections)
    dump_sir_history("data/sir/exp_1/sir_history_2.txt", S, I, R, endtime, ii)


if __name__ == "__main__":
    main()
