from rakan.rakan import PyRakan

import asyncio
import websockets
import threading

import json
import time

class BaseRakan(PyRakan):
    """
    Basic Rakan format. Use as a template.
    """
    iterations = 0 # iterations rakan has gone through

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
    update_speed = 100000 # number of seconds of how often rakan sends xayah an update
    iterations = 0 # iterations rakan has gone through

    def __init__(self, *args, **kwargs):
        print("Rakan running with websocket server!")
        super().__init__(*args, **kwargs)
        self._create_websocket()
        
        self._vertexes = {} # vertexes of each rid

    def add_vertexes(self, rid, vertexes):
        self._vertexes[rid] = vertexes

    # In javascript, connect via: new WebSocket("ws://127.0.0.1:3001"); 
    # Build a websocket server on specified port.
    def _create_websocket(self):
        self._init_socket = websockets.serve(self.send_seed, '127.0.0.1', self.ws_port)
        asyncio.get_event_loop().run_until_complete(self._init_socket)

        wst = threading.Thread(target=asyncio.get_event_loop().run_forever)
        wst.daemon = True
        wst.start()

    def send_seed(self, websocket, path):
        print("New Xayah Client!")
        for precinct in self.precincts:
            yield from websocket.send(
                json.dumps({
                    "precinct_vertexes": [v[0] for k, v in self._vertexes.items()],
                    "precint_districts": [_.district for _ in self.precincts],
                    "iterations": self.iterations,
                })
            )
        while True:
            yield from websocket.send(json.dumps({

            }))
            time.sleep(self.update_speed)

    # When connected, send xayah update every n seconds
    @asyncio.coroutine
    def send_move(self, websocket, path):
        while True:
            yield from websocket.send(json.dumps({
                "1": 3,
                "3": 1,
            }))
            time.sleep(self.update_speed)
        print("> Updating Xayah")


    # Scold the user for not implementing anything
    def step(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")

    def walk(self, *args, **kwargs):
        raise NotImplementedError("Not implemented by user!")
