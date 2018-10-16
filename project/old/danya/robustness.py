import pandas as pd, plotly.graph_objs as go, numpy as np, networkx as nx, powerlaw, collections, random
from plotly import tools
from operator import add
from plotly.offline import download_plotlyjs, init_notebook_mode, iplot, plot

'''
Part of this code contains work of the following authors: 
The MIT License (MIT)

Copyright (c) 2015 Michael Lees, Debraj Roy

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'''


def diameter_ave_path_length(G):
    max_path_length = 0
    total = 0.0
    for n in G:
        path_length=nx.single_source_shortest_path_length(G, n)
        total += sum(path_length.values())
        if max(path_length.values()) > max_path_length:
            max_path_length = max(path_length.values())
    try:
        avg_path_length = total / (G.order()*(G.order() - 1))
    except ZeroDivisionError:
        avg_path_length = 0.0
    return max_path_length, avg_path_length


def fail(G):
    n = random.choice(list(G.nodes()))
    G.remove_node(n)

def attack_degree(G):
    degrees = dict(G.degree())
    max_degree = max(degrees.values())
    max_keys = [k for k, v in degrees.items() if
                v == max_degree]
    G.remove_node(max_keys[0])


def attack_betweenness(G):
    betweenness = dict(nx.betweenness_centrality(G))
    max_betweenenss = max(betweenness.values())
    max_keys = [k for k, v in betweenness.items() if
                v == max_betweenenss]
    G.remove_node(max_keys[0])

def a_network_statistics(n):
    Gcc = sorted(nx.connected_component_subgraphs(n), key=len, reverse=True)
    G0 = Gcc[0]
    d, l = diameter_ave_path_length(G0)
    s = float(G0.order()) / float(NetworkSize)
    e = nx.density(G0)
    avd = float(G0.size()) / float(NetworkSize)
    return d, l, s, e, avd

def all_network_statistics(nw_list):
    diameters = []
    path_lengths = []
    S = []
    densities = []
    average_degrees = []
    for n in nw_list:
        d,l,s,e,avd = a_network_statistics(n)
        diameters.append(d)
        path_lengths.append(l)
        S.append(s)
        densities.append(e)
        average_degrees.append(avd)
    return (diameters, path_lengths, S, densities, avd)


def experiments(networks, removals, run_fail=True, measure_every_X_removals=1):
    ave_diameters = []
    ave_path_lengths = []
    ave_S = []
    for x in range(removals):
        for n in networks:
            if run_fail:
                fail(n)
            else:
                attack_degree(n)
        if x % measure_every_X_removals == 0:
            d, l, s, e, avd = all_network_statistics(networks)
            ave_diameters.append(np.mean(d))
            ave_path_lengths.append(np.mean(l))
            ave_S.append(np.mean(s))
    return ave_diameters, ave_path_lengths, ave_S

dut_f = {}
dut_a = {}
n = 1
for i in range(n):
    with open('edgelist.csv', 'rb') as file_handle:
        next(file_handle, '')   # skip the header line (NOTE the first list in the CSV file doesn't contain an edge)
        G = nx.read_edgelist(file_handle, delimiter=',',
                             nodetype=str, data=(('weight', float),), encoding="utf-8")
    G_c = G.copy()
    NetworkSize = G.order()
    dut_f[i] = [experiments([G], NetworkSize, run_fail=True, measure_every_X_removals=200)]
    dut_a[i] = [experiments([G_c], NetworkSize, run_fail=False, measure_every_X_removals=200)]

def get_avg(dut):
    ms = {0:[0]*len(list(dut.values())[0][0][0]),1:[0]*len(list(dut.values())[0][0][1]),2:[0]*len(list(dut.values())[0][0][2])}
    stds =  [[],[],[]]
    for k,i in dut.items():
            ms[0] = list(map(add,ms[0],i[0][0]))
            ms[1] = list(map(add,ms[1],i[0][1]))
            ms[2] = list(map(add,ms[2],i[0][2]))
            stds[0].append(i[0][0])
            stds[1].append(i[0][1])
            stds[2].append(i[0][2])

    for i in ms.keys():
        ms[i] = [x/len(dut.keys()) for x in ms[i]]

    stds[0] = np.std(stds[0],axis=0)
    stds[1] = np.std(stds[1],axis=0)
    stds[2] = np.std(stds[2],axis=0)
    return ms,stds
attack,std_a = get_avg(dut_a)
failure, std_f = get_avg(dut_f)

xvalues = [(float(x)/float(NetworkSize)) * 200 for x in range(len(failure[1]))]

trace1 = go.Scatter(x=xvalues,y=failure[0], error_y = dict(type='data',array = std_f[0], visible=True), mode='lines+markers', name='Failure')
trace2 = go.Scatter(x=xvalues,y=attack[0],error_y = dict(type='data',array = std_a[0], visible=True), mode='lines+markers', name='Attack')
layout = go.Layout(xaxis=dict(title='Fraction of removed nodes', titlefont=dict(size=25)),
                              yaxis=dict(titlefont=dict(size=25), title='Diameter'))
fig = go.Figure(data=[trace1,trace2], layout=layout)
plot(fig, filename='diameter.html')

trace1 = go.Scatter(x=xvalues,y=failure[1],error_y = dict(type='data',array = std_f[1], visible=True), mode='lines+markers', name='Failure')
trace2 = go.Scatter(x=xvalues,y=attack[1],error_y = dict(type='data',array = std_a[1], visible=True), mode='lines+markers', name='Attack')
layout = go.Layout(xaxis=dict(title='Fraction of removed nodes', titlefont=dict(size=25)),
                              yaxis=dict(titlefont=dict(size=25), title='Path length'))
fig = go.Figure(data=[trace1,trace2], layout=layout)
plot(fig, filename='path_length.html')

trace1 = go.Scatter(x=xvalues,y=failure[2], mode='lines+markers', name='Failure')
trace2 = go.Scatter(x=xvalues,y=attack[2], mode='lines+markers', name='Attack')
layout = go.Layout(xaxis=dict(title='Fraction of removed nodes', titlefont=dict(size=25)),
                              yaxis=dict(titlefont=dict(size=25), title='Size of giant component'))
fig = go.Figure(data=[trace1,trace2], layout=layout)
plot(fig, filename='gc.html')