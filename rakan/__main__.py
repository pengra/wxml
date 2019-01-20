from base import BaseRakanWithServer, BaseRakan
from progress.bar import IncrementalBar

import faulthandler; faulthandler.enable()
import time

import random
import networkx

class Rakan(BaseRakanWithServer):

    """
    An example step
    Argument can be passed in.

    Arguments are completely arbritary and can be rewritten by the user.
    """
    def step(self, max_value=1, *more_positional_stuff, **wow_we_got_key_words_up_here):
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

    r = Rakan()
    r.read_nx(nx_path)

    return r

if __name__ == "__main__":
    # nx_path = "rakan/iowa.dnx"
    nx_path = "rakan/washington.dnx"
    rakan = build_rakan(nx_path)
    graph = networkx.read_gpickle(nx_path)
    input("<Enter to run validation. Server is currently live.>")
    rakan.is_valid()
    print("<Enter> to step, 'pdb' to debug, 'q' to quit, <n> to walk n times.")
    while True:
        response = input()
        if response == 'pdb': 
            import pdb; pdb.set_trace()
        elif response == 'q': 
            break
        elif response.isnumeric():
            target = int(response)
            bar = IncrementalBar("Walking {} steps".format(target), max=target)
            start = time.time()
            for _ in range(target):
                bar.next()
                rakan.step()
            end = time.time()
            bar.finish()
            print("Average iterations / second:", target / (end - start))
        else:
            rakan.step()

    print("Run complete.")