## TruMan: Trust Management for Vehicular Network
# References:
# https://github.com/renangreca/truman
# https://ieeexplore.ieee.org/abstract/document/8538683
# https://www.academia.edu/37710449/TruMan_Trust_Management_for_Vehicular_Networks
# https://www.acervodigital.ufpr.br/handle/1884/57615

# Graph library
from snap import TIntStrH, DrawGViz, gvlNeato, TFIn, TNEANet, PUNGraph, LoadEdgeList, TFOut, PNGraph, PNEANet
import numpy as np

# Multiprocessing tools
import multiprocessing
from functools import partial
from contextlib import contextmanager

# Other helpers
import os
import shutil
import csv
import argparse
import random

# Modules
from tarjan import tarjan
from graph_coloring import graph_coloring, find_largest_color
import graph_tools

# Argument parser
parser = argparse.ArgumentParser(description='Distributed network expansion.')
parser.add_argument('-i', '--input_dir', type=str, required=True,
                    help='(str) Directory containing mobility data. Should contain output from process_report.py.')
parser.add_argument('-o', '--output_dir', type=str, required=True,
                    help='(str) Directory for output. Should contain output from generate_weights.py.')
parser.add_argument('-p', '--parallel', default=False, const=True, action='store_const',
                    help='Activate CPU parallelization. Better for large number of nodes.')
parser.add_argument('-s', '--step', type=int, default=1,
                    help='(int) Multiplier for the iterator. Sometimes large steps produce good-enough results faster. Default: 1.')
parser.add_argument('-t', '--threshold', type=float, default=0.5,
                    help='(float [0.0, 1.0]) Trust threshold for determining strongly connected components. Default: 0.5.')
parser.add_argument('-a', '--aging_rate', type=int, default=0,
                    help='(int) The number of iterations it takes for trust data to be discarded. Default: data is never discarded.')
parser.add_argument('--draw_graphs', default=False, const=True, action='store_const',
                    help='Draw the trust graph at every iteration.')

# Constants for edge attribute labels
const_trust = "Trust"
const_timestamp = "Timestamp"


# Marks all nodes that are not in the largest color as malicious
def detect_malicious(components, colors, largest_color):
    dmalicious = []
    for node, component in components.iteritems():
        if colors[component] != largest_color:
            dmalicious.append(node)

    dmalicious.sort()

    return dmalicious


# Reviews detections and stores them in a results file
def analyze_results(directory, iter_no):

    results_path = os.path.join(directory, 'results')
    if not os.path.exists(results_path):
        os.makedirs(results_path)

    results_file = os.path.join(results_path, 'results_'+str(iter_no)+'.csv')
    f = open(results_file, 'w')
    writer = csv.writer(f)

    writer.writerow(["Node ID", "Detected", "True Positives",
                     "False Positives", "False Negatives"])

    detected_correct = []

    for node in node_labels:
        # Load the node's detection results
        detected_malicious = []
        path = os.path.join(graphs_dir, str(iter_no), 'detected_'+str(node)+'.nodes')
        df = open(path, 'r')
        for line in df:
            detected_malicious.append(int(line))
        df.close()

        total_detected = 0
        true_positives = 0
        false_positives = 0
        false_negatives = 0

        # Load the node's trust graph
        path = os.path.join(graphs_dir, str(iter_no), 'trust_'+str(node)+'.graph')
        FIn = TFIn(path)
        trust_graph = TNEANet.Load(FIn)

        total_detected = trust_graph.GetNodes()

        for detected in detected_malicious:
            if detected in malicious:
                # The node was detected malicious and is actually malicious
                true_positives += 1
            else:
                # The node was detected malicious but is not actually malicious
                false_positives += 1

        for m in malicious:
            if m not in detected_malicious:
                # The node was not detected malicious but is actually malicious
                false_negatives += 1

        # Write results into CSV
        writer.writerow([str(node), str(total_detected), str(true_positives),
            str(false_positives), str(false_negatives)])

        detected_correct.append(true_positives)

        trust_graph.Clr()

    f.close()

    # Number of true positives for each node
    return detected_correct

def expand_edge(graph, iter_no, prev_iter, u, v):
    # Load the previous iteration of the other node
    path = graphs_dir+'/'+str(prev_iter)+'/trust_'+str(v)+'.graph'
    FIn = TFIn(path)
    dest_trust = TNEANet.Load(FIn)

    # Add node and edge to graph if necessary
    if not graph.IsNode(v):
        graph.AddNode(v)
    if not graph.IsEdge(u,v):
        eid = graph.AddEdge(u,v)
        graph.AddFltAttrDatE(eid, 0.5, const_trust)
    eid = graph.GetEId(u,v)

    if u in malicious:
        # If truster (u) is malicious, the trust value is random
        trust = random.uniform(0, 1)
        graph.AddFltAttrDatE(eid, trust, const_trust)

    else:
        trust = graph.GetFltAttrDatE(eid, const_trust)
        # Update trust value according to the trustee (v)
        if v in malicious:
            trust_value = trust-0.1
            if trust_value < 0.0:
                trust_value = 0.0
            graph.AddFltAttrDatE(eid, trust_value, const_trust)
        else:
            trust_value = trust+0.1
            if trust_value > 1.0:
                trust_value = 1.0
            graph.AddFltAttrDatE(eid, trust_value, const_trust)
    
    ts = iter_no
    graph.AddIntAttrDatE(eid, ts, const_timestamp)

    if v not in malicious:
        graph_tools.merge(graph, dest_trust)

    dest_trust.Clr()

    return graph


def expand_network(node_index, iter_no):
    global input_dir
    global graphs_dir

    # global aging_timestamp

    prev_iter = iter_no-step

    # Load graph from mobility data
    graph_file = os.path.join(input_dir,str(iter_no)+'0.txt')
    if not os.path.isfile(graph_file):
        print 'Graph file not found:', graph_file
        return 0
    G = LoadEdgeList(PUNGraph, graph_file, 0, 1)

    # Load previous iteration's trust graph
    path = os.path.join(graphs_dir,str(prev_iter),'trust_'+str(node_index)+'.graph')
    FIn = TFIn(path)
    new_trust = TNEANet.Load(FIn)

    # Look for edges containing the node
    for edge in G.Edges():
        u = edge.GetSrcNId()
        v = edge.GetDstNId()

        # Since the topology is undirected, the node in question can be either end of the edge.
        if node_index == u:
            new_trust = expand_edge(new_trust, iter_no, prev_iter, u, v)

        if node_index == v:
            new_trust = expand_edge(new_trust, iter_no, prev_iter, v, u)

    # TODO: information aging
    # age information before processing
    if args.aging_rate > 0:
        graph_tools.age_information(new_trust, iter_no, args.aging_rate)

    # Save current iteration's trust graph
    path = os.path.join(graphs_dir,str(iter_no),'trust_'+str(node_index)+'.graph')
    FOut = TFOut(path)
    new_trust.Save(FOut)
    FOut.Flush()

    # Run Tarjan's algorithm and generate component graph
    (components, _) = tarjan(new_trust, args.threshold)
    C = graph_tools.build_component_graph(new_trust, components)

    # Run graph coloring algorithm and detect malicious nodes
    (colors, color_count) = graph_coloring(C)
    largest_color = find_largest_color(components, colors, color_count)
    dmalicious = detect_malicious(components, colors, largest_color)

    # Save detected malicious nodes
    path = os.path.join(graphs_dir,str(iter_no),'detected_'+str(node_index)+'.nodes')
    f = open(path, 'w')
    for node in dmalicious:
        f.write(str(node)+'\n')
    f.close()

    # Draw graph if requested
    if node_index == 3 and args.draw_graphs:
        # TODO: correct output path
        graph_tools.draw(new_trust, 3, 'trust_'+str(iter_no), output_dir, colors, ids=components)

    G.Clr()
    new_trust.Clr()
    C.Clr()

# Multiprocessing helper
@contextmanager
def poolcontext(*args, **kwargs):
    pool = multiprocessing.Pool(*args, **kwargs)
    yield pool
    pool.terminate()


def iteration(graphs_dir, iter_no):
    global T

    print " "
    print "Iteration ", iter_no

    # Create directory for iteration i
    iter_path = os.path.join(graphs_dir,str(iter_no))
    if not os.path.exists(iter_path):
        os.makedirs(iter_path)

    # Delete directory for iteration i-3
    prev_iter_path = os.path.join(graphs_dir, str(iter_no - step*3))
    if os.path.exists(prev_iter_path):
        shutil.rmtree(prev_iter_path)

    # Run expand_network concurrently or sequentially
    if args.parallel:
        num_cores = multiprocessing.cpu_count()
        with poolcontext(processes=num_cores) as pool:
            pool.map(partial(expand_network, iter_no=iter_no), node_labels)
    else:
        for node_index in node_labels:
            expand_network(node_index, iter_no)

    detected_correct = analyze_results(output_dir, iter_no)

    rows = []
    for dmalicious in detected_correct:
        rows.append(dmalicious)

    nrows = np.array(rows)
    avg = np.mean(nrows, axis=0)
    std = np.std(nrows, axis=0)

    print "Average number of malicious found: ", avg
    # print "Number of malicious found by node 0: ", len(detected_malicious[0])
    print "Total number of malicious nodes: ", len(malicious)
    percent = round(float(avg)/float(len(malicious))*100, 2)
    print "Percent of malicious found: ", percent,"%"

# Determine how many iterations to run according to input directory contents
def find_number_of_iterations(input_dir):
    number_of_iterations = 0
    for _, _, files in os.walk(input_dir):
        for name in files:
            if ".txt" in name:
                number_of_iterations += 1
    return number_of_iterations

# Core method. Prepares global variables and runs iterations.
def trust_snap():
    global T

    global malicious

    global node_labels
    global graphs_dir

    # global aging_timestamp

    # Prepare global variables
    # aging_timestamp = aging # TODO: does not need to be global?
    
    graphs_dir = os.path.join(output_dir,'graphs')

    # Store the ground truth malicious nodes
    malicious = []
    f = open(os.path.join(output_dir,'ground_truth.nodes'), 'r')
    for line in f:
        malicious.append(int(line))
    f.close()

    # Creates a directed graph with all edges from the file
    print "Importing network for trust"
    T = LoadEdgeList(PUNGraph, os.path.join(output_dir,"topology.edges"), 0, 1)
    print "Topology network has ", T.GetNodes(), " nodes and ", T.GetEdges(), " edges."

    node_labels = graph_tools.prepare_initial_graph(T, graphs_dir)

    number_of_iterations = find_number_of_iterations(input_dir)
    for i in range(1, number_of_iterations/step):
        iteration(graphs_dir, i*step)

        # TODO: add malicious nodes during execution
        # if i == 450: # when?
        #     extra = 0 # how many?
        #     for node in node_labels:
        #         if node not in malicious:
        #             malicious.append(node)
        #             extra += 1
        #             print "added "+str(node)+" to malicious list"
        #             if extra == extra_malicious:
        #                 break

# Topology graph
T = PUNGraph.New()

# ground truth
malicious = []

node_labels = []

# aging_timestamp = 0 # TODO: should be a parameter

# input_dir = ''
# graphs_dir = ''

if __name__ == '__main__':
    args = parser.parse_args()
    step = args.step
    input_dir = args.input_dir
    output_dir = args.output_dir

    if args.threshold < 0.0 or args.threshold > 1.0:
        print "Threshold should be between 0.0 and 1.0."
        exit(1)

    trust_snap()
