"""
A script that show all adjacencies in geojson.
"""

FILENAME = "WA3.dnx"
OUT_FILENAME = "map.geojson"

import networkx
import json
import io

z = {
    0: 1,
    1: 0,
    2: 7,
    9: 9
}

def export(nx_graph, black_list=list()):
    features = []
    
    for rid in nx_graph.nodes:
        index = nx_graph.nodes[rid]['name'].lower().startswith('water:')
        if (len(nx_graph.edges(rid)) == 0):
            index = 2
        if rid in black_list:
            index = 9
        features.append({
            "type": "Feature",
            "properties": {
                "district": z[index],
                "description": """<strong>{name}</strong><br/>
                ID: {rid}<br/>
                Population: {pop}<br/>
                District: {dis}<br/>
                """.format(
                    name=nx_graph.nodes[rid]['name'],
                    rid=rid,
                    pop=nx_graph.nodes[rid]['pop'],
                    dis=nx_graph.nodes[rid]['dis'],
                )
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": nx_graph.nodes[rid]['vertexes']
            }
        })

    for rid1, rid2 in nx_graph.edges:
        rid1_longs = [_[0] for _ in nx_graph.nodes[rid1]['vertexes'][0]]
        rid1_lads = [_[1] for _ in nx_graph.nodes[rid1]['vertexes'][0]]
        rid2_longs = [_[0] for _ in nx_graph.nodes[rid2]['vertexes'][0]]
        rid2_lads = [_[1] for _ in nx_graph.nodes[rid2]['vertexes'][0]]

        features.append({
            "type": "Feature",
            "properties": {
                "description": "{rid1} - {rid2}".format(rid1=rid1, rid2=rid2),
                "stroke": "#29a505",
                "stroke-width": 2,
                "stroke-opacity": 1
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        sum(rid1_longs) / len(rid1_longs),
                        sum(rid1_lads) / len(rid1_lads),
                    ],
                    [
                        sum(rid2_longs) / len(rid2_longs),
                        sum(rid2_lads) / len(rid2_lads),
                    ]
                ]
            }
        })

    geojson = json.dumps({
        "type": "FeatureCollection",
        "features": features
    })

    return geojson

def main():
    graph = networkx.read_gpickle(FILENAME)
    with io.open(OUT_FILENAME, 'w') as handle:
        handle.write(export(graph))

if __name__ == "__main__":
    main()