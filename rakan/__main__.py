from base import BaseRakan
from xayah import Xayah
from progress.bar import IncrementalBar

import sys
import time
import math
import networkx
import threading
import socketserver
import http.server
import random as rand
from decimal import Decimal
from sys import getsizeof
from independence_tester import test

try:
    nx_path = sys.argv[1]
except:
    nx_path = "iowa.dnx"

class Rakan(BaseRakan):

    """
    Example Walk. This is the primary method for defining "runs" discussed at meetings.
    """
    def walk(self):
        one_million = 10 ** 6
        random_independence = 148
        random_maps = 10

        self.ALPHA = Decimal(0)
        self.BETA = Decimal(0)

        # Get some distance from the seed map
        for i in range(random_independence * random_maps): 
            self.step()
            if i % random_independence == 0:
                self.image("output/iowa_phase0_" + str(self.ALPHA) + "_" + str(self.BETA) + "_" + str(i) + '.png')

        # Phase 1: Gets us to ~74% from ideal
        # Score converges after ~30 iterations

        phase1_independence = 1177
        phase1_iterations = 10

        self.ALPHA = Decimal(1e-10)
        self.BETA = Decimal(0.2)

        for i in range(phase1_independence * phase1_iterations):
            self.step()
            if i % phase1_independence == 0:
                self.image("output/iowa_phase1_" + str(self.ALPHA) + "_" + str(self.BETA) + "_" + str(i) + '.png')
        
        # Phase 2: Gets us to ~13-30% from ideal
        # Score converges after ~150 iterations

        phase2_independence = 2745
        phase2_iterations = 10

        self.ALPHA = Decimal(1e-9)
        self.BETA = Decimal(0.2)

        for i in range(phase2_independence * phase2_iterations):
            self.step()
            if i % phase2_independence == 0:
                self.image("output/iowa_phase2_" + str(self.ALPHA) + "_" + str(self.BETA) + "_" + str(i) + '.png')

        
        # Phase 3: Gets us ~0.5-3% from ideal
        # Score converges after <2745 iterations

        phase3_independence = 3295
        phase3_iterations = 30

        self.ALPHA = Decimal(5e-8)
        self.BETA = Decimal(0.3)

        for i in range(phase2_independence * phase2_iterations):
            self.step()
            if i % phase2_independence == 0:
                self.image("output/iowa_phase3_" + str(self.ALPHA) + "_" + str(self.BETA) + "_" + str(i) + '.png')

        # RINSE REPEAT
        

"""
Example code to build a Rakan instance.
Read a networkx graph and sends it off to Xayah upon its connection.
"""
def build_rakan(nx_path, xyh_path="save.xyh"):
    r = Rakan(0, 0)
    x = Xayah(xyh_path, threaded=False)
    try:
        last_row = x.last()
        precincts = last_row
        r.read_nx(nx_path)
        g = r.nx_graph

        for precinct, district in enumerate(precincts):
            g.nodes[precinct]['dis'] = district

        networkx.write_gpickle(g, '~tmp')
        r.read_nx('~tmp')
        r._iterations = x._iterations
        g = r.nx_graph
    except IndexError:
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
    Set a new Beta value (compactnpopulations = [_.population for _ in rakan.districts]
                    total_population = sum(populations)
                    average_population = total_population / len(populations)
                    absolute_population_deltas = [abs(_ - average_population) for _ in populations]
                    absolute_population_differences = sum(absolute_population_deltas) / average_population
l <path>
    Load a new .dnx file
i <path>
    Spawn a thread that saves the populations = [_.population for _ in rakan.districts]
                    total_population = sum(populations)
                    average_population = total_population / len(populations)
                    absolute_population_deltas = [abs(_ - average_population) for _ in populations]
                    absolute_population_differences = sum(absolute_population_deltas) / average_populationge to the path specified.
pdb
    To enter PDB mode.
m
    To check memory consumption ofpopulations = [_.population for _ in rakan.districts]
                    total_population = sum(populations)
                    average_population = total_population / len(populations)
                    absolute_population_deltas = [abs(_ - average_population) for _ in populations]
                    absolute_population_differences = sum(absolute_population_deltas) / average_population
t <file_name> <rid1 (optional)> <rpopulations = [_.population for _ in rakan.districts]
                    total_population = sum(populations)
                    average_population = total_population / len(populations)
                    absolute_population_deltas = [abs(_ - average_population) for _ in populations]
                    absolute_population_differences = sum(absolute_population_deltas) / average_population
    To check independence of the wpopulations = [_.population for _ in rakan.districts]
                    total_population = sum(populations)
                    average_population = total_population / len(populations)
                    absolute_population_deltas = [abs(_ - average_population) for _ in populations]
                    absolute_population_differences = sum(absolute_population_deltas) / average_population
x
    Save previous walk for loadingpopulations = [_.population for _ in rakan.districts]
                    total_population = sum(populations)
                    average_population = total_population / len(populations)
                    absolute_population_deltas = [abs(_ - average_population) for _ in populations]
                    absolute_population_differences = sum(absolute_population_deltas) / average_population
"""
    server = None

    rakan = build_rakan(nx_path)
    graph = rakan.nx_graph # for pdb context
    rakan.is_valid()
    print("Rakan is live. Type 'h' for help \n")

    while True:
        response = input(">>> ")
        # debug
        if response == 'pdb':
            import pdb; pdb.set_trace()
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
        # memory
        elif response == 'm':
            print("Rakan Memory Usage:")
            print("C++ Representation Object: {:.2f} KB".format(getsizeof(rakan) / (1024)))
            print("Python District Representation: {:.2f} KB".format(getsizeof(rakan.districts) / (1024)))
            print("Python Precinct Representation: {:.2f} KB".format(getsizeof(rakan.precincts) / (1024)))
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
                    total_population = sum(populations)
                    average_population = total_population / len(populations)
                    absolute_population_deltas = [abs(_ - average_population) for _ in populations]
                    absolute_population_differences = sum(absolute_population_deltas) / average_population
                    print("Population difference from ideal: {:.2f}%".format(absolute_population_differences * 100))

                    nodes = [len(_) for _ in rakan.districts]
                    total_nodes = len(rakan)
                    average_nodes = total_nodes / len(rakan.districts)
                    absolute_node_deltas = [abs(_ - average_nodes) for _ in nodes]
                    absolute_node_differences = sum(absolute_node_deltas) / average_nodes
                    print("Precinct difference from ideal: {:.2f}%".format(absolute_node_differences * 100))
                    try:
                        print("Rejection rate of last {} moves: {:.2f}%".format(rakan._xayah.iterations, 100 - (100 * rakan._xayah._moves / rakan._xayah.iterations)))
                    except ZeroDivisionError:
                        pass
            else:
                print("Score: ", rakan.score())
                print("Pop Score: ", rakan.population_score())
                print("Pop Score (Weighted): ", Decimal(rakan.population_score()) * Decimal(rakan.ALPHA))
                print("Comp Score: ", rakan.compactness_score())
                print("Comp Score (Weighted): ", Decimal(rakan.compactness_score()) * Decimal(rakan.BETA))

                populations = [_.population for _ in rakan.districts]
                total = sum(populations)
                average = total / len(populations)
                absolute_deltas = [abs(_ - average) for _ in populations]
                absolute_differences = sum(absolute_deltas) / average
                print("Population difference from ideal: {:.2f}%".format(absolute_differences * 100))
                try:
                    print("Rejection rate of last {} moves: {:.2f}%".format(rakan._xayah.iterations, 100 - (100 * rakan._xayah._moves / rakan._xayah.iterations)))
                except ZeroDivisionError:
                    pass
        # walk
        elif response == 'w':
            start = time.time()
            rakan.walk()
            end = time.time()
            print("Walk time:", end - start, "seconds")
        elif response == 'x':
            print('Xayah Iterations:', rakan._xayah.iterations)
            print('Rakan Iterations:', rakan.iterations)
            print("Xayah save behind by {} iterations".format(len(rakan._xayah._events)))
            threading.Thread(target=rakan._xayah.save()).start()
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
        elif response.startswith('t '):
            options = response.split(' ', 3) # t (file name) (rid1) (rid2)
            result = False
            if len(options) == 2:
                result = test(options[1])
            elif len(options) == 4:
                result = test(options[1], options[2], options[3])
            else:
                print("Invalid set of inputs")
                continue

            if result:
                print("The sequence from the file {} is independent".format(options[1]))
            else:
                print("The sequence from the file {} is NOT independent".format(options[1]))
        # ??
        else:
            print("Unknown Command")

    print("Run complete.")


if __name__ == "__main__":
    routine()
