import argparse
import os
import csv
import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser(description='Tests several networks with different malicious counts.')
parser.add_argument('-d', '--directory', type=str, required=True,
                    help='Directory containing the edges files')
parser.add_argument('-p', '--parallel', default=False, const=True, action='store_const',
                    help='Activate CPU parallelization')

malicious_numbers = [#0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,
                     # 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0,
                     10.0]#, 20.0, 30.0, 40.0, 50.0]

scenarios = [30]
numbers = [10.0]
# numbers = [1.0, 5.0, 10.0, 20.0, 30.0, 40.0, 50.0]

# scenarios = [9, 26, 44]
# scenarios = [12, 36, 60]
# scenarios = [50]#, 30, 50] #, 100, 150, 200, 250, 300]
# scenarios = [350, 400]

colors = ['b', 'g', 'r', 'm', 'c', 'y', 'k']
color_index = 0
#
# def plot(iterations, deviations, name, color):
#     a = []
#     for i in range(1, len(iterations)+1):
#         a.append(i)
#     x = np.array(a)
#     # x_axis = np.linspace(30000, 60000, 10)
#     y = np.array(iterations)
#     dev = np.array(deviations)
#
#     # fig = plt.figure(figsize=(11,8))
#     # ax1 = fig.add_subplot(111)
#
#     # for i in range(0, len(labels)):
#         # ax1.plot(x_axis, y_stack[i,:], label=labels[i], color='c', marker='o')
#
#     plt.plot(x, y, label=name, color=color, marker='o')
#     plt.fill_between(x, y-dev, y+dev, alpha=0.3, edgecolor=color, facecolor=color)
#     # ax1.plot(builds, y_stack[1,:], label='Component 2', color='g', marker='o')
#     # ax1.plot(builds, y_stack[2,:], label='Component 3', color='r', marker='o')
#     # ax1.plot(builds, y_stack[3,:], label='Component 4', color='b', marker='o')
#
#     # plt.xticks(x)
#     plt.xlabel('Iterations')
#
#     # plt.xticks(x_axis, labels)
#     plt.grid('on')


def full_plot(avgs_dt, devs_dt, avgs_tp, devs_tp,
              avgs_fp, devs_fp, avgs_fn, devs_fn,
              list_gt, graph_name):
    a = []
    for i in range(1, len(avgs_dt)+1):
        a.append(i*10)

    x = np.array(a)
    dt = np.array(avgs_dt)
    ddt = np.array(devs_dt)

    tp = np.array(avgs_tp)
    dtp = np.array(devs_tp)

    fp = np.array(avgs_fp)
    dfp = np.array(devs_fp)

    fn = np.array(avgs_fn)
    dfn = np.array(devs_fn)

    gt = np.array(list_gt)

    color = 0
    plt.plot(x, dt, label='dt', color=colors[color], marker='')
    plt.fill_between(x, dt-ddt, dt+ddt, alpha=0.3, edgecolor=colors[color], facecolor=colors[color])
    color += 1

    plt.plot(x, tp, label='tp', color=colors[color], marker='')
    plt.fill_between(x, tp-dtp, tp+dtp, alpha=0.3, edgecolor=colors[color], facecolor=colors[color])
    color += 1

    plt.plot(x, fp, label='fp', color=colors[color], marker='')
    plt.fill_between(x, fp-dfp, fp+dfp, alpha=0.3, edgecolor=colors[color], facecolor=colors[color])
    color += 1

    

    plt.plot(x, gt, label='gt', color=colors[color], marker='', alpha=0.5)
    color += 1

    plt.plot(x, fn, label='fn', color=colors[color], marker='')
    plt.fill_between(x, fn-dfn, fn+dfn, alpha=0.3, edgecolor=colors[color], facecolor=colors[color])
    color += 1

    # plt.xlabel('Iterations')


def calculate_detected(results_dir, results_file, total_nodes):
    if total_nodes == 0:
        print "total_nodes is 0"
        return 100.00, 0.00

    rows = []
    with open(results_dir+"/"+results_file, 'rb') as csvfile:
        csv_rows = csv.reader(csvfile)
        csv_rows.next()
        for row in csv_rows:
            if int(row[0]) not in malicious:
                rows.append(int(row[1]))

    nrows = np.array(rows)
    avg = np.mean(nrows, axis=0)
    std = np.std(nrows, axis=0)

    avg_percent = round(float(avg)/float(total_nodes)*100, 2)
    std_percent = round(float(std)/float(total_nodes)*100, 2)

    return (avg_percent, std_percent)


def calculate_true_positives(results_dir, results_file, num_malicious):
    if num_malicious == 0:
        print "num_malicious is 0"
        return 100.00, 0.00

    rows = []
    with open(results_dir+"/"+results_file, 'rb') as csvfile:
        csv_rows = csv.reader(csvfile)
        csv_rows.next()
        for row in csv_rows:
            if int(row[0]) not in malicious:
                rows.append(int(row[2]))

    nrows = np.array(rows)
    avg = np.mean(nrows, axis=0)
    std = np.std(nrows, axis=0)

    avg_percent = round(float(avg)/float(num_malicious)*100, 2)
    std_percent = round(float(std)/float(num_malicious)*100, 2)

    return (avg_percent, std_percent)


def calculate_false_positives(results_dir, results_file, num_malicious):
    if num_malicious == 0:
        print "num_malicious is 0"
        return 100.00, 0.00

    rows = []
    with open(results_dir+"/"+results_file, 'rb') as csvfile:
        csv_rows = csv.reader(csvfile)
        csv_rows.next()
        for row in csv_rows:
            if int(row[0]) not in malicious:
                rows.append(int(row[3]))

    nrows = np.array(rows)
    avg = np.mean(nrows, axis=0)
    std = np.std(nrows, axis=0)

    avg_percent = round(float(avg)/float(num_malicious)*100, 2)
    std_percent = round(float(std)/float(num_malicious)*100, 2)

    return (avg_percent, std_percent)

def calculate_false_negatives(results_dir, results_file, num_malicious):
    if num_malicious == 0:
        print "num_malicious is 0"
        return 100.00, 0.00

    rows = []
    with open(results_dir+"/"+results_file, 'rb') as csvfile:
        csv_rows = csv.reader(csvfile)
        csv_rows.next()
        for row in csv_rows:
            if int(row[0]) not in malicious:
                rows.append(int(row[4]))

    nrows = np.array(rows)
    avg = np.mean(nrows, axis=0)
    std = np.std(nrows, axis=0)

    avg_percent = round(float(avg)/float(num_malicious)*100, 2)
    std_percent = round(float(std)/float(num_malicious)*100, 2)

    return (avg_percent, std_percent)


def read_results(number, graph_dir):
    global color_index

    graph_name = graph_dir.split('_')[0]
    results_dir = directory+"/"+graph_dir+"/"
    num_malicious = sum(1 for line in open(results_dir+'/ground_truth.nodes') if line.rstrip())

    avgs_dt = []
    devs_dt = []

    avgs_tp = []
    devs_tp = []

    avgs_fp = []
    devs_fp = []

    avgs_fn = []
    devs_fn = []

    gt = []

    # total_nodes = 1100 # TODO: Automate
    total_nodes = 160
    percent_malicious = round(float(num_malicious)/float(total_nodes)*100, 2)
    # print percent_malicious

    n_results = 0
    for results_file in os.listdir(results_dir):
        if results_file.startswith("results_"):
            n_results += 1

    # 6042
    # 864
    # 1726
    for iteration in range(1, 863):
        i = iteration*10
        results_file = 'results/results_'+str(i)+'.csv'
        print results_file

        # print results_file
        # print "Graph", graph_name, "iteration", iteration
        # print calculate_average(results_dir, results_file, num_malicious)
        avg, std = calculate_detected(results_dir, results_file, total_nodes)
        avgs_dt.append(avg)
        devs_dt.append(std)

        avg, std = calculate_true_positives(results_dir, results_file, total_nodes)
        avgs_tp.append(avg)
        devs_tp.append(std)

        avg, std = calculate_false_positives(results_dir, results_file, total_nodes)
        avgs_fp.append(avg)
        devs_fp.append(std)

        avg, std = calculate_false_negatives(results_dir, results_file, total_nodes)
        avgs_fn.append(avg)
        devs_fn.append(std)

        gt.append(percent_malicious)

        # if iteration == 450:
        #     percent_malicious = round(float(num_malicious+1)/float(total_nodes)*100, 2)
        # print results_file

    # plot(averages, deviations, graph_name, colors[color_index])
    full_plot(avgs_dt, devs_dt, avgs_tp, devs_tp,
              avgs_fp, devs_fp, avgs_fn, devs_fn,
              gt, graph_name)
    # color_index += 1

args = parser.parse_args()
directory = args.directory



for scenario in scenarios:
    for number in numbers:
        graph_dir = ''#'one_'+str(number)
        
        malicious = []
        f = open(directory+graph_dir+'/ground_truth.nodes', 'r')
        for line in f:
            malicious.append(int(line))
        f.close()
        read_results(scenario, graph_dir)
        x1,x2,y1,y2 = plt.axis()
        plt.axis((x1,x2,0,100))
        plt.xlabel("Iterations")
        plt.ylabel("Percent")
        # plt.margins(x=1)
        # plt.legend(loc='upper left')
        plt.savefig(directory+"/"+str(scenario)+'_'+str(number)+'.png', dpi=300)
        plt.clf()
        color_index = 0
