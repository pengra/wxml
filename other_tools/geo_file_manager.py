import utm
import math
import warnings
import numpy as np
import networkx as nx
import shapefile as shp
import matplotlib.pyplot as plt
from adjacency_factory import get_adjacency_list
from progress.bar import IncrementalBar

IMAGE_SIZE = 80 # inches
DNX_PATH = "../dnx/"
SHP_PATH = "../shp/"
IMG_PATH = "../img/"


def shape_to_dnx(input_file="ohio/precincts_results.shp", output_file="ohio.dnx"):
    print("reading in the shapefile...")
    sf = shp.Reader(SHP_PATH + input_file).shapeRecords()
    dnx = nx.Graph()

    # graph attributes
    dnx.graph["fips"] = 39 # OHIO Data
    dnx.graph["code"] = "OH" # OHIO Data
    dnx.graph["state"] = "Ohio" # OHIO Data
    dnx.graph["districts"] = 16 # OHIO Data
    dnx.graph["is_super"] = 0 # OHIO Data

    # new edge process (django)
    all_edges = get_adjacency_list(SHP_PATH + input_file)
    dnx.add_edges_from(all_edges)

    # node attributes
    target = len(sf)
    bar = IncrementalBar("adding appedix information...".format(target), max=target)
    for rid in range(len(sf)):
        # meta data
        r = sf[rid].record
        dnx.add_node(rid)
        dnx.nodes[rid]['geoid'] = -1# Don't know yet
        dnx.nodes[rid]['name'] = r.PRECINCT
        dnx.nodes[rid]['dis'] = 0 # NOT ASSIGNED YET
        dnx.nodes[rid]['pop'] = r.pres_16_re if r.pres_16_re else 0 # registered voters from year 16
        dnx.nodes[rid]['d_active'] = 0 # don't have info
        dnx.nodes[rid]['r_active'] = 0 # don't have info
        dnx.nodes[rid]['o_active'] = 0 # don't have info
        dnx.nodes[rid]['children'] = [] # don't have info
        dnx.nodes[rid]['is_super'] = False
        dnx.nodes[rid]['super_level'] = 0

        # coordinates
        c_array = sf[rid].shape.points
        #standard_c = c_array
        standard_c = [(utm.to_latlon(c[0], c[1], 17, "N")[1],utm.to_latlon(c[0], c[1], 17, "N")[0]) for c in c_array] # OHIO Data
        dnx.nodes[rid]['vertexes'] = tuple([tuple(standard_c)])
        bar.next()

    nx.write_gpickle(dnx, DNX_PATH + output_file)
    print("\nfinished!")


def visualize_dnx(file_name="ohio.dnx", connections=True, borders=True):
    warnings.simplefilter("ignore")
    print("reading in the gpickle...")
    G = nx.read_gpickle(DNX_PATH + file_name)
    pos = nx.get_node_attributes(G, 'vertexes')
    print(G.edges)

    # Remove ghost precincts and find centers for the ones aren't ghosts
    precinct_centers = {}
    filtered_nodes = []
    target = len(pos.keys())
    plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE))
    bar = IncrementalBar("visualizing nodes...".format(target), max=target)
    for k in pos.keys():
        points = list(G.node[k]['vertexes'][0])
        if len(points) > 0:
            filtered_nodes.append(k)
            # calculate precinct_centers:
            x_lon = list(map(lambda p: p[0], points))
            y_lat = list(map(lambda p: p[1], points))
            x = np.mean(x_lon)
            y = np.mean(y_lat)
            precinct_centers[k] = [x,y]
            plt.text(x, y, str(k), fontsize=4)
            if borders:
                plt.plot(x_lon,y_lat)
        else:
            G.remove_node(k)
        bar.next()
    nx.draw_networkx_nodes(G, precinct_centers, nodelist=filtered_nodes, node_size=5)

    if connections:
        print("\nvisualizing edges...")
        nx.draw_networkx_edges(G, precinct_centers, nodelist=filtered_nodes, alpha=0.4)
        print("saving the png file...")
    else:
        print("\nsaving the png file...")
    plt.axis('off')
    plt.savefig(IMG_PATH + file_name.replace(".dnx", ".png"));

    warnings.simplefilter("default")
    print("finished!")

# cannot visualize node connections, because shapefiles do not have the adjacency info
def visuzlize_shp(file_name="ohio/precincts_results"):
    warnings.simplefilter("ignore")

    print("reading in shape files...")
    sf = shp.Reader(SHP_PATH + file_name)

    target = len(sf)
    bar = IncrementalBar("visualizing nodes...".format(target), max=target)
    plt.figure(figsize=(IMAGE_SIZE, IMAGE_SIZE))
    for id in range(len(sf)):
        shape_ex = sf.shape(id)
        if len(shape_ex.points) > 0:
            x_lon = list(map(lambda p: p[0], shape_ex.points))
            y_lat = list(map(lambda p: p[1], shape_ex.points))
            x0 = np.mean(x_lon)
            y0 = np.mean(y_lat)
            plt.plot(x_lon,y_lat)
            plt.text(x0, y0, str(id), fontsize=4)
        bar.next()

    print("\nsaving the png file...")
    plt.axis('off')
    plt.savefig(IMG_PATH + file_name.split("/")[-1] +".png");

    warnings.simplefilter("default")
    print("finished!")

visualize_dnx()
