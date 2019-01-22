try:
    from rakan import PyRakan
except ImportError:
    # py.test import
    from .rakan.rakan import PyRakan

import asyncio
import websockets
import threading
import networkx

import json
import time

class BaseRakan(PyRakan):
    """
    Basic Rakan format. Use as a template.
    Use for production code.
    """
    iterations = 0 # iterations rakan has gone through
    super_layer = 0 # super precinct layer
    nx_graph = None # the graph object

    """
    Save the current rakan state to a file.
    Modifies self.nx_graph
    """
    def save(self, nx_path="save.dnx"):
        for precinct in self.precincts:
            self.nx_graph.nodes[precinct.rid]['dis'] = precinct.district
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
    def report(self, html_path="save.html"):
        geojson = self.export(json_path=None)
        with open("rakan/template.htm") as handle:
            template = handle.read()
            with open(html_path, "w") as w_handle:
                w_handle.write(template.replace('{"$DA":"TA$"}', geojson))
        
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

    # Scold the user for not implementing anything
    def step(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")

    def walk(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")

    def score(self, rid=None, district=None):
        # alpha = -0.2
        # beta = -1.2
        # return score = math.exp(
        #   (alpha * self.population_score(rid, district)) + 
        #   (beta * self.compactness_score(rid, district))
        # )
        raise NotImplementedError("Scoring algorithm not implemented!")



"""
DEPRECIATED.
"""
class BaseRakanWithServer(BaseRakan):
    """
    Rakan with a websocket for communication with Xayah.
    """
    ws_port = 3001 # websocket port
    update_speed = 1 # number of seconds of how often rakan sends xayah an update
    _move_history = [] # the set of moves unreported to xayah
    _thread_lock = False # a threadlock to prevent skipping moves

    @property
    def move_history(self):
        """
        Read only accessor to latest moves
        """
        return self._move_history

    def record_move(self, rid, district):
        """
        Record the move by rid and district.
        Does not verify if the move plugged in is valid, nor if it actually happened.

        This method should only be called after move_precinct with the same parameters
        succesfully executes.
        """
        while True:
            # Thread lock logic

            # is resource being accessed by different thread?
            # if so, wait, otherwise, modify
            if not self._thread_lock:
                # resource is not busy, lock the thread
                self._thread_lock = True
                # modify resource
                self._move_history.append((rid, district))
                # unlock resource
                self._thread_lock = False
                break
    
    def __init__(self, *args, **kwargs):
        """
        Same exact arguments as parent.

        Only difference is that this instance tracks vertexes and creates a websocket
        in its own thread.
        """
        print("Rakan running with websocket server!")
        super().__init__(*args, **kwargs)
        self._create_websocket()

    def _create_websocket(self):
        """
        Build a websocket for xayah to connect to.
        Port defined by self.ws_port.
        Will always run on localhost.

        Xayah Connect via (js):
            const socket = new WebSocket("ws://127.0.0.1:3001");
        """
         # Create the socket
        self._init_socket = websockets.serve(self.send_seed, '127.0.0.1', self.ws_port)
        
        # Create in seperate thread and run forever
        asyncio.get_event_loop().run_until_complete(self._init_socket)
        wst = threading.Thread(target=asyncio.get_event_loop().run_forever)
        # Daemonize & Start
        wst.daemon = True
        wst.start()

    def send_seed(self, websocket, path):
        # Send the initial blob of everything Xayah needs to know
        yield from websocket.send(self.export(None))
        
    def districts(self, websocket, path):
        # Update infinitely
        last_iteration = self.iterations
        while True:
            # Send Xayah move history and clear it.

            # Threading logic
            # If resource is busy, try again until it's free
            if not self._thread_lock and last_iteration != self.iterations:
                # lock resource
                self._thread_lock = True
                # transmit resource
                yield from websocket.send(json.dumps({
                    'update': self._move_history,
                    'iterations': self.iterations,
                }))
                last_iteration = self.iterations
                # reset resource
                self._move_history = []
                # unlock resource
                self._thread_lock = False
                # take a breather
                time.sleep(self.update_speed)
            
            time.sleep(0.01)

    # Scold the user for not implementing anything

    def step(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")

    def walk(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")

