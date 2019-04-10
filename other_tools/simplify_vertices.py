import networkx
import math
from progress.bar import IncrementalBar

def pointInAlignment(first, second, third):
    v1 = [first[0] - second[0], first[1] - second[1]]
    v2 = [third[0] - second[0], third[1] - second[1]]
    dotProd = v1[0]*v2[0]+v1[1]*v2[1]
    magV1 = math.sqrt(v1[0]**2+v1[1]**2)
    magV2 = math.sqrt(v2[0]**2+v2[1]**2)
    angle = math.acos(max(min(dotProd/magV1/magV2, 1), -1))
    return (abs(angle - math.pi) < 0.008 ,angle)

def newGraph(old_file="../WA.dnx"):
    angles = {}
    graph = networkx.read_gpickle(old_file)
    newGraph = graph.copy()
    newVertexes = {}
    bar = IncrementalBar("Simplifying {} nodes".format(len(graph.node)), max=len(graph.node))
    for i in graph.node:
        vertices = graph.node[i]['vertexes'][0]
        newSet = [vertices[0]]
        for i in range(1, len(vertices) - 1):
            before = vertices[i - 1]
            current = vertices[i]
            after = vertices[i + 1]
            
            # restructured to test the angle
            r = pointInAlignment(before, current, after)
            if abs(r[1] - math.pi) < 0.1:
                an = int(abs(r[1] - math.pi)*1000)/1000
                if an not in angles:
                    angles[an] = 0
                angles[an] += 1

            if not r[0]:
                newSet.append(before)
        newVertexes[i] = (tuple(newSet),)
        bar.next()
        # print("Key: {:4d} original: {:4d} new: {:4d} diff: {:4d}".format(i, len(vertices), len(newSet), len(vertices) - len(newSet)))
    networkx.set_node_attributes(newGraph, newVertexes, 'vertexes')
    networkx.write_gpickle(newGraph, '../holy.dnx')
    # print(angles)
    return newGraph

newGraph()
