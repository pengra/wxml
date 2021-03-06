#ifndef GRAPH_H
#define GRAPH_H
#include <list>
#include <vector>
#include <map>
#include <set>
#include <iostream>
#include <queue>
#include <thread>
#include <future>
#include <math.h>
#include <random>
#include <time.h>

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

	struct District{
	public:
		int population;
		int area;
		int democrat_votes;
		int republican_votes;
		int other_votes;
		int border=0;

		std::list<int> precincts;
		District();

	};


    typedef std::vector<District*> Districts;
	typedef std::vector<Precinct*> Atlas;

    // To be wrapped in a Python API for mathematicians who know what they're doing.
    // I'm just a software engineer.
    class Rakan {
    private:
        bool __is_valid; // is the map valid?
    protected:
        Atlas _atlas; // atlas of the precincts, where index = rid
        DynamicBoundary _edges; // dynamic boundary helper
        Districts _districts; // track districts of each precinct

        // record the last move


        // Tools for random distribution
        std::uniform_real_distribution<double> distribution = std::uniform_real_distribution<double>(0.0, 1.0);
        std::default_random_engine generator;

    public:
        // for tracking last move
        std::vector<int> _last_move = std::vector<int>(3);

        // For rapid state management (for communication with the server)
        std::list<int> _unchecked_changes;
        std::list<int> _checked_changes;

        // Weights
        double alpha = 0; // population weight
        double beta = 0; // compactness weight
        unsigned long int iterations = 0; // iterations so far

        Rakan(); // for python
        Rakan(int size, int districts);
        ~Rakan(); // deconstruction

        // == API for debugging in python ==
        Districts districts();
        Atlas atlas();
        DynamicBoundary edges(); // need a python API I guess

        // == API for the mathematicains ==

        // Construction of Rakan
        int add_precinct(int district, int population, int d_pop, int r_pop, int o_pop); // add a precinct
        void set_neighbors(int rid1, int rid2); // set neighbors

        // Useful API for walking
        std::map<int, std::list<int>> get_neighbors(int rid); // given an rid, get a map of {districts: [rids]}
        std::map<int, std::list<int>> get_diff_district_neighbors(int rid); // given an rid, get a map of {different districts: [rids]}
        // A dual breadth first serach to determine connectivity via the same district will not use the black_listed rid as part of path
        bool are_connected(int rid1, int rid2, int black_listed_rid, int kill_multiplier);
        bool is_valid(); // is the graph still valid?
        std::vector<int> propose_random_move(); // propose a random move in the form of rid, new district
        void move_precinct(int rid, int district); // move the specified rid to the new district

        // scoring
        double population_score();
        double population_score(int rid, int district);
        int total_boundary_length();
        int total_boundary_length(int rid, int district);
		double compactness_score();
        double compactness_score(int rid, int district);
        int democrat_seats();
		double democrat_proportion(int district);
        int democrat_seats(int rid, int district);
        int republican_seats();
		double republican_proportion(int district);
        int republican_seats(int rid, int district);
        int other_seats();
		double other_proportion(int district);
        int other_seats(int rid, int district);

        // internal methods
        std::set<std::pair<int, int>> _checks_required(int rid); // a set of paris that need to be checked that require are_connected checks
        bool _is_valid();
        bool _is_legal_new_district(int rid, int district); // is it legal to attain this new district?
        bool _severs_neighbors(int rid); // check all the neighbors are still conected one way or another
        bool _destroys_district(int rid); // check that a district isn't being removed from the map.
        void _update_district_boundary(int rid, int district); // update the dynamic boundary
        void _update_atlas(int rid, int district); // update the atlas
        void _update_districts(int rid, int district); // update district map

        // Hardened Step/Scoring Algorithms
        bool step();
        double score();
        double score(int rid, int district);
    };
}

#endif // !GRAPH_H
