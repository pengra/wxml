from multiprocessing import Process
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import networkx as nx
import shapefile as shp
import math
import warnings
from progress.bar import IncrementalBar

def visualize_connections(file_name="ohio.dnx"):
    warnings.simplefilter("ignore")
    print("reading in gpickle...")
    G = nx.read_gpickle(file_name)
    pos = nx.get_node_attributes(G, 'vertexes')

    print("converting vertexes into visualizable points...")
    # Remove ghost precincts and find centers for the ones aren't ghosts
    boundaries = {
        "xmin": math.inf,
        "xmax": -math.inf,
        "ymin": math.inf,
        "ymax": -math.inf,
    }
    precinct_centers = {}
    filtered_nodes = []
    for k in pos.keys():
        points = list(G.node[k]['vertexes'][0])
        if len(points) > 0:
            filtered_nodes.append(k)
            # calculate precinct_centers:
            x = 0
            y = 0
            for v in list(pos[k][0]):
                x += v[0]
                y += v[1]
                if boundaries["xmin"] > v[0]:
                    boundaries["xmin"] = v[0]
                if boundaries["xmax"] < v[0]:
                    boundaries["xmax"] = v[0]

                if boundaries["ymin"] > v[1]:
                    boundaries["ymin"] = v[1]
                if boundaries["ymax"] < v[1]:
                    boundaries["ymax"] = v[1]
            x /= len(pos[k][0])
            y /= len(pos[k][0])
            precinct_centers[k] = [x,y]
        else:
            G.remove_node(k)

    print("normalizing...")
    for k in filtered_nodes:
        newX = (precinct_centers[k][0]-boundaries["xmin"])/(boundaries["xmax"] - boundaries["xmin"])
        newY = (precinct_centers[k][1]-boundaries["ymin"])/(boundaries["ymax"] - boundaries["ymin"])
        precinct_centers[k] = [newX, newY]

    plt.figure(figsize=(40, 40))
    print("visualizing edges...")
    nx.draw_networkx_edges(G, precinct_centers, nodelist=filtered_nodes, alpha=0.4)

    print("visualizing nodes...")
    nx.draw_networkx_nodes(G, precinct_centers, nodelist=filtered_nodes, node_size=5)

    plt.xlim(-0.05, 1.05)
    plt.ylim(-0.05, 1.05)
    plt.axis('off')
    plt.savefig(file_name.replace(".dnx", ".png"));

    warnings.simplefilter("default")

def visualize_borders(file_name="../shp/ohio/precincts_results"):
    warnings.simplefilter("ignore")

    print("reading shape files...")
    sns.set(style="whitegrid", palette="pastel", color_codes=True)
    sns.mpl.rc("figure", figsize=(10,6))
    sf = shp.Reader(file_name)

    print("preparing pandas...")
    fields = [x[0] for x in sf.fields][1:]
    records = sf.records()
    shps = [s.points for s in sf.shapes()]
    df = pd.DataFrame(columns=fields, data=records)
    df = df.assign(coords=shps)

    target = len(sf)
    bar = IncrementalBar("visualizing nodes...".format(target), max=target)
    plt.figure(figsize=(60, 60))
    ax = plt.axes()
    ax.set_aspect('equal')

    xboundaries = [math.inf, -math.inf]
    for id in range(len(sf)):
        if id > 500:
            bar.next()
            continue
        shape_ex = sf.shape(id)
        if len(shape_ex.points) <= 0:
            bar.next()
            continue
        x_lon = np.zeros((len(shape_ex.points),1))
        y_lat = np.zeros((len(shape_ex.points),1))
        for ip in range(len(shape_ex.points)):
            x_lon[ip] = shape_ex.points[ip][0]
            y_lat[ip] = shape_ex.points[ip][1]
        plt.plot(x_lon,y_lat)
        x0 = np.mean(x_lon)
        y0 = np.mean(y_lat)
        plt.text(x0, y0, str(id), fontsize=4)
        xboundaries = [min(shape_ex.bbox[0], xboundaries[0]),max(shape_ex.bbox[2], xboundaries[1])]
        bar.next()

    print("\nsaving the png file...")
    # use bbox (bounding box) to set plot limits
    plt.xlim(xboundaries[0],xboundaries[1])
    plt.axis('off')
    plt.savefig(file_name  +".png");

    warnings.simplefilter("default")
    print("finished")
