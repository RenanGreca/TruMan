from snap import PUNGraph

# Finds the color with the most number of nodes.
def find_largest_color(components, colors, n_color):
    color_numbers = [0]*(n_color)

    for _, component in components.iteritems():
        color_numbers[colors[component]] += 1

    largest = 0
    for c_id in range(0, len(color_numbers)):
        if color_numbers[c_id] > color_numbers[largest]:
            largest = c_id
    
    return largest

# Sort edges according to nodes' IDs.
def sort_edges(c_edges):
    edges = []
    for edge in c_edges:
        u = edge.GetSrcNId()
        v = edge.GetDstNId()
        edges.append((u, v))
    edges.sort(key=lambda tup: (tup[0],tup[1]))

    return edges

# Graph coloring algorithm [Mittal et al, 2011]
# Reference: https://www.computer.org/csdl/proceedings/csnt/2011/4437/00/4437a638-abs.html
def graph_coloring(G):
    # initialize data structures
    colors = {}
    for node in G.Nodes():
        colors[node.GetId()] = 0

    edges = sort_edges(G.Edges())
    
    d = 0
    for edge in edges:
        u = edge[0]
        v = edge[1]

        if colors[u] == colors[v]:
            if colors[v] == d:
                d += 1
            colors[v] = d

    d += 1
    return (colors, d)

if __name__ == '__main__':

    # Sample graph for testing.
    G = PUNGraph.New()

    for i in range(0,7):
        G.AddNode(i)
    
    eid = G.AddEdge(0,1)
    eid = G.AddEdge(1,2)
    eid = G.AddEdge(1,4)
    eid = G.AddEdge(1,5)
    eid = G.AddEdge(2,3)
    eid = G.AddEdge(3,4)
    eid = G.AddEdge(4,2)
    eid = G.AddEdge(5,0)
    eid = G.AddEdge(5,6)

    result = graph_coloring(G)
    print(result)