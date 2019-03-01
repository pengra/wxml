import sqlite3
from collections import deque
from threading import Thread
import time
from random_sequence_tests import chisquare_independence_test, r_value_independence_test
import matplotlib.pyplot as plt

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
        success = False
        while not success:
            try:
                self._cur.execute(*args, **kwargs)
                self._conn.commit()
                success = True
            except (sqlite3.DatabaseError, sqlite3.OperationalError) as e:
                print(e)
                time.sleep(0.1)

    def seed(self, **rakan):
        self.queue.append(('do_seed', rakan))

    def select(self, columns, iteration=None, many=False, where=''):
        if isinstance(iteration, int):
            self._cur.execute('SELECT ({columns}) FROM history WHERE iteration={iteration} {where};'.format(columns=columns, iteration=iteration, where=where))
        where = ' WHERE ' + where if where else where
        self._cur.execute('SELECT ({columns}) FROM history{where};'.format(columns=columns, where=where))
        if many:
            return self._cur.fetchall()
        return self._cur.fetchone()
        
    def get_score(self, iteration=None):
        return self.select('score', iteration)

    def get_alpha(self, iteration=None):
        return self.select('alpha', iteration)

    def get_beta(self, iteration=None):
        return self.select('beta', iteration)

    def get_compactness(self, iteration=None):
        return self.select('raw_comp_score', iteration)

    def get_population(self, iteration=None):
        return self.select('raw_pop_score', iteration)

    def get_district(self, precinct, iteration=None):
        return self.select('precinct_{}'.format(precinct), iteration)

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
        try:
            self._cur.execute('CREATE TABLE history (iteration INTEGER, action_ INTEGER, {}, alpha REAL, beta REAL, raw_pop_score REAL, raw_comp_score REAL, score REAL);'.format(precinct_table))
            self._conn.commit()
            self.do_move(**rakan)
        except sqlite3.OperationalError: # sqlite3.DatabaseError as e: # which one? # table already exists exception.
            self._iterations = self.select('count(*)')[0]
            self._moves = self.select('count(*)', where='action_=0')[0]

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

    def export_graph_chisquared(self, start, end, step, rid1, rid2):
        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        values = [self.get_district(i, rid1) == self.get_district(i, rid2) for i in range(0, self.iterations)]
        y = [chisquare_independence_test(values, i) for i in x]
        plt.plot(x, y)
        plt.savefig('chisquared.png')

    def export_graph_rvalue(self, start, end, step, rid1, rid2):
        x = list(range(5, 100, 1))
        values = []
        for i in range(0, 1000): #self.iterations):
            print(i)
            values.append(int(self.get_district(i, rid1) == self.get_district(i, rid2)))
        # values = [self.get_district(i, rid1) == self.get_district(i, rid2) for i in range(0, self.iterations)]
        y = []
        print(x)
        print(values)
        for i in x:
            y.append(r_value_independence_test(values, i))
            print("y", i)
        # y = [r_value_independence_test(values, i) for i in x]
        plt.plot(x, y)
        plt.savefig('chisquared.png')
        
    def export_graph_distribution(self, start, end, step):
        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

    def export_graph_scores(self, start, end, step):
        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        y = [self.get_score(i) for i in x]
        plt.plot(x, y)
        plt.savefig('scores.png')

    def export_graph_alpha(self, start, end, step):
        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        y = [self.get_alpha(i) for i in x]
        plt.plot(x, y)
        plt.savefig('alpha.png')

    def export_graph_beta(self, start, end, step):
        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        y = [self.get_beta(i) for i in x]
        plt.plot(x, y)
        plt.savefig('beta.png')

    def export_graph_population_score(self, start, end, step):
        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        y = [self.get_population(i) for i in x]
        plt.plot(x, y)
        plt.savefig('pop.png')

    def export_graph_compactness_score(self, start, end, step):
        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        y = [self.get_compactness(i) for i in x]
        plt.plot(x, y)
        plt.savefig('comp.png')


if __name__ == "__main__":
    x =  Xayah("save.xyh")
    x.export_graph_rvalue(99, 101, 100, 82, 48)
    # x.export_graph_chisquared(100, 101, 1, 82, 48)
