import argparse
import os

parser = argparse.ArgumentParser(description='Reads Report and outputs separate files.')
parser.add_argument('-i', '--input_dir', type=str, required=True,
                    help='Directory containing ONE reports')
parser.add_argument('-o', '--output_dir', type=str, required=True,
                    help='Directory for output')

# Finds report files in the input directory.
def list_reports(dir):
    reports = []
    for root, _, files in os.walk(dir):
        for name in files:
            if "_AdjacencySnapshotReport.txt" in name:
                scenario = os.path.basename(name).split('_AdjacencySnapshotReport.txt')[0]
                report = (scenario, os.path.join(root, name))
                reports.append(report)
    return reports

args = parser.parse_args()

for (scenario, report_file) in list_reports(args.input_dir):
    output = args.output_dir+'/'+str(scenario)

    # Avoid path errors
    if not os.path.exists(report_file):
        print 'Report '+report_file+' not found. Skipping.'
        continue

    print 'Processing '+scenario

    # Create directories if necessary
    if not os.path.exists(output):
        os.makedirs(output)

    timestamp = 0
    edges = ''
    with open(report_file, 'rb') as report:
        for line in report.readlines():
            # Square brackets separate the timestamps
            if '[' in line:
                # Each line in the file is an edge in the graph
                with open(output+'/'+str(timestamp)+'.txt', 'w') as out:
                    out.write(edges)
                edges = ''
                timestamp = int(line.translate(None, '[]'))
            else:
                edges += line.translate(None, 'ABCDEFGHW')
