try:
    from rakan.rakan import PyRakan
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
            self.nx_graph[precinct.rid]['dis'] = precinct.district
        networkx.save_gpickle(self.nx_graph, nx_path)

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

class BaseRakanWithServer(BaseRakan):
    """
    Rakan with a websocket for communication with Xayah.
    """
    ws_port = 3001 # websocket port
    update_speed = 1 # number of seconds of how often rakan sends xayah an update
    _move_history = [] # the set of moves unreported to xayah
    _thread_lock = False # a threadlock to prevent skipping moves

    def read_nx(self, nx_path):
        self.nx_graph = networkx.read_gpickle(nx_path)
        self._reset(len(self.nx_graph.nodes), self.nx_graph.graph['districts'])
        for node in sorted(self.nx_graph.nodes):
            self.add_precinct(self.nx_graph.nodes[node]['dis'], self.nx_graph.nodes[node]['pop'])
            self.add_vertexes(node, self.nx_graph.nodes[node]['vertexes'])
        for (node1, node2) in self.nx_graph.edges:
            self.set_neighbors(node1, node2)

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
        
        self._vertexes = {} # vertexes of each rid

    def add_vertexes(self, rid, vertexes):
        """
        Adds a log of vertexes. Does not verify the vertexes are accurate.
        Method for Xayah's rendering of precinct.
        """
        self._vertexes[rid] = vertexes

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
        """
        Method that returns json blobs sent directly to Xayah.
        By default, it sends all information of all precincts
            - geographic information of precinct polygon (precinct_vertexes)
            - what district each precinct is in (precinct_districts)
            - what precinct is "touching" other precincts on the graph (edges)
            - how long rakan has been running (iterations)
        Then, after every self.update_speed seconds, send smaller bits of information
            - what precincts changed districts (update)
            - how long rakan has been running (iterations)
        """
        print("New Xayah Client!")
        # Send the initial blob of everything Xayah needs to know
        yield from websocket.send(json.dumps({
            "precinct_vertexes": [v[0] for k, v in self._vertexes.items()],
            "precinct_districts": [_.district for _ in self.precincts],
            "edges": [_ for _ in self.nx_graph.edges] if self.nx_graph else [],
            "iterations": self.iterations,
        }))
        # Update infinitely
        while True:
            # Send Xayah move history and clear it.

            # Threading logic
            # If resource is busy, try again until it's free
            if not self._thread_lock:
                # lock resource
                self._thread_lock = True
                # transmit resource
                yield from websocket.send(json.dumps({
                    'update': self._move_history,
                    'iterations': self.iterations,
                }))
                # reset resource
                self._move_history = []
                # unlock resource
                self._thread_lock = False
                # take a breather
                time.sleep(self.update_speed)

    # Scold the user for not implementing anything

    def step(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")

    def walk(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")

