from base import BaseRakanWithServer, BaseRakan
from progress.bar import IncrementalBar

import time
import random
import math
import networkx

import http.server
import socketserver

class Rakan(BaseRakan):

    ALPHA = 0.1 ** 14 # 10 ** -15 # Weight for population
    BETA = 0.2 ** 1 #10 ** -2   # Weight for compactness

    """
    An example step
    Argument can be passed in.

    Arguments are completely arbritary and can be rewritten by the user.
    """
    def step(self, max_value=1, *more_positional_stuff, **wow_we_got_key_words_up_here):
        precinct, district = self.propose_random_move()
        prev_district = self.district_of(precinct)

        try:
            if self.score(precinct, district) < self.score():
                self.move_precinct(precinct, district)
                self.record_move(precinct, district, prev_district)
                self.iterations += 1
            elif random.random() < self.score_ratio(precinct, district):
                # Sometimes propose_random_move severs districts, and move_precinct will catch that.
                self.move_precinct(precinct, district)
                self.record_move(precinct, district, prev_district)
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
            (self.ALPHA * self.population_score(rid, district)) +
            (self.BETA * self.compactness_score(rid, district))
        )

    """
    An example scoring ratio algorithm.
    """
    def score_ratio(self, rid, district):
        return math.exp(
            (self.ALPHA * (self.population_score() - self.population_score(rid, district))) +
            (self.BETA * (self.compactness_score() - self.compactness_score(rid, district)))
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
    Export the current state as geojson int <name>.geojson.
r <name>
    Export a report of the current state
s <name>
    Save current graph into <name>.dnx.
pdb
    Start debugging
a <value>
    Set a new Alpha value (population weight)
b <value>
    Set a new Beta value (compactness weight)"""
    
    # nx_path = "rakan/iowa.dnx"
    # nx_path = "rakan/washington.dnx"
    # nx_path = "rakan/newwashington.dnx"
    # nx_path = "wa.140100.dnx"
    nx_path = "million.dnx"
    
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
            rakan.report(dir_path=response.split(' ', 1)[1])
            print("Hit Ctrl + C at any time to break")
            httpd = socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler)
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass
            finally:
                httpd.server_close()
                print()
        # run
        elif response.isnumeric():
            target = int(response)
            if target > 0:
                bar = IncrementalBar("Walking {} steps".format(target), max=target)
                old_score = rakan.score()
                old_pop = rakan.population_score()
                old_comp = rakan.compactness_score()
                start = time.time()
                for _ in range(target):
                    bar.next()
                    rakan.step()
                end = time.time()
                bar.finish()
                new_score = rakan.score()
                new_pop = rakan.population_score()
                new_comp = rakan.compactness_score()
                print("Average iterations / second:", target / (end - start))
                print("Average seconds / iteration:", (end - start) / target)
                print("Total time: ", end - start)
                print("Score change (old: {}, new: {}): {}".format(old_score, new_score, new_score - old_score))
                print("Pop Score change (old: {}, new: {}): {}".format(old_pop, new_pop, new_pop - old_pop))
                print("Comp Score change (old: {}, new: {}): {}".format(old_comp, new_comp, new_comp - old_comp))
            else:
                print("Score: ", rakan.score())
                print("Pop Score: ", rakan.population_score())
                print("Comp Score: ", rakan.compactness_score())
        # walk
        elif response == 'w':
            start = time.time()
            rakan.walk()
            end = time.time()
            print("Walk time:", end - start, "seconds")
        # new weights
        elif response.startswith('a '):
            if response.split(' ', 1)[1] == 'n':
                rakan.ALPHA = 0
            else:
                rakan.ALPHA = 0.1 ** int(response.split(' ', 1)[1])
            print("Set new ALPHA value:", rakan.ALPHA)
        # new weights
        elif response.startswith('b '):
            if response.split(' ', 1)[1] == 'n':
                rakan.BETA = 0
            else:
                rakan.BETA = 0.1 ** int(response.split(' ', 1)[1])
            print("Set new BETA value:", rakan.BETA)
        # one step
        elif response == '':
            old_score = rakan.score()
            old_pop = rakan.population_score()
            old_comp = rakan.compactness_score()
            start = time.time()
            rakan.step()
            end = time.time()
            new_score = rakan.score()
            new_pop = rakan.population_score()
            new_comp = rakan.compactness_score()
            print("Average iterations / second:", 1 / (end - start))
            print("iteration completed in:", (end - start), 'seconds')
            print("Total time: ", end - start)
            print("Score change (old: {}, new: {}): {}".format(old_score, new_score, new_score - old_score))
            print("Pop Score change (old: {}, new: {}): {}".format(old_pop, new_pop, new_pop - old_pop))
            print("Comp Score change (old: {}, new: {}): {}".format(old_comp, new_comp, new_comp - old_comp))
        # ??
        else:
            print("Unknown Command")

    print("Run complete.")