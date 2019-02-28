import sqlite3
from collections import deque
from threading import Thread
import time
from random_sequence_tests import chisquare_independence_test, r_value_independence_test


class Xayah(object):

    def __init__(self, filename):
        if not filename.endswith('.xyh'):
            filename += '.xyh'
        self.filename = filename
        self.queue = deque()
        Thread(target=self.worker).start()

    def worker(self):
        self._conn = sqlite3.connect(self.filename)
        self._cur = self._conn.cursor()
        while True:
            if len(self.queue) > 0:
                task_type, params = self.queue.popleft()
                getattr(self, task_type)(**params)
            else:
                time.sleep(0.1)

    def do(self, *args, **kwargs):
        self._cur.execute(*args, **kwargs)
        self._conn.commit()

    def seed(self, **rakan):
        self.queue.append(('do_seed', rakan))

    def move(self, **rakan):
        self.queue.append(('do_move', rakan))

    def fail(self, **rakan):
        self.queue.append(('do_fail', rakan))

    def weight(self, **rakan):
        self.queue.append(('do_weight', rakan))

    def do_seed(self, **rakan):
        self._iterations = 0
        self._moves = 0
        precinct_table = ", ".join(['precinct_{} INTEGER'.format(
            precinct_id) for precinct_id in range(len(rakan['precincts']))])
        self.do('CREATE TABLE history (iteration INTEGER, action_ INTEGER, {}, alpha REAL, beta REAL, raw_pop_score REAL, raw_comp_score REAL, score REAL);'.format(precinct_table))
        self.do_move(**rakan)

    def do_move(self, **rakan):  # ACTION CODE = 0
        self._iterations += 1
        self._moves += 1
        self.do('INSERT INTO history VALUES ({iteration}, 0, {precincts}, {alpha}, {beta}, {raw_pop}, {raw_comp}, {score});'.format(
            iteration=self.iterations,
            precincts=", ".join([str(_.district) for _ in rakan['precincts']]),
            alpha=rakan['ALPHA'],
            beta=rakan['BETA'],
            raw_pop=rakan['population_score'],
            raw_comp=rakan['compactness_score'],
            score=rakan['score'],
        ))

    def do_fail(self, **rakan):  # ACTION CODE = 1
        self._iterations += 1
        self.do('INSERT INTO history VALUES ({iteration}, 1, {precincts}, {alpha}, {beta}, {raw_pop}, {raw_comp}, {score});'.format(
            iteration=self.iterations,
            precincts=", ".join([str(_.district) for _ in rakan['precincts']]),
            alpha=rakan['ALPHA'],
            beta=rakan['BETA'],
            raw_pop=rakan['population_score'],
            raw_comp=rakan['compactness_score'],
            score=rakan['score'],
        ))

    def do_weight(self, **rakan):  # ACTION CODE = 2
        self.do('INSERT INTO history VALUES ({iteration}, 2, {precincts}, {alpha}, {beta}, {raw_pop}, {raw_comp}, {score});'.format(
            iteration=self.iterations,
            precincts=", ".join([str(_.district) for _ in rakan['precincts']]),
            alpha=rakan['ALPHA'],
            beta=rakan['BETA'],
            raw_pop=rakan['population_score'],
            raw_comp=rakan['compactness_score'],
            score=rakan['score'],
        ))

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    @property
    def iterations(self):
        return self._iterations

    # GRAPH EXPORTS

    def export_graph_chisquared(self):
        pass

    def export_graph_r_value(self):
        pass

    def export_graph_distribution(self):
        pass

    def export_graph_scores(self):
        pass

    def export_graph_alpha(self):
        pass

    def export_graph_beta(self):
        pass

    def export_graph_population_score(self):
        pass

    def export_graph_compactness_score(self):
        pass
