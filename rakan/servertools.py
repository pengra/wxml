import socket
import json

HEADERS = b"HTTP/1.1 200 OK\nServer: Rakan\nConnection: close\nContent-Type: application/json\nAccess-Control-Allow-Origin: *\n\n"
OUTPUT_LOCATION = "./rakan/values/"
ADDRESS = '127.0.0.1:4200'

class Event(object):

    def __init__(self, type, data=None):
        assert type in ['start', 'move', 'fail', 'weight', 'burn start', 'burn end', 'anneal start', 'anneal end']
        self.type = type
        self.data = data


def save_current_scores(rakan_instance):
    sock = socket.socket()
    sock.bind((ADDRESS.split(':')[0], int(ADDRESS.split(':')[1])))
    
    while True:
        sock.listen(1)
        conn, address = sock.accept()
        conn.send(HEADERS)
        try:
            conn.send(json.dumps(
                rakan_instance.move_history[-1]
            ).encode('utf-8'))
        except:
            conn.send(json.dumps({
                "pscore": rakan_instance.population_score(),
                "cscore": rakan_instance.compactness_score(),
                "score": float(rakan_instance.score()),
                "alpha": float(rakan_instance.ALPHA),
                "beta": float(rakan_instance.BETA),
                "index": rakan_instance.iterations,
            }).encode('utf-8'))
        conn.close()
