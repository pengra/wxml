#ifndef GRAPH_H
#define GRAPH_H
#include <list>
#include <vector>
#include <map>
#include <set>
#include <iostream>
#include <queue>
#include "dynamicboundary.h"

namespace rakan {
    // To be wrapped in Python with read only attributes
    struct Precinct {
    public:
        int rid;
        int district; // READ/WRITE ACCESS
        int population; // population of this precinct
        int area; // geographic area
        int democrat_votes; // democratic votes
        int republican_votes; // republican votes
        int other_votes; // other votes

        std::list<Precinct*> neighbors;

        Precinct() { }; // for python
        Precinct(int rid, int district);
        Precinct(int rid, int district, std::list<Precinct*> neighbors);
    };

    typedef std::vector<Precinct*> Atlas;
    typedef std::vector<std::list<int>> Districts;

    // To be wrapped in a Python API for mathematicians who know what they're doing.
    // I'm just a software engineer.
    class Rakan {
    private:
        bool __is_valid; // is the map valid?
    protected:
        Atlas _atlas; // atlas of the precincts, where index = rid
        DynamicBoundary _edges; // dynamic boundary helper
        Districts _districts; // track districts of each precinct

    public:    
        // For rapid state management (for communication with the server)
        std::list<int> _unchecked_changes; 
        std::list<int> _checked_changes;
    
        Rakan(); // for python
        Rakan(int size, int districts);
        ~Rakan(); // deconstruction

        // == API for debugging in python ==
        Districts districts();
        Atlas atlas();
        DynamicBoundary edges(); // need a python API I guess

        // == API for the mathematicains ==

        // Construction of Rakan
        int add_precinct(int district, int population); // add a precinct
        void set_neighbors(int rid1, int rid2); // set neighbors
        
        // Useful API for walking
        std::map<int, std::list<int>> get_neighbors(int rid); // given an rid, get a map of {districts: [rids]}
        std::map<int, std::list<int>> get_diff_district_neighbors(int rid); // given an rid, get a map of {different districts: [rids]} 
        // A dual breadth first serach to determine connectivity via the same district will not use the black_listed rid as part of path
        bool are_connected(int rid1, int rid2, int black_listed_rid); 
        bool is_valid(); // is the graph still valid?
        std::pair<int, int> propose_random_move(); // propose a random move in the form of rid, new district
        void move_precinct(int rid, int district); // move the specified rid to the new district

        // todo: scoring
        double population_score();
        double population_score(int rid, int district);
        double compactness_score();
        double compactness_score(int rid, int district);
        int democrat_seats();
        int democrat_seats(int rid, int district);
        int republican_seats();
        int republican_seats(int rid, int district);
        int other_seats();
        int other_setas(int rid, int district);

        /* MORE APIS TO ADD OVER TIME
            Grunularity (bulk move precincts)
            Statistical tests
            Profiler
            Multi-threading
        */


        // internal methods
        std::set<std::pair<int, int>> _checks_required(int rid); // a set of paris that need to be checked that require are_connected checks
        bool _is_valid();
        bool _is_legal_new_district(int rid, int district); // is it legal to attain this new district?
        bool _severs_neighbors(int rid); // check all the neighbors are still conected one way or another
        void _update_district_boundary(int rid, int district); // update the dynamic boundary
        void _update_atlas(int rid, int district); // update the atlas
        void _update_districts(int rid, int district); // update district map
    };
}

#endif // !GRAPH_H