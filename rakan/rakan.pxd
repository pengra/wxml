from libcpp.set cimport set as cset
from libcpp.map cimport map as cmap
from libcpp cimport bool as cbool
from libcpp.list cimport list as clist
from libcpp.vector cimport vector as cvector
from libcpp.pair cimport pair as cpair

cdef extern from "dynamicboundary.cpp": pass
cdef extern from "graph.cpp": pass

cdef extern from "dynamicboundary.h" namespace "rakan": 
    # THIS IS FOR DEBUGGING ONLY.
    # DO NOT USE UNLESS IF YOU KNOW WHAT YOU'RE DOING
    cdef cppclass DynamicBoundary: 
        cvector[cpair[clist[int], clist[int]]] _tree
        cpair[int, int] get_district_edge(int index) except +;
        int _d_edges;
        int _s_edges;
        int _nodes;
        
        # Construction
        void add_node(int) except +;
        void add_edge(int, int, bool) except +;

        cpair[int, int] get_random_district_edge() except +;
        cpair[int, int] get_district_edge(int) except +;
        void toggle_edge(int, int) except +;

        int edge_count() except +;
        int node_count() except +;

cdef extern from "graph.h" namespace "rakan":
    cdef cppclass Precinct:
        Precinct() except +
        Precinct(int, int) except +
        Precinct(int, int, list[Precinct*]) except +
        int rid
        int district
        int population
        int area
        int democrat_votes
        int republican_votes
        int other_votes
        clist[Precinct*] neighbors
        
    cdef cppclass Rakan:
        Rakan() except +
        Rakan(int size, int district) except +

        # == API for debugging in python ==
        cvector[clist[int]] districts()
        cvector[Precinct*] atlas()
        DynamicBoundary edges()

        # == API for myself ==
        clist[int] _unchecked_changes
        clist[int] _checked_changes

        # == API for the mathematicains ==

        # Construction of Rakan
        int add_precinct(int district, int population) except +
        void set_neighbors(int rid1, int rid2) except +
        
        # Useful API for walking
        cmap[int, clist[int]] get_neighbors(int rid) except + # given an rid, get a map of {districts: [rids]}
        cmap[int, clist[int]] get_diff_district_neighbors(int rid) except + # given an rid, get a map of {different districts: [rids]} 
        cbool are_connected(int rid1, int rid2, int black_listed_rid) except + # A dual breadth first serach to determine connectivity via the same district will not use the black_listed rid as part of path
        cbool is_valid() except + # is the graph still valid?
        cpair[int, int] propose_random_move() except + # propose a random move in the form of rid, new district
        void move_precinct(int rid, int district) except + # move the specified rid to the new district

        # scoring
        double population_score() except +
        double population_score(int rid, int district) except +
        double compactness_score() except +
        double compactness_score(int rid, int district) except +
        int democrat_seats() except +
        int democrat_seats(int rid, int district) except +
        int republican_seats() except +
        int republican_seats(int rid, int district) except +
        int other_seats() except +
        int other_setas(int rid, int district) except +

        # internal methods
        cset[cpair[int, int]] _checks_required(int rid) except + # a set of paris that need to be checked that require are_connected checks
        cbool _is_valid() except +
        cbool _is_legal_new_district(int rid, int district) except + # is it legal to attain this new district?
        cbool _severs_neighbors(int rid) except + # check all the neighbors are still conected one way or another
        void _update_district_boundary(int rid, int district) except + # update the dynamic boundary
        void _update_atlas(int rid, int district) except + # update the atlas
        void _update_districts(int rid, int district) except + # update district map