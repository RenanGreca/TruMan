## Tarjan's strongly connected components algorithm
# References:
# https://epubs.siam.org/doi/abs/10.1137/0201010
# https://en.wikipedia.org/wiki/Tarjan%27s_strongly_connected_components_algorithm

from snap import PNGraph, PNEANet, TFIn, TNEANet, TIntStrH, DrawGViz, gvlNeato
import os

import graph_tools

# prepares data structures and runs the core algorithm
def tarjan(trust_graph, thresh):
    global node_count
    global component_count
    global index
    global lowlink
    global stack
    global component
    global threshold

    component = {}      # maps nodes to components
    index = {}          # maps nodes to the index given during Tarjan execution
    lowlink = {}        # maps nodes to the lowest-indexed node reachable from it
    stack = []

    node_count = 0      # number of nodes visited
    component_count = 0 # number of components found

    threshold = thresh  # sensitivity of the algorithm

    # Set data structures
    # Before running the algorithm, each node has -1 as index, lowlink and component
    for node in trust_graph.Nodes():
        n_id = node.GetId()
        component[n_id] = -1
        index[n_id] = -1
        lowlink[n_id] = -1

    # Visit each unvisited node
    for node in trust_graph.Nodes():
        n_id = node.GetId()
        if index[n_id] == -1:
            visit(n_id, trust_graph)
        
    return (component, component_count)

def visit(u, trust_graph):
    global node_count
    global component_count
    global index
    global lowlink
    global stack
    global component
    global threshold

    index[u] = node_count
    lowlink[u] = node_count
    node_count = node_count + 1
    stack.append(u)

    U = trust_graph.GetNI(u)

    # Visit all nodes v which are neighbors of u
    for v in U.GetOutEdges():

        eid_u = trust_graph.GetEId(u, v)
        trust_u = trust_graph.GetFltAttrDatE(eid_u, "Trust")
        
        # Sensitivity threshold of the algorithm. 
        # A number closer to 1 makes it more restrictive.
        if trust_u < threshold:
            continue

        # If v is unvisited, visit it.
        if index[v] == -1:
            visit(v, trust_graph)
            lowlink[u] = min(lowlink[u], lowlink[v])
        elif v in stack:
            lowlink[u] = min(lowlink[u], index[v])

    # If u is the lowest node reachable from itself, form a component.
    if lowlink[u] == index[u]:
        while True:
            w = stack.pop()
            component[w] = component_count
            if (w == u):
                break
        component_count += 1

if __name__ == '__main__':

    # Sample graph for testing.
    G = PNEANet.New()
    # for i in range(0,7):
    #     G.AddNode(i)

    edges = [(0,1), (1,0), (1,2), (1,5), (2,3), (3,4), (4,2), (5,0), (5,6)]
    for edge in edges:
        u = edge[0]
        v = edge[1]

        if not G.IsNode(u):
            G.AddNode(u)
        if not G.IsNode(v):
            G.AddNode(v)

        if not G.IsEdge(u, v):
            eid = G.AddEdge(u,v)
            G.AddFltAttrDatE(eid, 1, "Trust")
        
    (ids, n_component) = tarjan(G, 0.5)
    print n_component, "components found"
    print ids