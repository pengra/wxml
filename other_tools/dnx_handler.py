import networkx
import shapefile
import csv
#import neighbors
import utm
import math

'''
    # Description of the returned dict from 'dnx_to_JSON()' method
    json_obj = {
        'nodes': [ node_obj, node_obj, ..., node_obj ],
        'edges': [ (rid, rid), (rid, rid), ..., (rid, rid) ],
        'districts': int
    }
    node_obj = {
        'rid': int,
        'name': String,
        'dis': int,
        'pop': int,
        'd_active': int,
        'r_active': int,
        'district': int,
        'o_active': int,
        'vertices': [ (longitude, latitude), (longitude, latitude), ... ]
    }
'''
def dnx_to_JSON(path):
    dnx = networkx.read_gpickle(path)
    json_obj = {
        'nodes': [],
        'edges': list(dnx.edges),
        'graph': dnx.graph
    }
    for rid in sorted(dnx.nodes):
        node_obj =  {
            'rid': rid,
            'name': accessInfoFromDNXNode(dnx, rid, 'name', convert_to_int=False),
            'dis': accessInfoFromDNXNode(dnx, rid, 'dis'),
            'pop': accessInfoFromDNXNode(dnx, rid, 'pop'),
            'd_active': accessInfoFromDNXNode(dnx, rid, 'd_active'),
            'r_active': accessInfoFromDNXNode(dnx, rid, 'r_active'),
            'o_active': accessInfoFromDNXNode(dnx, rid, 'o_active'),
            'vertexes': list(accessInfoFromDNXNode(dnx, rid, 'vertexes', convert_to_int=False)[0])
        };
        json_obj['nodes'].append(node_obj);
    return json_obj

# Method to return processed values from dnx files
# takes into account when the information is missing in the dnx file
def accessInfoFromDNXNode(dnx, rid, info, convert_to_int=True):
    if info in dnx.nodes[rid]:
        v = dnx.nodes[rid][info];
        if convert_to_int:
            return int(v)
        return v
    else:
        if not convert_to_int:
            return "-1"
        return -1

def JSON_to_dnx(json_obj, name):
    dnx = networkx.Graph();
    # graph attributes
    for k in json_obj['graph'].keys():
        dnx.graph[k] = json_obj['graph'][k];

    dnx.add_edges_from(json_obj['edges']);
    for node_obj in json_obj['nodes']:
        rid = node_obj['rid']
        dnx.nodes[rid]['geoid'] = -1
        dnx.nodes[rid]['name'] = node_obj['name']
        dnx.nodes[rid]['dis'] = node_obj['dis']
        dnx.nodes[rid]['pop'] = node_obj['pop']
        dnx.nodes[rid]['d_active'] = max(0, node_obj['d_active'])
        dnx.nodes[rid]['r_active'] = max(0, node_obj['r_active'])
        dnx.nodes[rid]['o_active'] = max(0, node_obj['o_active'])
        dnx.nodes[rid]['vertexes'] = tuple([tuple(node_obj['vertexes'])])
    networkx.write_gpickle(dnx, name)

def shape_to_dnx(shapeFileName="../shp/ohio/precincts_results", dnx_name="../dnx/ohio.dnx"):
    sf = shapefile.Reader(shapeFileName).shapeRecords()
    print(sf[0].record)
    dnx = networkx.Graph()

    print("graph created");

    # graph attributes
    dnx.graph["fips"] = 39 # OHIO Data
    dnx.graph["code"] = "OH" # OHIO Data
    dnx.graph["state"] = "Ohio" # OHIO Data
    dnx.graph["districts"] = 16 # OHIO Data
    dnx.graph["is_super"] = 0 # OHIO Data

    '''
    print("edge attribute process started");
    # edge attributes
    n = neighbors.getAllEdges(shapeFileName) #{ n1: [n2, n3, ... ], n2: [...],...}
    print("\tgetAllEdges finished")
    converted_n = []
    for k in n.keys():
        for l in n[k]:
            converted_n.append((k,l)) #[ (n1, n2), (n2, n3), ...]
    print("\tdictionary conversion finished")
    print(converted_n);
    dnx.add_edges_from(converted_n)
    print("\tadding to dnx finished")

    print("edge attribute process finished");
    '''
    # node attributes
    print("starting")
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
        dnx.nodes[rid]['is_super'] = False # don't have info
        dnx.nodes[rid]['super_level'] = 0 # don't have info

        # coordinates
        c_array = sf[rid].shape.points
        #standard_c = c_array
        standard_c = [(utm.to_latlon(c[0], c[1], 17, "N")[1],utm.to_latlon(c[0], c[1], 17, "N")[0]) for c in c_array] # OHIO Data
        dnx.nodes[rid]['vertexes'] = tuple([tuple(standard_c)])

    print("ended")
    networkx.write_gpickle(dnx, dnx_name)
# shape_to_dnx();
