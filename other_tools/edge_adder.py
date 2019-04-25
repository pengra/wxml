import networkx as nx
from progress.bar import IncrementalBar

edge_file_name = '../shp/ohio/output.txt';

dnx = nx.read_gpickle("../dnx/ohio.dnx")

all_edges = []
num_lines = sum(1 for line in open(edge_file_name))
with open(edge_file_name, 'r') as edge_file:
    bar = IncrementalBar("Reading in the file...".format(num_lines), max=num_lines)
    for i in edge_file:
        a = i.split(" ")
        edge = (int(a[0].replace("(", "")[:-1]), int(a[1].replace(")\n", "")))
        all_edges.append(edge)
        bar.next()

dnx.add_edges_from(all_edges)
nx.write_gpickle(dnx, "ohio.dnx")
