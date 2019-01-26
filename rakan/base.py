try:
    from rakan import PyRakan
except ImportError:
    # py.test import
    from rakan.rakan import PyRakan

import asyncio
import websockets
import threading
import networkx

import random
import json
import time

import os

class BaseRakan(PyRakan):
    """
    Basic Rakan format. Use as a template.
    Use for production code.
    """
    iterations = 0 # iterations rakan has gone through
    super_layer = 0 # super precinct layer
    nx_graph = None # the graph object
    _move_history = [] # the set of moves unreported to xayah

    """
    Save the current rakan state to a file.
    Modifies self.nx_graph
    """
    def save(self, nx_path="save.dnx"):
        for precinct in self.precincts:
            self.nx_graph.nodes[precinct.rid]['dis'] = precinct.district
        self.nx_graph.graph['iterations'] = self.iterations
        self.nx_graph.graph['move_history'] = self._move_history
        networkx.write_gpickle(self.nx_graph, nx_path)

    """
    Save the current rakan state to a geojson file.
    Does not modify self.nx_graph
    """
    def export(self, json_path="save.json"):
        features = []
        for rid, precinct in enumerate(self.precincts):
            features.append({
                "type": "Feature",
                "properties": {
                    "district": precinct.district,
                    "description": """<strong>{name}</strong><br/>
                    ID: {rid}<br/>
                    Population: {pop}<br/>
                    District: {dis}<br/>
                    """.format(
                        name=self.nx_graph.nodes[precinct.rid]['name'],
                        rid=rid,
                        pop=precinct.population,
                        dis=precinct.district,
                    )
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": self.nx_graph.nodes[precinct.rid]['vertexes']
                }
            })
            self.nx_graph.nodes[precinct.rid]['dis'] = precinct.district
        
        geojson = json.dumps({
            "type": "FeatureCollection",
            "features": features
        })

        if not (json_path is None):
            with open(json_path, 'w') as handle:
                handle.write(geojson)
        else:
            return geojson

    """
    Generate a mapjsgl page.
    Used for analyzing how the districts have crawled around.
    """
    def report(self, dir_path="save"):
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        self.export(json_path=os.path.join(dir_path, "map.geojson"))
        self.save(nx_path=os.path.join(dir_path, "save.dnx"))
        with open("rakan/template.htm") as handle:
            template = handle.read()
            with open(os.path.join(dir_path, "index.html"), "w") as w_handle:
                w_handle.write(template.replace(
                    '{"$DA":"TA$"}', '"./map.geojson"'
                ).replace(
                    '"{$IT$}"', str(self.iterations)
                ).replace(
                    '{"$SC"$}', str(self.score())
                ).replace(
                    '{"$SCP"$}', str(self.population_score())
                ).replace(
                    '{"$SCC"$}', str(self.compactness_score())
                ).replace(
                    '{"$AL"$}', str(self.ALPHA)
                ).replace(
                    '{"$BE"$}', str(self.BETA)
                ))
        with open(os.path.join(dir_path, "moves.json"), 'w') as handle:
            handle.write(json.dumps(self.move_history))

    @property
    def move_history(self):
        """
        Read only accessor to latest moves
        """
        return self._move_history

    def record_move(self, rid, district, prev):
        """
        Record the move by rid and district.
        Does not verify if the move plugged in is valid, nor if it actually happened.

        This method should only be called after move_precinct with the same parameters
        succesfully executes.
        """
        self._move_history.append({
            "prev": (rid, prev),
            "move": (rid, district),
            "pscore": self.population_score(),
            "cscore": self.compactness_score(),
            "score": self.score(),
            "alpha": self.ALPHA,
            "beta": self.BETA,
            "index": self.iterations,
        })
        
    """
    Build rakan from a .dnx file.
    """
    def read_nx(self, nx_path):
        self.nx_graph = networkx.read_gpickle(nx_path)
        self._reset(len(self.nx_graph.nodes), self.nx_graph.graph['districts'])
        for node in sorted(self.nx_graph.nodes):
            self.add_precinct(self.nx_graph.nodes[node]['dis'], self.nx_graph.nodes[node]['pop'])
        for (node1, node2) in self.nx_graph.edges:
            self.set_neighbors(node1, node2)
        self.iterations = self.nx_graph.graph.get('iterations', 0)
        self._move_history = self.nx_graph.graph.get('move_history', list())

    """
    A Metropolis Hastings Algorithm Step.
    Argument can be passed in.

    Arguments are completely arbritary and can be rewritten by the user.
    """
    def step(self):
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

    def walk(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")

    def score(self, rid=None, district=None):
        raise NotImplementedError("Scoring algorithm not implemented!")

    def score_ratio(self, rid, district):
        raise NotImplementedError("Scoring algorithm not implemented!")

