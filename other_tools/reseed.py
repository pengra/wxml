import networkx
from progress.bar import IncrementalBar
import random

def seed_districts(graph, districts):
    """
    A simple procedure that selects n random seed nodes (n = number of districts)
    and then selects neighbors of those seeds and claims them to be of the same
    district.
    Performance Notes:
    o(n^3), but operations are cheap.
    """
    if districts > 1:
        bar = IncrementalBar("Seeding Districts", max=len(graph.nodes))
        graph_pool = [_ for _ in graph.nodes]
        random.shuffle(graph_pool)

        district_sizes = [[1, district] for district in range(districts)]

        # Start the district with some seeds
        for district in range(districts):
            bar.next()
            
            seed = graph_pool.pop()
            graph.nodes[seed]['dis'] = district

        # While there are unclaimed nodes
        while graph_pool:
            last_run = len(graph_pool)
            # Let each district claim a new node
            district_sizes = sorted(district_sizes)
            for i, (size, district) in enumerate(district_sizes):
                round_complete = False
                # Find the nodes that belong to a district
                for node, props in graph.nodes(data=True): 
                    if props['dis'] == district:
                        # Iterate through edges and find an unclaimed neighbor
                        for _, neighbor in graph.edges(node):
                            if neighbor in graph_pool:
                                graph_pool.remove(neighbor)
                                district_sizes[i][0] += 1
                                bar.next()
                                graph.nodes[neighbor]['dis'] = district
                                round_complete = True
                                break
                    if round_complete: break # Quicker breaking
                if round_complete: break # Quicker breaking

            # if len(graph_pool) == last_run:
            #     for node in graph_pool:
            #         graph.remove_node(node)
            #     break

        bar.finish()

    else:
        for node in graph.nodes():
            graph.nodes[node]['dis'] = 0
    
    return graph

if __name__ == "__main__":
    g = networkx.read_gpickle("WA4.dnx")
    for node in g.nodes:
        g.nodes[node]['dis'] = -1
    g = seed_districts(g, 10)
    networkx.write_gpickle(g, "WA4.dnx")

