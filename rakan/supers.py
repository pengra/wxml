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
    
    
def get_n_precincts(n, m):
    pos = [i for i in range(m)]
    vals = []
    
    for i in range(n):
        idx = pos.pop(random.randint(0,len(pos)-1))
        vals.append(idx)
    
    return vals

def remove_possible_move(possible_moves, move):
    new_possible_moves = []
    for m in possible_moves:
        if m[0] != move[0]:
            new_possible_moves.append(m)
    return new_possible_moves

def prim_change(move, r, groups):
    prim = 0
    for dist in r.get_neighbors(move[0]).values():
        for p in dist:
            if groups[p] != move[1]:
                prim +=1
    return prim

def get_boarders(possible_moves, adj_graph, groups):
    boarders = {}
    for m in possible_moves:
        b = 0
        for p in adj_graph[m[0]]:
            if groups[p] != m[1]:
                b += 1
        boarders[m[0]] = b
    return boarders 

def pick_move(possible_moves, sizes, boarders = None):
    #idx = np.random.randint(0,len(possible_moves))
    min_possible_size = 1000000000000
    for move in possible_moves:
        if boarders != None:
            s = boarders[move[0]]
        else:
            s = sizes[move[1]]
        if  min_possible_size > s:
            min_possible_size = s
            best_move = move
    return best_move
    idxs = [i for i in range(len(possible_moves))]
    np.random.shuffle(idxs)
    for idx in idxs:
        if sizes[possible_moves[idx][1]] == min_possible_size:
            return possible_moves[idx]
     
def build_supers(base_dnx_path, supers, districts, dictionary_path, destination_dnx_path, vis= False, supers_vis_path = 'supers.png'):
    r = Rakan()

    r.read_nx(base_dnx_path)
    
    adj_graph = nx.Graph()
    
    groups = [supers for i in range(len(r))]
    sizes = [0 for i in range(supers)]
    
    
    starting = get_n_precincts(supers, len(r))
    
    used = set()
    possible_moves = []
    
    for i in range(supers):
         adj_graph.add_node(i)
    
    for i in range(supers):
        groups[starting[i]]=i
        used.add(starting[i])
        adj_graph.nodes[i]['dis'] = r.nx_graph.nodes[starting[i]]['dis']
        adj_graph.nodes[i]['pop'] = r.nx_graph.nodes[starting[i]]['pop']
        adj_graph.nodes[i]['d_active'] = r.nx_graph.nodes[starting[i]]['d_active']
        adj_graph.nodes[i]['r_active'] = r.nx_graph.nodes[starting[i]]['r_active']
        adj_graph.nodes[i]['o_active'] = r.nx_graph.nodes[starting[i]]['o_active']
        possible_moves = remove_possible_move(possible_moves, [starting[i],0])
        sizes[i] += r.nx_graph.nodes[starting[i]]['pop']
        for p in r.nx_graph[starting[i]]:
            if not p in used:
                possible_moves.append([p,i])
            else:
                adj_graph.add_edge(i, groups[p])
                adj_graph.edges[i, groups[p]]['weight'] = 1
    
    while len(possible_moves) > 0:
        boarders = get_boarders(possible_moves, r.nx_graph, groups)
        move = pick_move(possible_moves, sizes, boarders)
        used.add(move[0])
        groups[move[0]] = move[1]
        adj_graph.nodes[move[1]]['pop'] += r.nx_graph.nodes[move[0]]['pop']
        adj_graph.nodes[move[1]]['d_active'] += r.nx_graph.nodes[move[0]]['d_active']
        adj_graph.nodes[move[1]]['r_active'] += r.nx_graph.nodes[move[0]]['r_active']
        adj_graph.nodes[move[1]]['o_active'] += r.nx_graph.nodes[move[0]]['o_active']
        sizes[move[1]] += r.nx_graph.nodes[move[0]]['pop']
        possible_moves = remove_possible_move(possible_moves, move)
        for p in r.nx_graph[move[0]]:
            if not p in used:
                possible_moves.append([p,move[1]])
            else:
                if move[1] != groups[p]:
                    if adj_graph.has_edge(move[1], groups[p]):
                        adj_graph.edges[move[1], groups[p]]['weight'] += 1
                    else:
                        adj_graph.add_edge(move[1], groups[p])
                        adj_graph.edges[move[1], groups[p]]['weight'] = 1
    ''''
    precincts_to_keep = []
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
        else:
            precincts_to_keep.append(i)
    
        
    corrected_adj_graph = nx.Graph()
    for i in range(len(precincts_to_keep)):
        corrected_adj_graph.add_node(i)
        corrected_adj_graph.nodes[i]['d_active'] = adj_graph.nodes[precincts_to_keep[i]]['d_active']
        corrected_adj_graph.nodes[i]['r_active'] = adj_graph.nodes[precincts_to_keep[i]]['r_active']
        corrected_adj_graph.nodes[i]['o_active'] = adj_graph.nodes[precincts_to_keep[i]]['o_active']
        corrected_adj_graph.nodes[i]['pop'] = adj_graph.nodes[precincts_to_keep[i]]['pop']
        corrected_adj_graph.nodes[i]['name'] = 'super ' + str(i)
        corrected_adj_graph.nodes[i]['vertexes'] = None
        
    for i in range(len(precincts_to_keep)):
        for node in adj_graph[precincts_to_keep[i]]:
            corrected_adj_graph.add_edge(i, precincts_to_keep.index(node))
            corrected_adj_graph.edges[i, precincts_to_keep.index(node)]['weight'] = adj_graph.edges[node, precincts_to_keep[i]]['weight']
    '''
    corrected_adj_graph = adj_graph
    if vis:
        '''
        g =  r.nx_graph
        g.graph['districts'] = supers
        for i in range(len(g.nodes)):
            g.nodes[i]['dis'] = precincts_to_keep.index(groups[i])
           # print(g.nodes[i]['dis'])
        r.build_from_graph(g)
        r.show(supers_vis_path)
        '''
        g =  r.nx_graph
        g.graph['districts'] = supers
        for i in range(len(g.nodes)):
            g.nodes[i]['dis'] = groups[i]
           # print(g.nodes[i]['dis'])
        r.build_from_graph(g)
        r.show('uncorrected.png')
        
    corrected_adj_graph = adj_graph
        
    # create new districts
    starters = []
    open_nodes = []
    closed_nodes = []
    dist_sizes = [1 for i in range(districts)]
    for i in range(districts):
        strt = np.random.randint(0,len(corrected_adj_graph))
        while strt in starters or len(corrected_adj_graph[strt]) == 0:
            strt = np.random.randint(0,len(corrected_adj_graph))
        closed_nodes.append(strt)
        starters.append(strt)
    
    for strt in starters:
        corrected_adj_graph.nodes[strt]['dis'] = starters.index(strt)
        for i in corrected_adj_graph[strt]:
            if not i in closed_nodes:
                open_nodes.append((i, corrected_adj_graph.nodes[strt]['dis']))
    
    
    while len(open_nodes) > 0:
        move = pick_move(open_nodes, dist_sizes)
        open_nodes=remove_possible_move(open_nodes, move)
       
        closed_nodes.append(move[0])
        corrected_adj_graph.nodes[move[0]]['dis'] = move[1]
        dist_sizes[move[1]] += 1
        for i in corrected_adj_graph[move[0]]:
            if not i in closed_nodes:
                open_nodes.append((i, corrected_adj_graph.nodes[move[0]]['dis']))
    
    s_map = open(dictionary_path, 'w')
    filewriter = csv.writer(s_map, delimiter=',',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
    filewriter.writerow(['precinct','superprecinct'])
    for i in range(len(groups)):
        filewriter.writerow([i, groups[i]])
        
    s_map.close()
    
            
    
    print("Mean size")
    print(np.mean(sizes))
    print("Standard Deviation:")
    print(np.std(sizes))
    print("Max:")
    print(max(sizes))
    print("Min:")
    print(min(sizes))
    corrected_adj_graph.graph['districts'] = districts
    
    nx.write_gpickle(corrected_adj_graph, destination_dnx_path)
