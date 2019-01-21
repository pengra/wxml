# Some code to do super precincts

import networkx

# Create a Rakan from the layer by calling read_nx on new graph
# Create a networkx graph from the super precincts, plug that networkx into some build function
# Let that rakan run, once it finishes, save the state of rakan
# Create rakan from one layer down, populate with the districts loaded from last state save
# Keep going until reaching the base

"""
Given a base layer, clump them together so they all form the size of <granularity> super precincts.
The new layer is the base layer + 1.
"""
def build_layer(base_layer: int, granularity: int):
    pass

def superize(graph, base_layer, granularity):
    if base_layer == 0:
        pass
        

if __name__ == "__main__":
    pass
    # Need levels
    # Go from 100 precincts -> 1000 precincts -> 10000 precincts