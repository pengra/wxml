from rakan import PyRakan
from xayah import Xayah
from servertools import Event, PENGRA_ENDPOINT

import asyncio
import websockets
import threading
import networkx
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import geopandas as gpd

from progress.bar import IncrementalBar
from sys import getsizeof
import requests
import pickle
import threading
import random
import json
import time
import os


class BaseRakan(PyRakan):
    """
    Basic Rakan format. Use as a template.
    Use for production code.
    """
    nx_graph = None  # the graph object
    max_size = 1000  # 10k logs should be a sizeable bite for the server

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._id = None
        self._xayah = Xayah("save.xyh")  # the set of moves unreported to xayah
        self._step_size = 1

    def step(self):
        result = super().step()
        if self.iterations % self._step_size == 0 and result:
            self._xayah.move(precincts=self.precincts, ALPHA=self.ALPHA, BETA=self.BETA, population_score=self.population_score(
            ), compactness_score=self.compactness_score(), score=self.score())
        else:
            self._xayah.fail(precincts=self.precincts, ALPHA=self.ALPHA, BETA=self.BETA, population_score=self.population_score(
            ), compactness_score=self.compactness_score(), score=self.score())

    @property
    def ALPHA(self):
        return self._ALPHA

    @property
    def BETA(self):
        return self._BETA

    @ALPHA.setter
    def ALPHA(self, value: float):
        self._ALPHA = value
        self._xayah.weight(precincts=self.precincts, ALPHA=self.ALPHA, BETA=self.BETA, population_score=self.population_score(
        ), compactness_score=self.compactness_score(), score=self.score())

    @BETA.setter
    def BETA(self, value: float):
        self._BETA = value
        self._xayah.weight(precincts=self.precincts, ALPHA=self.ALPHA, BETA=self.BETA, population_score=self.population_score(
        ), compactness_score=self.compactness_score(), score=self.score())

    """
    Save the current rakan state to a file.
    Modifies self.nx_graph
    """

    def save(self, nx_path="save.dnx"):
        for precinct in self.precincts:
            self.nx_graph.nodes[precinct.rid]['dis'] = precinct.district
        self.nx_graph.graph['iterations'] = self.iterations
        networkx.write_gpickle(self.nx_graph, nx_path)

    """
    Save the current rakan state to a image.
    """

    def image(self, image_path="img.png"):
        fig, ax = plt.subplots(1)
        bar = IncrementalBar("Creating Image", max=len(self.precincts))
        for precinct in self.precincts:
            xs = [coord[0]
                  for coord in self.nx_graph.nodes[precinct.rid]['vertexes'][0]]
            ys = [coord[1]
                  for coord in self.nx_graph.nodes[precinct.rid]['vertexes'][0]]
            ax.fill(xs, ys, color=[
                "#001f3f",  # Navy
                "#3D9970",  # Olive
                "#FF851B",  # Orange
                "#85144b",  # Maroon
                "#AAAAAA",  # Silver
                "#0074D9",  # Blue
                "#2ECC40",  # Green
                "#FF4136",  # Red
                "#F012BE",  # Fuchsia
                "#111111",  # Black
                "#7FDBFF",  # Aqua
                "#FFDC00",  # Yellow
                "#B10DC9",  # Purple
                "#39CCCC",  # Teal
                "#01FF70",  # Lime
            ][precinct.district], linewidth=0.1)
            bar.next()
        plt.savefig(image_path, dpi=900)
        plt.close(fig)
        bar.finish()

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
    """

    def write_array(self, file_path="report.txt"):
        mode = 'a' if os.path.isfile(file_path) else 'w'
        with open(file_path, mode) as handle:
            handle.write(json.dumps(
                [_.district for _ in self.precincts]
            ))
            handle.write("\n")

    """
    Generate a mapjsgl page.
    Used for analyzing how the districts have crawled around.
    """

    def report(self, dir_path="save", include_json=True, include_export=True, include_save=True):
        try:
            os.mkdir(dir_path)
        except FileExistsError:
            pass
        if include_export:
            self.export(json_path=os.path.join(dir_path, "map.geojson"))
        if include_save:
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
        if include_json:
            with open(os.path.join(dir_path, "moves.json"), 'w') as handle:
                handle.write(json.dumps([_.json for _ in self.move_history]))

    @property
    def move_history(self):
        """
        Read only accessor to latest moves
        """
        return list(self._xayah)

    """
    Build rakan from a .dnx file.
    """

    def read_nx(self, nx_path):
        self.nx_graph = networkx.read_gpickle(nx_path)
        self._reset(len(self.nx_graph.nodes), self.nx_graph.graph['districts'])
        for node in sorted(self.nx_graph.nodes):
            self.add_precinct(
                int(self.nx_graph.nodes[node]['dis']),
                int(self.nx_graph.nodes[node]['pop']),
                int(self.nx_graph.nodes[node]['d_active']),
                int(self.nx_graph.nodes[node]['r_active']),
                int(self.nx_graph.nodes[node]['o_active']),
            )
        for (node1, node2) in self.nx_graph.edges:
            self.set_neighbors(node1, node2)
        self._iterations = self.nx_graph.graph.get('iterations', 0)
        self._xayah.seed(precincts=self.precincts, ALPHA=self.ALPHA, BETA=self.BETA, population_score=self.population_score(
        ), compactness_score=self.compactness_score(), score=self.score())

    """
    A statistical test to check two random precincts are in the same district
    """

    def precinct_in_same_district(self, rid1, rid2):
        return self.precincts[rid1].district == self.precincts[rid2].district

    def walk(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")
