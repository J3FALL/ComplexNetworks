import collections
import networkx as nx
import numpy as np
import plotly.graph_objs as go
import powerlaw
from plotly.offline import plot

G = nx.read_edgelist('reduced_fixed.csv', delimiter=',')
print('Nodes', len(G.nodes()))
print('Edges', len(G.edges()))
print('Assortativity', nx.degree_assortativity_coefficient(G))
print('Average Clust', nx.average_clustering(G.to_undirected()))
print('Degree', np.mean([x for x in nx.degree(G).values()]))
# print('Diameter', nx.diameter(G))
all_degrees = dict(G.degree())
cluster_coeffs = dict(nx.clustering(G))
# bet_cen = dict(nx.betweenness_centrality(G))
# clo_cen = dict(nx.closeness_centrality(G))
# short_paths = []
# length = dict(nx.all_pairs_shortest_path_length(G))
# for x in length:
#     for y in length[x]:
#         short_paths.append(length[x][y])
# short_paths = list(filter(lambda a: a != 0, short_paths))
# cluster_coeffs = dict(nx.clustering(G))

# all_degrees = dict(G.degree())
# all_degree_counts = dict(collections.Counter(list(all_degrees.values())))
# fit = powerlaw.Fit(list(all_degree_counts.values()))
# print("Sigma: ", fit.power_law.alpha)
# print("Xmin: ", fit.power_law.xmin)
# x = sorted(list(set(all_degrees.values())))
# y = [list(all_degrees.values()).count(a) / len(all_degrees.values()) for a in x]
# y1 = [y[0]]
# for i in range(1, len(y)):
#     y1.append(y1[i - 1] + y[i])
# trace1 = go.Scatter(x=x, y=y, mode='markers', name='Distribution')
# trace2 = go.Scatter(x=x, y=[a ** -fit.power_law.alpha for a in (x)], mode='lines',
#                     name='Theta = ' + str(fit.power_law.alpha)[:5])
# layout = go.Layout(xaxis=dict(type='log', title='Degree (log)', titlefont=dict(size=25)),
#                    yaxis=dict(type='log', titlefont=dict(size=25), title='Fraction of nodes (log)'))
# fig = go.Figure(data=[trace1, trace2], layout=layout)
# plot(fig)
#

def plot1(d, xax):
    x = sorted(list(set(d)))
    y = [list(d).count(a) / len(d) for a in x]
    trace1 = go.Scatter(x=x, y=y, mode='markers')
    layout = go.Layout(xaxis=dict(type='log', tickfont=dict(size=17), title=xax + '(log)', titlefont=dict(size=25)),
                       yaxis=dict(type='log', tickfont=dict(size=17),
                                  titlefont=dict(size=25), title='Fraction of nodes (log)'))
    fig = go.Figure(data=[trace1], layout=layout)
    plot(fig, filename=xax)


# plot1(cluster_coeffs.values(), 'Clustering coefficient')
# plot1(short_paths, 'Shortest path')
# plot1(bet_cen.values(), 'Betweness centrality')
# plot1(clo_cen.values(), 'Closeness centrality')

G = nx.extended_barabasi_albert_graph(3286, 1, 0.82, 0.07)
print('Assortativity', nx.degree_assortativity_coefficient(G))
print('Average Clust', nx.average_clustering(G.to_undirected()))
print('Degree', np.mean([x[1] for x in nx.degree(G)]))
print('Diameter', nx.diameter(G))

all_degrees = dict(G.degree())
all_degree_counts = dict(collections.Counter(list(all_degrees.values())))
fit = powerlaw.Fit(list(all_degree_counts.values()))
print("Sigma: ", fit.power_law.alpha)
print("Xmin: ", fit.power_law.xmin)
x = sorted(list(set(all_degrees.values())))
y = [list(all_degrees.values()).count(a) / len(all_degrees.values()) for a in x]
y1 = [y[0]]
for i in range(1, len(y)):
    y1.append(y1[i - 1] + y[i])
trace1 = go.Scatter(x=x, y=y, mode='markers', name='Distribution')
trace2 = go.Scatter(x=x, y=[a ** -fit.power_law.alpha for a in (x)], mode='lines',
                    name='Theta = ' + str(fit.power_law.alpha)[:5])
layout = go.Layout(xaxis=dict(type='log', title='Degree (log)', titlefont=dict(size=25)),
                   yaxis=dict(type='log', titlefont=dict(size=25), title='Fraction of nodes (log)'))
fig = go.Figure(data=[trace1, trace2], layout=layout)
plot(fig)
