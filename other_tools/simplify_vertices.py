import networkx
import math
from progress.bar import IncrementalBar
from other_tools.geo import calculate_initial_compass_bearing

def pointInAlignment(first, second, third):
    a1 = calculate_initial_compass_bearing((first[1], first[0]), (second[1], second[0]))
    a2 = calculate_initial_compass_bearing((second[1], second[0]), (third[1], third[0]))
    return abs(a1-a2) < 0.01 #1 degree

def newGraph(old_file="../WA.dnx"):
    '''
    a method to create a graph with reduced number of vertices. Currently,
    reduces too many vertices to the point where the graph looks jagged. 
    '''
    angles = []
    graph = networkx.read_gpickle(old_file)
    newGraph = graph.copy()
    newVertexes = {}
    bar = IncrementalBar("Simplifying {} nodes".format(len(graph.node)), max=len(graph.node))
    for j in graph.node:
        vertices = graph.node[j]['vertexes'][0]
        newSet = [vertices[0]]
        for i in range(1, len(vertices) - 1):
            before = vertices[i - 1]
            current = vertices[i]
            after = vertices[i + 1]

            if not pointInAlignment(before, current, after):
                newSet.append(current)
        newSet.append(vertices[-1])
        newVertexes[j] = (tuple(newSet),)
        newGraph.node[j]['vertexes'] = newVertexes[j]
        bar.next()
        # print("Key: {:4d} original: {:4d} new: {:4d} diff: {:4d}".format(i, len(vertices), len(newSet), len(vertices) - len(newSet)))
    #networkx.set_node_attributes(newGraph, newVertexes, 'vertexes')
    networkx.write_gpickle(newGraph, '../holy.dnx')
    print(angles)
    return newGraph
