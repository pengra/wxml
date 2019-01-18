from base import BaseRakanWithServer, BaseRakan
from progress.bar import IncrementalBar

import faulthandler; faulthandler.enable()

import random
import networkx

class Rakan(BaseRakanWithServer):

    """
    An example step
    Argument can be passed in.

    Arguments are completely arbritary and can be rewritten by the user.
    """
    def step(self, max_value=1, *more_positional_stuff, **wow_we_got_key_words_up_here):
        print("|", end="")
        precinct, district = self.propose_random_move()
        # Completely random
        
        try:
            # Sometimes propose_random_move severs districts, and move_precinct will catch that.
            self.move_precinct(precinct, district)
            # For Xayah, record the move.
            if hasattr(self, "record_move"):
                self.record_move(precinct, district)
            self.iterations += 1
        except ValueError:
            # Sometimes the proposed move severs the district
            # Just try again
            self.step()
        

    """
    An example walk.
    Perhaps there is specific behavior for the 10 steps
    and specific behavior for the last 10.

    Arguments are completely arbritary and can be rewritten by the user.
    """
    def walk(self, *more_positional_stuff, **wow_we_got_key_words_up_here):
        # for instance:
        for i in range(100):
            self.step(max_value=1)
        
        for i in range(100):
            self.step(max_value=2)


"""
Example code to build a Rakan instance.
Read a networkx graph and sends it off to Xayah upon its connection.
"""
def build_rakan(nx_path):
    graph = networkx.read_gpickle(nx_path)
    print("=" * 80)
    print("Properties:", graph.graph)
    print("Adjust the Graph as you see fit. Results will be saved. Type 'c' to continue or'exit' to cancel.")
    print("=" * 80)
    import pdb; pdb.set_trace()
    networkx.write_gpickle(graph, nx_path)

    r = Rakan(len(graph.nodes), graph.graph['districts'])
    r.nx_graph = graph
    
    bar = IncrementalBar("Building Rakan (Step 1: Nodes)", max=len(graph.nodes))
    
    # load up nodes with their respective populations
    for node in sorted(graph.nodes):
        r.add_precinct(graph.nodes[node]['dis'], graph.nodes[node]['pop'])
        if isinstance(r, BaseRakanWithServer):
            try:
                r.add_vertexes(node, graph.nodes[node]['vertexes'])
            except:
                pass
        bar.next()
    
    bar.finish()

    bar = IncrementalBar("Building Rakan (Step 2: Edges)", max=len(graph.edges))

    for (node1, node2) in graph.edges:
        
        r.set_neighbors(node1, node2)
        bar.next()

    bar.finish()

    return r

if __name__ == "__main__":
    nx_path = "rakan/iowa.dnx"
    # nx_path = "rakan/test.dnx"
    rakan = build_rakan(nx_path)
    graph = networkx.read_gpickle(nx_path)
    rakan.is_valid()
    print("<Enter> to step, 'pdb' to debug, 'q' to quit, <n> to walk n times.")
    while True:
        response = input()
        if response == 'pdb': 
            import pdb; pdb.set_trace()
        elif response == 'q': 
            break
        elif response.isnumeric():
            for _ in range(int(response)):
                rakan.step()
        else:
            rakan.step()

    print("Run complete.")