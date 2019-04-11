from base import  Rakan
import networkx as nx
import csv
import random
import numpy as np

def translate(source_dnx_path, dictionary_path, base_dnx_path, destination_dnx_path):
    r = Rakan()
    r_supers = Rakan()

    r.read_nx(base_dnx_path)

    r_supers.read_nx(source_dnx_path)

    supers_graph = r_supers.nx_graph
    s_map = open(dictionary_path, 'r')
    csv_reader = csv.reader(s_map, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
    adj_graph = r.nx_graph
    for row in csv_reader:
        if row[0] != 'precinct':
            adj_graph.nodes[int(row[0])]['dis'] = supers_graph.nodes[int(row[1])]['dis']
    adj_graph.graph['districts'] = supers_graph.graph['districts']
    nx.write_gpickle(adj_graph, destination_dnx_path)

    r.read_nx(destination_dnx_path)
    r.show("dists.png")

def get_n_precincts(n, m):
    pos = [i for i in range(m)]
    vals = []
    for i in range(n):
        vals.append(pos.pop(random.randint(0,len(pos)-1)))
    return vals

def remove_possible_move(possible_moves, move):
    new_possible_moves = []
    for m in possible_moves:
        if m[0] != move[0]:
            new_possible_moves.append(m)
    return new_possible_moves

def prim_change(move, r, groups):
    prim =0
    for dist in r.get_neighbors(move[0]).values():
        for p in dist:
            if groups[p] != move[1]:
                prim +=1
    return prim

def pick_move(possible_moves, sizes):
    #idx = np.random.randint(0,len(possible_moves))
    min_possible_size = 1000000000000
    for move in possible_moves:
        min_possible_size = min(min_possible_size, sizes[move[1]])
    idxs = [i for i in range(len(possible_moves))]
    np.random.shuffle(idxs)
    for idx in idxs:
        if sizes[possible_moves[idx][1]] == min_possible_size:
            return possible_moves[idx]

# 'WA.dnx', 300, 10, 'super_map.csv', 'supers.dnx'
def build_supers(base_dnx_path, supers, districts, dictionary_path, destination_dnx_path):
    r = Rakan()

    r.read_nx("WA.dnx")

    adj_graph = nx.Graph()

    groups = [supers for i in range(len(r))]
    sizes = [1 for i in range(supers)]

    new_rak = Rakan(len(r), supers+1)

    new_rak.nx_graph = r.nx_graph

    starting = get_n_precincts(supers, len(r))
    used = set()
    possible_moves = []

    for i in range(supers):
        #r.move_precinct(starting[i], i)
        groups[starting[i]]=i
        used.add(starting[i])
        adj_graph.add_node(i)
        adj_graph.nodes[i]['dis'] = r.nx_graph.nodes[starting[i]]['dis']
        adj_graph.nodes[i]['pop'] = r.nx_graph.nodes[starting[i]]['pop']
        adj_graph.nodes[i]['d_active'] = r.nx_graph.nodes[starting[i]]['d_active']
        adj_graph.nodes[i]['r_active'] = r.nx_graph.nodes[starting[i]]['r_active']
        adj_graph.nodes[i]['o_active'] = r.nx_graph.nodes[starting[i]]['o_active']
        for dist in r.get_neighbors(starting[i]).values():
            for p in dist:
                if not p in used:
                    possible_moves.append([p,i])
                else:
                     adj_graph.add_edge(i, groups[p])

    while len(possible_moves) > 0:
        move = pick_move(possible_moves, sizes)
        used.add(move[0])
        groups[move[0]] = move[1]
        adj_graph.nodes[move[1]]['pop'] += r.nx_graph.nodes[move[0]]['pop']
        adj_graph.nodes[move[1]]['d_active'] += r.nx_graph.nodes[move[0]]['d_active']
        adj_graph.nodes[move[1]]['r_active'] += r.nx_graph.nodes[move[0]]['r_active']
        adj_graph.nodes[move[1]]['o_active'] += r.nx_graph.nodes[move[0]]['o_active']
        sizes[move[1]] += 1
        possible_moves = remove_possible_move(possible_moves, move)
        for dist in r.get_neighbors(move[0]).values():
            for p in dist:
                if not p in used:
                    if r.nx_graph.nodes[move[0]]['dis'] == r.nx_graph.nodes[p]['dis']:
                        possible_moves.append([p,move[1]])
                else:
                    if move[1] != groups[p]:
                        adj_graph.add_edge(move[1], groups[p])

    for i in range(supers):
        edges = [k for k in adj_graph[i].keys()]
        if len(edges) == 1:
            sizes[i] = 0
            for j in range(len(groups)):
                if groups[j] == i:
                    groups[j] = edges[0]
                    sizes[edges[0]] += 1
                    adj_graph.nodes[edges[0]]['pop'] += r.nx_graph.nodes[i]['pop']
                    adj_graph.nodes[edges[0]]['d_active'] += r.nx_graph.nodes[i]['d_active']
                    adj_graph.nodes[edges[0]]['r_active'] += r.nx_graph.nodes[i]['r_active']
                    adj_graph.nodes[edges[0]]['o_active'] += r.nx_graph.nodes[i]['o_active']
            adj_graph.remove_edge(edges[0],i)

    # create new districts
    starters = []
    open_nodes = []
    closed_nodes = []
    dist_sizes = [1 for i in range(districts)]
    for i in range(districts):
        strt = np.random.randint(0,supers)
        while strt in starters or len(adj_graph[strt]) == 0:
            strt = np.random.randint(0,supers)
        closed_nodes.append(strt)
        starters.append(strt)

    for strt in starters:
        adj_graph.nodes[strt]['dis'] = starters.index(strt)
        for i in adj_graph[strt]:
            if not i in closed_nodes:
                open_nodes.append((i, adj_graph.nodes[strt]['dis']))
    print(len(starters))

    while len(open_nodes) > 0:

        #move = open_nodes[np.random.randint(0, len(open_nodes))]
        move = pick_move(open_nodes, dist_sizes)
        open_nodes=remove_possible_move(open_nodes, move)

        closed_nodes.append(move[0])
        adj_graph.nodes[move[0]]['dis'] = move[1]
        dist_sizes[move[1]] += 1
        for i in adj_graph[move[0]]:
            if not i in closed_nodes:
                open_nodes.append((i, adj_graph.nodes[move[0]]['dis']))

    s_map = open('super_map.csv', 'w')
    filewriter = csv.writer(s_map, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['precinct','superprecinct'])
    for i in range(len(groups)):
        filewriter.writerow([i, groups[i]])

    s_map.close()
    for i in range(len(r)):
        dist = groups[i]
        if dist != None:
            new_rak.add_precinct(dist)
        else:
            new_rak.add_precinct(9)


    print("Mean size")
    print(np.mean(sizes))
    print("Standard Deviation:")
    print(np.std(sizes))
    print("Max:")
    print(max(sizes))
    print("Min:")
    print(min(sizes))
    adj_graph.graph['districts'] = r.nx_graph.graph['districts']

    nx.write_gpickle(adj_graph, 'supers.dnx')
