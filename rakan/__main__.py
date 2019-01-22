from base import BaseRakanWithServer, BaseRakan
from progress.bar import IncrementalBar

import time
import random
import math
import networkx

class Rakan(BaseRakan):

    ALPHA = -(0.1 ** 18) # Weight for population

    """
    An example step
    Argument can be passed in.

    Arguments are completely arbritary and can be rewritten by the user.
    """
    def step(self, max_value=1, *more_positional_stuff, **wow_we_got_key_words_up_here):
        precinct, district = self.propose_random_move()

        try:
            if random.random() <= (self.score() / self.score(precinct, district)):
                # Sometimes propose_random_move severs districts, and move_precinct will catch that.
                self.move_precinct(precinct, district)
                self.iterations += 1
        except ValueError:
            # Sometimes the proposed move severs the district
            # Just try again
            self.step()

    """
    An example scoring algorithm.
    """
    def score(self, rid=None, district=None):
        return math.exp(
            self.ALPHA * self.population_score(rid, district)
        )


"""
Example code to build a Rakan instance.
Read a networkx graph and sends it off to Xayah upon its connection.
"""
def build_rakan(nx_path):
    graph = networkx.read_gpickle(nx_path)
    print("=" * 80)
    print("Properties:", graph.graph)
    print("Adjust the Graph as you see fit. Results will be saved. Type 'pdb' to modify.")
    print("=" * 80)
    if input(">>> continue? <enter> or 'pdb' ") == 'pdb':
        import pdb; pdb.set_trace()
        networkx.write_gpickle(graph, nx_path)

    r = Rakan()
    r.read_nx(nx_path)

    return r

if __name__ == "__main__":
    help_ = """
h
    Show this help message
q
    Quit the program
<Enter>
    Run one iteration
<any integer>
    Run that many iterations
w
    Call user defined rakan.walk()
e <name>
    Export the current state as geojson int <name>.json.
r <name>
    Export a report of the current state
s <name>
    Save current graph into <name>.dnx."""
    
    # nx_path = "rakan/iowa.dnx"
    # nx_path = "rakan/washington.dnx"
    nx_path = "rakan/newwashington.dnx"
    # nx_path = "wa.140100.dnx"
    
    rakan = build_rakan(nx_path)
    graph = rakan.nx_graph
    rakan.is_valid()
    print("Rakan is live. 'h' for help \n")
    while True:
        response = input(">>> ")
        # debug
        if response == 'pdb': 
            import pdb; pdb.set_trace()
        # quit
        elif response == 'q': 
            break
        # help
        elif response == 'h':
            print(help_)
        # save
        elif response.startswith('s '):
            rakan.save(nx_path=response.split(' ', 1)[1] + '.dnx')
        # export
        elif response.startswith('e '):
            rakan.export(json_path=response.split(' ', 1)[1] + '.json')
        # export
        elif response.startswith('r '):
            rakan.report(html_path=response.split(' ', 1)[1] + '.html')
        # run
        elif response.isnumeric():
            target = int(response)
            bar = IncrementalBar("Walking {} steps".format(target), max=target)
            old_score = rakan.score()
            start = time.time()
            for _ in range(target):
                bar.next()
                rakan.step()
            end = time.time()
            bar.finish()
            new_score = rakan.score()
            print("Average iterations / second:", target / (end - start))
            print("Average seconds / iteration:", (end - start) / target)
            print("Total time: ", end - start)
            print("Score change (old: {}, new: {}): {}".format(old_score, new_score, new_score - old_score))
        # walk
        elif response == 'w':
            start = time.time()
            rakan.walk()
            end = time.time()
            print("Walk time:", end - start, "seconds")
        # one step
        elif response == '':
            start = time.time()
            rakan.step()
            end = time.time()
            print("Average iterations / second:", 1 / (end - start))
            print("iteration completed in:", (end - start), 'seconds')
        # ??
        else:
            print("Unknown Command")

    print("Run complete.")