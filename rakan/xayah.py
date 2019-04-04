import pickle
from collections import deque
from threading import Thread
import time
import os
from random_sequence_tests import chisquare_independence_test, r_value_independence_test
import matplotlib.pyplot as plt

META_LENGTH = 10
ITERATION, ACTION, ALPHA, BETA, RAW_POP, RAW_COMP, SCORE, D_WIN, R_WIN, O_WIN = range(
    META_LENGTH)


class Xayah(object):

    def __init__(self, filename, threaded=True):
        if not filename.endswith('.xyh'):
            filename += '.xyh'
        self.filename = filename
        if os.path.isfile(filename):
            with open(filename, 'rb') as handle:
                payload = pickle.loads(handle.read())
        else:
            payload = {
                'events': deque(),
                'iterations': 0,
                'moves': 0
            }

        self._iterations = payload['iterations']
        self._moves = payload['moves']
        self._events = payload['events']

    def save(self):
        with open(self.filename, 'wb') as handle:
            handle.write(pickle.dumps({
                'events': self._events,
                'iterations': self._iterations,
                'moves': self._moves
            }))

    def last(self):
        try:
            return self._events[-1][META_LENGTH:]
        except IndexError:
            raise IndexError("Event list is empty")

    def select(self, columns, iterations=(-1,)):
        # ({iteration}, 0, {alpha}, {beta}, {raw_pop}, {raw_comp}, {score}, {d_win}, {r_win}, {o_win}, {precincts})
        for iteration in iterations:
            yield [self._events[iteration][col] for col in columns]

    def get_score(self, iterations=(-1, )):
        yield from self.select([SCORE], iterations)

    def get_alpha(self, iterations=(-1, )):
        yield from self.select([ALPHA], iterations)

    def get_beta(self, iterations=(-1, )):
        yield from self.select([BETA], iterations)

    def get_compactness(self, iterations=(-1, )):
        yield from self.select([RAW_COMP], iterations)

    def get_population(self, iterations=(-1, )):
        yield from self.select([RAW_POP], iterations)

    def get_district(self, precincts, iterations=(-1, )):
        for iteration in iterations:
            yield [self._events[iteration][precinct + META_LENGTH] for precinct in precincts]

    def seed(self, **rakan):
        self._events.append((
            self.iterations,
            -1,
            rakan['ALPHA'],
            rakan['BETA'],
            rakan['population_score'],
            rakan['compactness_score'],
            rakan['score'],
            rakan['d_win'],
            rakan['r_win'],
            rakan['o_win'],
            *[_.district for _ in rakan['precincts']]
        ))

    def move(self, **rakan):
        # ({iteration}, 0, {alpha}, {beta}, {raw_pop}, {raw_comp}, {score}, {d_win}, {r_win}, {o_win}, {precincts})
        self._iterations += 1
        self._moves += 1
        self._events.append((
            self.iterations,
            0,
            rakan['ALPHA'],
            rakan['BETA'],
            rakan['population_score'],
            rakan['compactness_score'],
            rakan['score'],
            rakan['d_win'],
            rakan['r_win'],
            rakan['o_win'],
            *[_.district for _ in rakan['precincts']]
        ))

    def fail(self, **rakan):
        self._iterations += 1
        self._moves += 1
        self._events.append((
            self.iterations,
            1,
            rakan['ALPHA'],
            rakan['BETA'],
            rakan['population_score'],
            rakan['compactness_score'],
            rakan['score'],
            rakan['d_win'],
            rakan['r_win'],
            rakan['o_win'],
            *[_.district for _ in rakan['precincts']]
        ))

    def weight(self, **rakan):
        self._events.append((
            self.iterations,
            2,
            rakan['ALPHA'],
            rakan['BETA'],
            rakan['population_score'],
            rakan['compactness_score'],
            rakan['score'],
            rakan['d_win'],
            rakan['r_win'],
            rakan['o_win'],
            *[_.district for _ in rakan['precincts']]
        ))

    def __getitem__(self, key):
        return self._events[key]

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

        districts = self.get_district([rid1, rid2])

        x = list(range(step_start, step_end, step_size))
        values = []
        for _ in range(start, end):
            try:
                a, b = next(districts)
            except StopIteration:
                break
            values.append(int(a == b))

        y = [chisquare_independence_test(values, i) for i in x]
        plt.plot(x, y)
        plt.savefig('chisquared.png')

    def export_graph_rvalue(self, start, end, step_start, step_end, points, rid1, rid2):

        confidence = 0.05

        if end == None:
            end = self.iterations - 1
        if step_end == None:
            step_end = end // 2

        step_size = (step_end - start) // points

        districts = self.get_district([rid1, rid2], range(self.iterations))

        x = list(range(step_start, step_end, step_size))
        values = []
        for _ in range(start, end):
            try:
                a, b = next(districts)
            except StopIteration:
                break
            values.append(int(a == b))

        y = [r_value_independence_test(values, i) for i in x]
        for index, value in enumerate(y):
            if value < confidence:
                print(index, x[index])
        plt.plot(x, y)
        plt.savefig('rvalue.png')

    def export_graph_movement_2d(self, start, end, step):
        if end is None:
            end = self.iterations - 1

        precincts_count = len(self.last())

        midway = precincts_count // 2

        reduced_dimension_x = []
        reduced_dimension_y = []

        for i in range(start, end, step):
            x = sum(self._events[i][META_LENGTH:midway])
            y = sum(self._events[i][midway + META_LENGTH:])
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
        if end is None:
            end = self.iterations - 1

        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        y = list(self.get_score(range(start, end, step)))
        plt.plot(x, y)
        plt.savefig('scores.png')

    def export_graph_alpha(self, start, end, step):
        if end is None:
            end = self.iterations - 1

        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        y = list(self.get_alpha(range(start, end, step)))
        plt.plot(x, y)
        plt.savefig('alpha.png')

    def export_graph_beta(self, start, end, step):
        if end is None:
            end = self.iterations - 1

        if (end < start):
            raise ValueError("End must come after Start")
        elif (start < -1 or start > self.iterations):
            raise ValueError("Invalid Start value")
        elif (end < -1 or end > self.iterations):
            raise ValueError("Invalid end value")
        elif (step < -1 or step > (end - start)):
            raise ValueError("Invalid step value")

        x = list(range(start, end, step))
        y = list(self.get_beta(range(start, end, step)))
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
    x = Xayah("save.xyh")
    # x.export_graph_chisquared(1, None, 100, None, 300, 82, 48)
    x.export_graph_rvalue(46620, None, 1, None, 1000, 82, 48)
    # params = (30000, None, 10)
    # x.export_graph_scores(*params)
    # x.export_graph_alpha(*params)
    # x.export_graph_movement_2d(0, None, 10)
    # x.export_graph_chisquared(100, 101, 1, 82, 48)
