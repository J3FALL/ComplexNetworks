import plotly.graph_objs as go
from plotly.offline import  plot
from scipy.integrate import odeint
from enum import *
import numpy as np, networkx as nx, random

'''
Part of this code written by following authors.
Authors: Michael Lees, Debraj Roy
The MIT License (MIT)

Copyright (c) 2015-2017 Michael Lees, Debraj Roy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

class State(Enum): # define the three states of the nodes.
    Succeptible = 0
    Infected = 1
    Removed = 2


def initialise_infection(G, num_to_infect):
    nodes_to_infect = random.sample(G.nodes(), num_to_infect)
    for n in nodes_to_infect:
        G.nodes[n]['state'] = State.Infected
    return nodes_to_infect

def reset(G):
    nx.set_node_attributes(G, name='state', values=State.Succeptible)


def transmission_model_factory(beta=0.03, alpha=0.05):
    def m(n, G):
        list_of_neighbours_to_infect = []  # list of neighbours will be infect after executing this step
        removeMyself = False  # should I change my state to removed?
        if G.nodes[n]['state'] == State.Infected:
            # infect susceptible neighbours with probability beta
            for k in G.neighbors(n):
                if G.nodes[k]['state'] == State.Succeptible:
                    if random.random() <= beta:  # generate random number between 0 and 1
                        list_of_neighbours_to_infect.append(k)
            if random.random() <= alpha:
                removeMyself = True
        return list_of_neighbours_to_infect, removeMyself
    return m


def apply_infection(G, list_of_newly_infected, list_of_newly_removed):
    for n in list_of_newly_infected:
        G.nodes[n]['state'] = State.Infected
    for n in list_of_newly_removed:
        G.nodes[n]['state'] = State.Removed

def execute_one_step(G, model):
    new_nodes_to_infect = []
    new_nodes_to_remove = []
    for n in G:
        i, remove = model(n, G)
        new_nodes_to_infect = new_nodes_to_infect + i
        if remove:
            new_nodes_to_remove.append(n)
    apply_infection(G, new_nodes_to_infect, new_nodes_to_remove)


def get_infection_stats(G):
    infected = []
    succeptible = []
    removed = []
    for n in G:
        if G.nodes[n]['state'] == State.Infected:
            infected.append(n)
        elif G.nodes[n]['state'] == State.Succeptible:
            succeptible.append(n)
        else:
            removed.append(n)
    return succeptible, infected, removed  # return the three lists.


def run_spread_simulation(G, model, initial_infection_count):
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
    return s_results, i_results, r_results, dt, initially_infected


def diff(sir, t):
    dsdt = - (beta * sir[0] * sir[1])
    didt = (beta * sir[0] * sir[1]) - gamma * sir[1]
    drdt = gamma * sir[1]
    dsirdt = [dsdt, didt, drdt]
    return dsirdt



beta = 0.2 # infection rate
gamma = 0.07 # recovery rate5

G = nx.read_edgelist(('reduced_fixed.csv'), delimiter=',')
reset(G)
m = transmission_model_factory(beta, gamma)
N = len(G.nodes())
I = 10
S = N - I
R = 0
sir0 = (S, I, R)
t = np.linspace(0, 200)
sir = odeint(diff, sir0, t)
S, I, R, endtime, ii = run_spread_simulation(G, m, I)
xvalues = list(range(len(S)))

trace1 = go.Scatter(x=xvalues,y=S, mode='lines', name='S')
trace2 = go.Scatter(x=xvalues,y=I, mode='lines', name='I')
trace3 = go.Scatter(x=xvalues,y=R, mode='lines', name='R')
layout = go.Layout(xaxis=dict(title='Iterations', titlefont=dict(size=25)),
                              yaxis=dict(titlefont=dict(size=25), title='Airports'))
fig = go.Figure(data=[trace1,trace2,trace3], layout=layout)
plot(fig, filename='1')

trace1 = go.Scatter(x=t,y= sir[:, 0], mode='lines', name='S')
trace2 = go.Scatter(x=t,y= sir[:, 1], mode='lines', name='I')
trace3 = go.Scatter(x=t,y= sir[:, 2], mode='lines', name='R')
layout = go.Layout(xaxis=dict(title='Iterations', titlefont=dict(size=25)),
                              yaxis=dict(titlefont=dict(size=25), title='Airports'))
fig = go.Figure(data=[trace1,trace2,trace3], layout=layout)
plot(fig, filename='2')