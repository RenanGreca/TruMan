from snap import DrawGViz, gvlNeato, LoadEdgeList, PUNGraph, PNGraph, SaveEdgeList
import os
import argparse
import random
from datetime import date

parser = argparse.ArgumentParser(description='Transform an undirected graph into a directed one based on a percentage of malicious nodes.')
parser.add_argument('-i', '--input_dir', type=str, required=True,
                    help='Input directory - output of process_report.py')
parser.add_argument('-o', '--output_dir', type=str, required=True,
                    help='Output directory - input of truman.py')
parser.add_argument('-m', '--malicious_percentage', type=float, required=True,
                    help='Percentage of malicious nodes [0-50]')
parser.add_argument('--draw_graph', default=False, const=True, action='store_const',
                    help='Plot graph topology')

# Saves the graph to a PNG file
def draw_graph(graph, directory, name):
    image_file = os.path.join(directory, name+'.png')
    DrawGViz(graph, gvlNeato, image_file, name, True)

# Adds an edge between two nodes according to their maliciousness
def add_edge(T, malicious, a, b):
    if a in malicious:
        # If truster is malicious, the value is random
        trust = random.randint(0,1)
        if trust:
            T.AddEdge(a,b)
    else:
        # If trustee is not malicious, create edge
        if b not in malicious:
            T.AddEdge(a,b)


def generate_weights(input_dir, output_dir, malicious_number, should_draw_graph=False):

    print "importing network"

    # Create an undirected graph with all edges from the files
    Graph = PUNGraph.New()
    for graph_file in os.listdir(input_dir):
        graph = LoadEdgeList(PUNGraph, input_dir+'/'+graph_file, 0, 1)

        for edge in graph.Edges():
            u = edge.GetSrcNId()
            v = edge.GetDstNId()

            if not Graph.IsNode(u):
                Graph.AddNode(u)
            if not Graph.IsNode(v):
                Graph.AddNode(v)
            if not Graph.IsEdge(u,v):
                Graph.AddEdge(u,v)

    # Shuffle nodes and separate malicious ones
    nodes = []
    for node in Graph.Nodes():
        nodes.append(node.GetId())
    random.shuffle(nodes)
    segment = int(len(nodes)*(malicious_number/100))
    malicious = nodes[:segment]

    # print 'building trust graph'
    # # Builds the new trust graph
    # Trust_Graph = PNGraph.New()
    # for edge in Graph.Edges():
    #     u = edge.GetSrcNId()
    #     v = edge.GetDstNId()

    #     if not Trust_Graph.IsNode(u):
    #         Trust_Graph.AddNode(u)
    #     if not Trust_Graph.IsNode(v):
    #         Trust_Graph.AddNode(v)

    #     # Add edges both ways according to maliciousness
    #     add_edge(Trust_Graph, malicious, u, v)
    #     add_edge(Trust_Graph, malicious, v, u)
    
    # if should_draw_graph:
    #     print 'drawing graph'
    #     draw_graph(Trust_Graph, output_dir, 'trust')

    # print 'saving output files...'
    # trust_edges = os.path.join(output_dir, 'trust.edges')
    # SaveEdgeList(Trust_Graph, trust_edges)
    # print 'saved trust'
    topology_edges = os.path.join(output_dir, 'topology.edges')
    SaveEdgeList(Graph, topology_edges)
    print 'saved topology'

    malicious.sort()
    ground_truth = os.path.join(output_dir, 'ground_truth.nodes')
    f = open(ground_truth, 'w')
    for node in malicious:
        f.write(str(node)+'\n')
    f.close()
    print 'saved ground truth'


if __name__ == '__main__':

    args = parser.parse_args()
    if args.malicious_percentage < 0 or args.malicious_percentage > 50:
        print "Invalid malicious_percentage argument"
        exit(1)

    graph_name = os.path.basename(args.input_dir)
    output_dir = os.path.join(args.output_dir, graph_name, str(args.malicious_percentage)+"%")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generate_weights(args.input_dir, output_dir, args.malicious_percentage, should_draw_graph=args.draw_graph)
