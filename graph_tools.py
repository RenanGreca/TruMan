from snap import TFIn, TNEANet, DrawGViz, gvlNeato, TIntStrH, PUNGraph, PNEANet, TFOut

import os
import random

color_names = ["green", "red", "blue", "yellow", "purple", "orange", "white", "black"]
const_trust = "Trust"
const_timestamp = "Timestamp"

# Saves the graph to a PNG file
def draw(graph, root, name, directory, colors=None, ids=None):

    draw_colors = TIntStrH()

    if colors and ids:
        for node, component in ids.iteritems():
            draw_colors[node] = color_names[colors[component]]
    else:
        for node in graph.Nodes():
            draw_colors[node.GetId()] = 'white'
        draw_colors[root] = 'green'

    path = os.path.join(directory, 'plots')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(path, name+'.png')

    DrawGViz(graph, gvlNeato, path, name, True, draw_colors)

# 
# def draw_scc(graph, colors, name, directory):
#     node_colors = TIntStrH()

#     for (node, color) in colors.iteritems():
#         node_colors[node] = color_names[color]

#     DrawGViz(graph, gvlNeato, directory+name+".png", name, True, node_colors)

# Builds a component graph from the result of Tarjan's algorithm
def build_component_graph(graph, component_map):
    C = PUNGraph.New()

    for (_, component_id) in component_map.iteritems():
        if not C.IsNode(component_id):
            C.AddNode(component_id)

    for (a, u) in component_map.iteritems():
        for (b, v) in component_map.iteritems():
            # a, b are nodes of the original graph
            # v, u are nodes of the component graph
            if u == v or C.IsEdge(u, v):
                continue

            if graph.IsEdge(a, b):
                C.AddEdge(u, v)
    
    return C

# Merges two graphs
def merge(A, B):
    for edge_b in B.Edges():
        u = edge_b.GetSrcNId()
        v = edge_b.GetDstNId()

        if not A.IsNode(u):
            A.AddNode(u)
        if not A.IsNode(v):
            A.AddNode(v)
        if not A.IsEdge(u, v):
            edge_a = A.AddEdge(u, v)

            trust = B.GetFltAttrDatE(edge_b, const_trust)
            A.AddFltAttrDatE(edge_a, trust, const_trust)

            ts = B.GetIntAttrDatE(edge_b, const_timestamp)
            A.AddIntAttrDatE(edge_a, ts, const_timestamp)

        else:
            edge_a = A.GetEId(u, v)

            timestamp_a = A.GetIntAttrDatE(edge_a, const_timestamp)
            timestamp_b = B.GetIntAttrDatE(edge_b, const_timestamp)

            trust_b = B.GetFltAttrDatE(edge_b, const_trust)

            # If B's information is more recent, update A.
            if timestamp_b > timestamp_a:
                A.AddFltAttrDatE(edge_a, trust_b, const_trust)
                A.AddIntAttrDatE(edge_a, timestamp_b, const_timestamp)

# Discards stale edges.
def age_information(graph, iter_no, aging_rate):
    for edge in graph.Edges():
        u = edge.GetSrcNId()
        v = edge.GetDstNId()

        timestamp = graph.GetIntAttrDatE(edge, const_timestamp)

        # If the information is older than the aging rate, discard the edge.
        if iter_no-aging_rate > timestamp:
            graph.DelAttrDatE(edge, const_trust)
            graph.DelAttrDatE(edge, const_timestamp)
            graph.DelEdge(u, v)

# prepare graph attributes and first graph file
def prepare_initial_graph(T, graphs_dir):
    graph_0 = os.path.join(graphs_dir,'0')

    if not os.path.exists(graph_0):
        os.makedirs(graph_0)

    node_labels = []
    for node in T.Nodes():
        node_labels.append(node.GetId())

        # Creates a new graph with a single node
        trust_graph = PNEANet.New()
        trust_graph.AddNode(node.GetId())
        # Establishes edge attributes for trust and timestamp
        trust_graph.AddFltAttrE(const_trust)
        trust_graph.AddIntAttrE(const_timestamp)

        path = os.path.join(graph_0, 'trust_'+str(node.GetId())+'.graph')
        FOut = TFOut(path)
        trust_graph.Save(FOut)
        FOut.Flush()
    
    return node_labels