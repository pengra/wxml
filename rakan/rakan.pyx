# distutils: language = c++
from cython.operator import dereference, preincrement, address

from libcpp.list cimport list as clist
from libcpp.vector cimport vector as cvector

from rakan.rakan cimport Precinct as cPrecinct
from rakan.rakan cimport District as cDistrict
from rakan.rakan cimport Rakan as cRakan



cdef class PyPrecinct:

    cdef cPrecinct __cprecinct

    def __cinit__(self, int rid=0, int district=0):
        self._reset(rid, district)

    def _reset(self, int rid, int district):
        self.__cprecinct = cPrecinct(rid, district)

    #def __dealloc__(self):
    #    del self.__cprecinct

    def __eq__(self, other):
        return other.rid == self.rid

    def __str__(self):
        return "<Rakan Precinct rid={} district={}>".format(self.__cprecinct.rid, self.__cprecinct.district)

    @property
    def population(self):
        return self.__cprecinct.population

    @property
    def rid(self):
        return self.__cprecinct.rid;

    @property
    def district(self):
        return self.__cprecinct.district;

    @district.setter
    def district(self, int value):
        self.__cprecinct.district = value

    @property
    def area(self):
        return self.__cprecinct.area

    @property
    def democrat_votes(self):
        return self.__cprecinct.democrat_votes

    @property
    def republican_votes(self):
        return self.__cprecinct.republican_votes

    @property
    def other_votes(self):
        return self.__cprecinct.other_votes

    @property
    def neighbors(self):
        return [PyPrecinct.factory(dereference(_)) for _ in self.__cprecinct.neighbors]

    @staticmethod
    cdef factory(cPrecinct cprecinct):
        py_obj = PyPrecinct.__new__(PyPrecinct)
        (<PyPrecinct>py_obj).__cprecinct = cprecinct
        return py_obj



cdef class PyDistrict:

    cdef cDistrict __cdistrict

    def __cinit__(self):
        self.__cdistrict = cDistrict()

    def __len__(self):
        return self.__cdistrict.precincts.size()

    @property
    def population(self):
        return self.__cdistrict.population

    @property
    def area(self):
        return self.__cdistrict.area

    @property
    def democrat_votes(self):
        return self.__cdistrict.democrat_votes

    @property
    def republican_votes(self):
        return self.__cdistrict.republican_votes

    @property
    def other_votes(self):
        return self.__cdistrict.other_votes

    @staticmethod
    cdef factory(cDistrict cdistrict):
        py_obj = PyDistrict.__new__(PyDistrict)
        (<PyDistrict>py_obj).__cdistrict = cdistrict
        return py_obj



cdef class PyRakan:

    cdef cRakan __crakan

    def __init__(self, size = 10000, districts = 100):
        self._reset(size, districts)

    def __cinit__(self, int size = 10000, int districts = 100):
        self._reset(size, districts)

    def _reset(self, int size, int districts):
        self.__crakan = cRakan(size, districts)

    def __dealloc__(self):
        pass

    # == API for debugging in python ==

    def __str__(self) -> str:
        return "<Rakan nodes={} @ {}>".format(self.__len__(), id(self))

    def __len__(self) -> int:
        return self.__crakan.atlas().size()

    @property
    def districts(self) -> list:
        districts = self.__crakan.districts()
        return districts

    @property
    def precincts(self) -> list:
        c_precincts = self.__crakan.atlas()
        py_precincts = [PyPrecinct.factory(dereference(_)) for _ in c_precincts]
        return py_precincts

    def district_of(self, precinct) -> int:
        return self.__crakan.atlas()[precinct].district

    @property
    def districts(self) -> list:
        c_districts = self.__crakan.districts()
        py_districts = [PyDistrict.factory(dereference(_)) for _ in c_districts]
        return py_districts

    @property
    def edges(self) -> list:
        edges = self.__crakan.edges()
        return edges._tree

    # == API for myself ==

    @property
    def _unchecked_changes(self) -> list:
        return self.__crakan._unchecked_changes

    @property
    def _checked_changes(self) -> list:
        return self.__crakan._checked_changes

    @property
    def _last_move(self) -> list:
        return self.__crakan._last_move

    # == API for construction ==

    def add_precinct(self,
        int district,
        int population = 0,
        int d_pop = 0,
        int r_pop = 0,
        int o_pop = 0,
    ) -> int:
        return self.__crakan.add_precinct(district, population, d_pop, r_pop, o_pop)

    def set_neighbors(self, int rid1, int rid2):
        return self.__crakan.set_neighbors(rid1, rid2)

    # == API for the mathematicians ==

    def get_neighbors(self, int rid) -> dict:
        return self.__crakan.get_neighbors(rid)

    def get_diff_district_neighbors(self, int rid) -> dict:
        return self.__crakan.get_diff_district_neighbors(rid)

    def are_connected(self, int rid1, int rid2, int black_listed_rid = -1) -> bool:
        return self.__crakan.are_connected(rid1, rid2, black_listed_rid)

    def is_valid(self) -> bool:
        return self.__crakan.is_valid()

    def propose_random_move(self) -> list:
        return self.__crakan.propose_random_move()

    def move_precinct(self, int rid, int district):
        return self.__crakan.move_precinct(rid, district)

    def population_score(self, rid=None, district=None) -> float:
        if rid is None and district is None:
            return self.__crakan.population_score()
        else:
            return self.__crakan.population_score(rid, district)

    def total_boundary_length(self, rid=None, district=None) -> int:
        if rid is None and district is None:
            return self.__crakan.total_boundary_length()
        else:
            return self.__crakan.total_boundary_length(rid, district)

    def compactness_score(self, rid=None, district=None) -> int:
        if rid is None and district is None:
            return self.__crakan.compactness_score()
        else:
            return self.__crakan.compactness_score(rid, district)

    def democrat_seats(self, rid=None, district=None) -> int:
        if rid is None and district is None:
            return self.__crakan.democrat_seats()
        else:
            return self.__crakan.democrat_seats(rid, district)
    def democrat_proportion(self, district):
        return self.__crakan.democrat_proportion(district)
    def republican_seats(self, rid=None, district=None) -> int:
        if rid is None and district is None:
            return self.__crakan.republican_seats()
        else:
            return self.__crakan.republican_seats(rid, district)
    def republican_proportion(self, district):
        return self.__crakan.republican_proportion(district)
    def other_seats(self, rid=None, district=None) -> int:
        if rid is None and district is None:
            return self.__crakan.other_seats()
        else:
            return self.__crakan.other_seats(rid, district)
    def other_proportion(self, district):
        return self.__crakan.other_proportion(district)
    def score(self, rid=None, district=None) -> float:
        if rid is None and district is None:
            return self.__crakan.score()
        else:
            return self.__crakan.score(rid, district)

    # == Stepping ==

    def step(self):
        return self.__crakan.step()

    # == Statistics + Weights ==

    @property
    def _iterations(self):
        return self.__crakan.iterations

    @_iterations.setter
    def _iterations(self, int value):
        self.__crakan.iterations = value

    @property
    def iterations(self):
        return self._iterations

    @property
    def _ALPHA(self):
        return self.__crakan.alpha

    @property
    def _BETA(self):
        return self.__crakan.beta

    @_ALPHA.setter
    def _ALPHA(self, double value):
        self.__crakan.alpha = value

    @_BETA.setter
    def _BETA(self, double value):
        self.__crakan.beta = value
