"""
A script that elimantes all edges that are connected by diagonals
"""

FILENAME = "WA.dnx"
JSON_LOC = "map.0.geojson"


import networkx
import collections
import itertools
import json

with open(JSON_LOC) as handle:
    JSON_BLOB = json.loads(handle.read())

def main():
    graph = networkx.read_gpickle(FILENAME)
    edges = [_ for _ in graph.edges]
    print("Discovered %i edges" % len(edges))
    
    shortcut_confirmed = 0
    dismissed = 0

    for i, (node1, node2) in enumerate(edges):
        # print("({i}/{total}) Grabbing node {edge1} & {edge2} vertexes".format(i=i,total=len(edges), edge1=node1, edge2=node2), end=' ... ')
        n1_vertexes = graph.nodes[node1]['vertexes'][0]
        n2_vertexes = graph.nodes[node2]['vertexes'][0]
        
        shared_vertexes = len(set(n1_vertexes).intersection(set(n2_vertexes)))

        if shared_vertexes >= 2:
            shortcut_confirmed += 1
            continue

        n1y = [_[0] for _ in n1_vertexes]
        n1x = [_[1] for _ in n1_vertexes]
        n2y = [_[0] for _ in n2_vertexes]
        n2x = [_[1] for _ in n2_vertexes]
        
        n1y = (min(n1y), max(n1y))
        n1x = (min(n1x), max(n1x))
        n2y = (min(n2y), max(n2y))
        n2x = (min(n2x), max(n2x))

        ok = False

        if (min(n1y) > min(n2y) and min(n1y) < max(n2y)) or (min(n2y) > min(n1y) and min(n2y) < max(n1y)):
            if (min(n1x) > min(n2x) and min(n1x) < max(n2x)) or (min(n2x) > min(n1x) and min(n2x) < max(n1x)):
                ok = True

        if not ok:
            dismissed += 1
            graph.remove_edge(node1, node2)
            JSON_BLOB['features'][node1]['properties']['district'] = 11
            JSON_BLOB['features'][node2]['properties']['district'] = 11

    with open("map.geojson", 'w') as handle:
        handle.write(json.dumps(JSON_BLOB))

    print("Shortcutted:", shortcut_confirmed)
    print("Dismissed:", dismissed)

def vectorize_coordinates(vertexes):
    pass
    


if __name__ == "__main__":
    main()