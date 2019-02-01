from base import BaseRakan
from servertools import save_current_scores
from progress.bar import IncrementalBar

import sys
import time
import math
import networkx
import threading
import socketserver
import http.server
from decimal import Decimal


try:
    nx_path = sys.argv[1]
except:
    nx_path = "rakan/iowa.dnx"
    # nx_path = "iowa2/save.dnx"
    # nx_path = "rakan/newwashington.dnx"
    # nx_path = "washingtonrandom/save.dnx"

e = Decimal(math.e)

class Rakan(BaseRakan):

    ALPHA = Decimal(4 * (0.1 ** 11)) # # 10 ** -15 # Weight for population
    BETA = Decimal(0.008) # ** 10 #10 ** -2   # Weight for compactness

    """
    An example scoring algorithm.
    """
    def score(self, rid=None, district=None):
        # Linear to prevent overflow errors
        return pow(e,
            (self.ALPHA * Decimal(self.population_score(rid, district))) +
            (self.BETA * Decimal(self.compactness_score(rid, district)))
        )

    """
    Example Walk. This is the primary method for defining "runs" discussed at meetings.
    """
    def score_ratio(self, rid, district):
        return pow(e, (
            (self.ALPHA * Decimal((self.population_score(rid, district) - self.population_score()))) +
            (self.BETA * Decimal((self.compactness_score(rid, district) - self.compactness_score())))
        ))

"""
Example code to build a Rakan instance.
Read a networkx graph and sends it off to Xayah upon its connection.
"""
def build_rakan(nx_path):
    r = Rakan(0, 0)
    r.read_nx(nx_path)
    return r


def routine():
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
p
    Produce a server that Xayah can communicate to. (Already running)
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
    Set a new Beta value (compactness weight)
l <path>
    Load a new .dnx file
i <path>
    Spawn a thread that saves the current map as an image to the path specified.
"""
    server = None
    
    rakan = build_rakan(nx_path)
    graph = rakan.nx_graph
    rakan.is_valid()
    print("Rakan is live. Type 'h' for help \n")

    while True:
        response = input(">>> ")
        # debug
        if response == 'pdb': 
            import pdb; pdb.set_trace()
        elif response == 'p':
            if server is None:
                server = threading.Thread(target=(lambda: save_current_scores(rakan)))
                server.start()
        # image
        elif response.startswith('i '):
            image = threading.Thread(target=lambda: rakan.image(image_path=response.split(' ', 1)[1] + '.png'))
            image.start()
            print("Image thread started")
        # quit
        elif response == 'q': 
            break
        # load a .dnx file
        elif response.startswith('l '):
            rakan = build_rakan(response.split(' ', 1)[1])
            graph = rakan.nx_graph
            rakan.is_valid()
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
                try:
                    old_score = rakan.score()
                    old_pop = rakan.population_score()
                    old_comp = rakan.compactness_score()
                    start = time.time()
                    for _ in range(target):
                        bar.next()
                        rakan.step()
                    
                except (Exception, KeyboardInterrupt):
                    pass
                finally:
                    end = time.time()
                    new_score = rakan.score()
                    new_pop = rakan.population_score()
                    new_comp = rakan.compactness_score()
                    bar.finish()
                    print("Average iterations / second:", target / (end - start))
                    print("Average seconds / iteration:", (end - start) / target)
                    print("Total time: ", end - start)
                    print("Score change (old: {}, new: {}): {}".format(old_score, new_score, new_score - old_score))
                    print("Pop Score change (old: {}, new: {}): {}".format(old_pop, new_pop, new_pop - old_pop))
                    print("Comp Score change (old: {}, new: {}): {}".format(old_comp, new_comp, new_comp - old_comp))
                    
                    populations = [_.population for _ in rakan.districts]
                    total = sum(populations)
                    average = total / len(populations)
                    absolute_deltas = [abs(_.population - average) for _ in populations]
                    absolute_differences = sum(absolute_deltas) / average
                    print("Population difference from ideal: {:.2f}%".format(absolute_differences * 100))
            else:
                print("Score: ", rakan.score())
                print("Pop Score: ", rakan.population_score())
                print("Pop Score (Weighted): ", Decimal(rakan.population_score()) * rakan.ALPHA)
                print("Comp Score: ", rakan.compactness_score())
                print("Comp Score (Weighted): ", Decimal(rakan.compactness_score()) * rakan.BETA)
                
                populations = [_.population for _ in rakan.districts]
                total = sum(populations)
                average = total / len(populations)
                absolute_deltas = [abs(_.population - average) for _ in populations]
                absolute_differences = sum(absolute_deltas) / average
                print("Population difference from ideal: {:.2f}%".format(absolute_differences * 100))
        # walk
        elif response == 'w':
            start = time.time()
            rakan.walk()
            end = time.time()
            print("Walk time:", end - start, "seconds")
        # new weights
        elif response.startswith('a'):
            if len(response.split(' ')) == 1:
                pass
            else:
                try:
                    rakan.ALPHA = Decimal(response.split(' ', 1)[1])
                except:
                    pass
            print("Set new ALPHA value:", rakan.ALPHA)
        # new weights
        elif response.startswith('b'):
            if len(response.split(' ')) == 1:
                pass
            else:
                try:
                    rakan.BETA = Decimal(response.split(' ', 1)[1])
                except:
                    pass
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


if __name__ == "__main__":
    routine()