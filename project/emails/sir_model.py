# Copyright (c) 2015-2017 Michael Lees, Debraj Roy
from __future__ import unicode_literals

from enum import Enum
import os
import random
import sys
from typing import (
    Callable,
    Dict,
    List,
    Tuple
)

from matplotlib import colors
import matplotlib.pyplot as plt
import networkx as nx

from project.emails import common
from project.emails.distributions import graph_from_gephi_edge_list


Model = Tuple[List[int], bool]
ModelFactory = Callable[[int, nx.Graph], Model]
Node = int
NodeList = List[Node]


class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    REMOVED = 2


def reset(graph: nx.Graph) -> None:
    """
    :param graph: The graph to reset
    Initialise/reset all the nodes in the network to be susceptible.
    Used to initialise the network at the start of an experiment
    """
    nx.set_node_attributes(graph, name='state', values=State.SUSCEPTIBLE)


def initialise_infection(graph: nx.Graph, num_to_infect: int) -> NodeList:
    """
    :param graph: Graph to infect nodes on
    :param num_to_infect: Number of nodes to infect on G
    Set the state of a random selection of nodes to be infected.
    numToInfect specifices how many infections to make, the nodes
    are chosen randomly from all nodes in the network
    """
    nodes_to_infect = random.sample(graph.nodes(), num_to_infect)
    for n in nodes_to_infect:
        graph.node[n]['state'] = State.INFECTED
    return nodes_to_infect


def transmission_model_factory(beta: float = 0.03, alpha: float = 0.05) -> ModelFactory:
    """
    :param beta: specifies the rate of infection (movement from S to I)
    :param alpha: specifies the rate of removal (movement from I to R)
    :returns: a function specifying infection model.
    Creates and returns an instance of a infection model. This allows us
    to create a number of models with different beta and alpha parameters.
    Note that in a single time step an infected node can infect their neighbours
    and then be removed.
    """

    def m(n: int, graph: nx.Graph) -> Model:
        list_of_neighbours_to_infect: List[int] = []  # list of neighbours will be infect after executing this step
        remove_myself = False  # should I change my state to removed?
        if graph.node[n]['state'] == State.INFECTED:
            # infect susceptible neighbours with probability beta
            for k in graph.neighbors(n):
                if graph.node[k]['state'] == State.SUSCEPTIBLE:
                    if random.random() <= beta:  # generate random number between 0 and 1
                        list_of_neighbours_to_infect.append(k)
            if random.random() <= alpha:
                remove_myself = True
        return list_of_neighbours_to_infect, remove_myself

    return m


def apply_infection(graph: nx.Graph, list_of_newly_infected: NodeList, list_of_newly_removed: NodeList) -> None:
    """
    :param graph: The graph on which to operate
    :param list_of_newly_infected: A list of nodes to infect (move from S to I)
    :param list_of_newly_removed: A list of nodes to remove (movement from I to R)
    Applies the state changes to nodes in the network. Note that the transmission model
    actually builds a list of nodes to infect and to remove.
    """
    for n in list_of_newly_infected:
        graph.node[n]['state'] = State.INFECTED
    for n in list_of_newly_removed:
        graph.node[n]['state'] = State.REMOVED


def execute_one_step(graph: nx.Graph, model: ModelFactory) -> None:
    """
    :param graph: the Graph on which to execute the infection model
    :param model: model used to infect nodes on G
    executes the infection model on all nodes in G
    """
    new_nodes_to_infect: NodeList = []  # nodes to infect after executing all nodes this time step
    new_nodes_to_remove: NodeList = []  # nodes to set to removed after this time step
    for n in graph:  # for each node in graph,
        i, remove = model(n, graph)  # execute transmission model on node n
        new_nodes_to_infect = new_nodes_to_infect + i  # add neigbours of n that are infected
        if remove:  # if I should remove this node? determined by model
            new_nodes_to_remove.append(n)
    apply_infection(graph, new_nodes_to_infect, new_nodes_to_remove)


def get_infection_stats(graph: nx.Graph) -> Tuple[NodeList, NodeList, NodeList]:
    """
    :param graph: the Graph on which to execute the infection model
    :returns: a tuple containing three lists of susceptible, infected and removed nodes.
    Creates lists of nodes in the graph G that are susceptible, infected and removed.
    """
    infected = []  # list of infected nodes
    susceptible = []  # list of susceptible
    removed = []  # list of removed nodes
    for n in graph:
        if graph.node[n]['state'] == State.INFECTED:
            infected.append(n)
        elif graph.node[n]['state'] == State.SUSCEPTIBLE:
            susceptible.append(n)
        else:
            removed.append(n)
    return susceptible, infected, removed  # return the three lists.


def print_infection_stats(graph: nx.Graph) -> None:
    """
    :param graph: the Graph on which to execute the infection model
    Prints the number of susceptible, infected and removed nodes in graph G.
    """
    s, i, r = get_infection_stats(graph)
    print(f'susceptible: {len(s)} Infected: {len(i)} Removed {len(r)}')


def run_spread_simulation(graph: nx.Graph,
                          model: ModelFactory,
                          initial_infection_count: int,
                          run_visualise: bool = False) -> Tuple[NodeList, NodeList, NodeList, int, NodeList]:
    """
    :param graph: the Graph on which to execute the infection model
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
    initially_infected = initialise_infection(graph, initial_infection_count)

    s_results: NodeList = []
    i_results: NodeList = []
    r_results: NodeList = []

    dt = 0
    susceptible, infected, removed = get_infection_stats(graph)

    pos = nx.spring_layout(graph, k=.75)

    while len(infected) > 0:
        execute_one_step(graph, model)  # execute each node in the graph once
        dt += 1  # increase time step
        susceptible, infected, removed = get_infection_stats(graph)  # calculate SIR stats of the current time step
        s_results.append(len(susceptible))  # add S counts to our final results
        i_results.append(len(infected))  # add I counts to our final results
        r_results.append(len(removed))  # add R counts to our final results
        sys.stderr.write(f'\rInfected: {len(infected)} time step: {dt}')
        sys.stderr.flush()

        if run_visualise:  # If run visualise is true, we output the graph to file
            draw_network_to_file(graph, pos, dt, initially_infected)

    return s_results, i_results, r_results, dt, initially_infected  # return our results for plotting


def plot_infection(susceptible: List[int], infected: List[int], removed: List[int], graph: nx.Graph) -> None:
    """
    :param susceptible: time-ordered list from simulation output indicating how susceptible count changes over time
    :param infected: time-ordered list from simulation output indicating how infected count changes over time
    :param removed: time-ordered list from simulation output indicating how removed count changes over time
    :param graph: Graph/Network of statistic to plot
    Creates a plot of the S,I,R output of a spread simulation.
    """
    peak_incidence = max(infected)
    peak_time = infected.index(max(infected))
    total_infected = susceptible[0] - susceptible[-1]

    fig_size = [18, 13]
    plt.rcParams.update({'font.size': 14, 'figure.figsize': fig_size})
    xvalues = range(len(susceptible))
    plt.plot(xvalues, susceptible, color='g', linestyle='-', label='S')
    plt.plot(xvalues, infected, color='b', linestyle='-', label='I')
    plt.plot(xvalues, removed, color='r', linestyle='-', label='R')
    plt.axhline(peak_incidence, color='b', linestyle='--', label='Peak Incidence')
    plt.annotate(str(peak_incidence), xy=(1, peak_incidence + 10), color='b')
    plt.axvline(peak_time, color='b', linestyle=':', label='Peak Time')
    plt.annotate(str(peak_time), xy=(peak_time + 1, 8), color='b')
    plt.axhline(total_infected, color='r', linestyle='--', label='Total Infected')
    plt.annotate(str(total_infected), xy=(1, total_infected + 10), color='r')
    plt.legend()
    plt.xlabel('time step')
    plt.ylabel('Count')
    plt.title('SIR for network size ' + str(graph.order()))
    plt.show()


def draw_network_to_file(graph: nx.Graph, pos: Dict, t: int, initially_infected: NodeList) -> None:
    """
    :param graph: Graph to draw to png file
    :param pos: position defining how to layout graph
    :param t: current timestep of simualtion (used for filename distinction)
    :param initially_infected: list of initially infected nodes
    Draws the current state of the graph G, colouring nodes depending on their state.
    The image is saved to a png file in the images subdirectory.
    """
    # create the layout
    states = []
    for n in graph.nodes():
        if n in initially_infected:
            states.append(3)
        else:
            states.append(graph.nodes[n]['state'].value)
    color_map = colors.ListedColormap(['green', 'blue', 'red', 'yellow'])

    # draw the nodes and the edges (all)
    nx.draw_networkx_nodes(graph, pos, cmap=color_map, alpha=0.5, node_size=170, node_color=states)
    nx.draw_networkx_edges(graph, pos, alpha=0.075)
    plt.savefig(os.path.join(common.FIGURES_FOLDER, f'g{t}.png'))
    plt.clf()


def dump_sir_history(path: str, s: NodeList, i: NodeList, r: NodeList, end_time: int, initial_infected: NodeList
                     ) -> None:
    with open(path, 'w') as file:
        file.write(f'{end_time}\n')
        for param in [s, i, r, initial_infected]:
            file.write(f'{common.join_values(param)}\n')


def plot_sir_model_results() -> None:
    for idx in range(1, 6):
        with open(os.path.join(common.SIR_FOLDER, 'exp_2', f'sir_history_{idx}.txt')) as sir_file:
            time_steps = int(sir_file.readline())
            susceptible = [int(val) for val in sir_file.readline().split()]
            infected = [int(val) for val in sir_file.readline().split()]
            recovered = [int(val) for val in sir_file.readline().split()]

        max_infected = max(infected)

        sir_file.close()

        times = [t for t in range(time_steps)]

        plt.figure()
        plt.plot(times, susceptible, label='S')
        plt.plot(times, infected, label='I')
        plt.plot(times, recovered, label='R')
        plt.hlines(max_infected, 0, time_steps, linestyles='--', label='Peak Infected')
        plt.xlim(0, time_steps)
        plt.xlabel('Time step')
        plt.ylabel('Number of nodes')
        plt.title(r'SIR model propagation with $\alpha = %.2f, \beta = %.2f$' % (0.6, 0.2))
        plt.legend(loc='upper right')
        plt.show()


def main() -> None:
    g: nx.Graph = graph_from_gephi_edge_list(common.REDUCED_GRAPH_PATH)

    for exp_number in range(3, 6):
        # exp_1
        m: ModelFactory = transmission_model_factory(0.05, 0.03)
        number_initial_infections = 10
        reset(g)  # initialise all nodes to susceptible
        susceptible, infected, removed, endtime, ii = run_spread_simulation(g, m, number_initial_infections)

        dump_sir_history(os.path.join(common.SIR_FOLDER, 'exp_1', f'sir_history_{exp_number}.txt'),
                         susceptible, infected, removed, endtime, ii)

        # exp_2
        m = transmission_model_factory(0.6, 0.2)
        number_initial_infections = 100
        reset(g)  # initialise all nodes to susceptible
        susceptible, infected, removed, endtime, ii = run_spread_simulation(g, m, number_initial_infections)
        dump_sir_history(os.path.join(common.SIR_FOLDER, 'exp_2', f'sir_history_{exp_number}.txt'),
                         susceptible, infected, removed, endtime, ii)


if __name__ == '__main__':
    plot_sir_model_results()
