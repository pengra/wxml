import sqlite3
from collections import deque
from threading import Thread
import time
from random_sequence_tests import chisquare_independence_test, r_value_independence_test
import matplotlib.pyplot as plt


class Xayah(object):

    def __init__(self, filename, threaded=True):
        if not filename.endswith('.xyh'):
            filename += '.xyh'
        self.filename = filename
        self.queue = deque()
        if threaded:
            Thread(target=self.worker).start()
        else:
            self._conn = sqlite3.connect(self.filename)
            self._cur = self._conn.cursor()
            try:
                self._iterations = self.select('count(*)')[0]
                self._moves = self.select('count(*)', where='action_=0')[0]
            except sqlite3.OperationalError:
                self._iterations = 0
                self._moves = 0

    def last(self):
        return self.select("*", iteration=self._iterations)[2:-6]

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
                print(args, kwargs)
                print(e)
                time.sleep(0.1)

    def seed(self, **rakan):
        self.queue.append(('do_seed', rakan))

    def select(self, columns, iteration=None, many=False, where='', range_=None):
        if isinstance(iteration, int):
            self._cur.execute('SELECT {columns} FROM history WHERE iteration={iteration} {where};'.format(
                columns=columns, iteration=iteration, where=where))
        where = 'WHERE ' + where if where else where
        self._cur.execute('SELECT {columns} FROM history {where};'.format(
            columns=columns, where=where))
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
        return self.select('precinct_{}'.format(precinct), iteration, many=(iteration is None))

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
            self._cur.execute(
                'CREATE TABLE history (iteration INTEGER, action_ INTEGER, {}, alpha REAL, beta REAL, raw_pop_score REAL, raw_comp_score REAL, score REAL, d_win INTEGER, r_win INTEGER, o_win INTEGER);'.format(precinct_table))
            self._conn.commit()
            self.do_move(**rakan)
            return False
        # sqlite3.DatabaseError as e: # which one? # table already exists exception.
        except sqlite3.OperationalError:
            self._iterations = self.select('count(*)')[0]
            self._moves = self.select('count(*)', where='action_=0')[0]
            return True

    def do_move(self, **rakan):  # ACTION CODE = 0
        self._iterations += 1
        self._moves += 1
        if rakan['score'] == 'inf':
            rakan['score'] = 'infinity'
        self.do('INSERT INTO history VALUES ({iteration}, 0, {precincts}, {alpha}, {beta}, {raw_pop}, {raw_comp}, {score}, {d_win}, {r_win}, {o_win});'.format(
            iteration=self.iterations,
            precincts=", ".join([str(_.district) for _ in rakan['precincts']]),
            alpha=rakan['ALPHA'],
            beta=rakan['BETA'],
            raw_pop=rakan['population_score'],
            raw_comp=rakan['compactness_score'],
            score=rakan['score'],
            d_win=rakan['d_win'],
            r_win=rakan['r_win'],
            o_win=rakan['o_win'],
        ))

    def do_fail(self, **rakan):  # ACTION CODE = 1
        self._iterations += 1
        self.do('INSERT INTO history VALUES ({iteration}, 1, {precincts}, {alpha}, {beta}, {raw_pop}, {raw_comp}, {score}, {d_win}, {r_win}, {o_win});'.format(
            iteration=self.iterations,
            precincts=", ".join([str(_.district) for _ in rakan['precincts']]),
            alpha=rakan['ALPHA'],
            beta=rakan['BETA'],
            raw_pop=rakan['population_score'],
            raw_comp=rakan['compactness_score'],
            score=rakan['score'],
            d_win=rakan['d_win'],
            r_win=rakan['r_win'],
            o_win=rakan['o_win'],
        ))

    def do_weight(self, **rakan):  # ACTION CODE = 2
        self.do('INSERT INTO history VALUES ({iteration}, 2, {precincts}, {alpha}, {beta}, {raw_pop}, {raw_comp}, {score}, {d_win}, {r_win}, {o_win});'.format(
            iteration=self.iterations,
            precincts=", ".join([str(_.district) for _ in rakan['precincts']]),
            alpha=rakan['ALPHA'],
            beta=rakan['BETA'],
            raw_pop=rakan['population_score'],
            raw_comp=rakan['compactness_score'],
            score=rakan['score'],
            d_win=rakan['d_win'],
            r_win=rakan['r_win'],
            o_win=rakan['o_win'],
        ))

    def __getitem__(self, key):
        pass

    def __setitem__(self, key, value):
        pass

    @property
    def iterations(self):
        return self._iterations

    # GRAPH EXPORTS

    """
    start = the index where to begin the test
    end = the index where to end the test
    step_start = the starting stepsize
    step_end = the ending stepsize
    """

    def export_graph_chisquared(self, start, end, step_start, step_end, points, rid1, rid2):
        if end == None:
            end = self.iterations - 1
        if step_end == None:
            step_end = end // 2

        step_size = (step_end - start) // points

        if (start < -1 or start >= end):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end >= self.iterations):
            raise ValueError("Invalid end value")

        precinct1_districts = self.get_district(rid1)
        precinct2_districts = self.get_district(rid2)

        x = list(range(step_start, step_end, step_size))
        values = [int(precinct1_districts[i] == precinct2_districts[i])
                  for i in range(start, end)]
        y = [chisquare_independence_test(values, i) for i in x]
        plt.plot(x, y)
        plt.savefig('chisquared.png')

    def export_graph_rvalue(self, start, end, step_start, step_end, points, rid1, rid2):
        if end == None:
            end = self.iterations - 1
        if step_end == None:
            step_end = end // 2

        step_size = (step_end - start) // points

        precinct1_districts = self.get_district(rid1)
        precinct2_districts = self.get_district(rid2)

        x = list(range(step_start, step_end, step_size))
        values = [int(precinct1_districts[i] == precinct2_districts[i])
                  for i in range(start, end)]
        y = [r_value_independence_test(values, i) for i in x]
        plt.plot(x, y)
        plt.savefig('rvalue.png')

    def export_graph_movement_2d(self, start, end, step):
        if end is None:
            end = self.iterations - 1
        
        precincts_count = len(self.last())
        precincts = self.select(", ".join(["precinct_{}".format(p) for p in range(precincts_count - 2)]), many=True, where="iteration BETWEEN {} AND {}".format(start, end))
        
        midway = precincts_count // 2
        
        reduced_dimension_x = []
        reduced_dimension_y = []

        for i in range(start, end, step):
            x = sum(precincts[i][:midway])
            y = sum(precincts[i][midway:])
            reduced_dimension_x.append(x)
            reduced_dimension_y.append(y)

        plt.scatter(reduced_dimension_x, reduced_dimension_y)
        plt.savefig('move2d.png')

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
    x = Xayah("save.xyh", threaded=False)
    # x.export_graph_chisquared(1, None, 100, None, 300, 82, 48)
    # x.export_graph_rvalue(1, None, 100, None, 300, 82, 48)
    x.export_graph_movement_2d(0, None, 10)
    # x.export_graph_chisquared(100, 101, 1, 82, 48)
