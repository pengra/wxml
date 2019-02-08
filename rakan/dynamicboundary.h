#ifndef DYNAMICBOUNDARY_H
#define DYNAMICBOUNDARY_H
#include <vector>
#include <list>
#include <algorithm>
#include <string>
#include <iostream>
#include <stdio.h>
#include <time.h>

namespace rakan {
    
    typedef std::pair<std::list<int>, std::list<int>> false_node;
    typedef std::vector<false_node> false_tree;

    class DynamicBoundary {
    public: // usually should be private, but made public for python
        false_tree _tree;
        int _d_edges = 0; // the number of edges between precincts in different districts
        int _s_edges = 0; // the number of edges between precincts in the same district
        int _nodes = 0; // the number of nodes
    public:
        // Constructing the tree
        DynamicBoundary();
        DynamicBoundary(int size); // Size being the number of nodes
        void add_node(int rid); // add a node
        void add_edge(int rid1, int rid2, bool diff); // add an edge, diff being true if they're in different districts

        // walk methods that might be used
        std::pair<int, int> get_random_district_edge(); // return a pair of rids
        std::pair<int, int> get_district_edge(int index); // return the nth edge
        void toggle_edge(int rid1, int rid2); // toggle a district between district border and non district border

        // other useful APIs
        int edge_count(); // returns the number of edges
        int node_count(); // returns the number of nodes
    };
}

#endif // !DYNAMICBOUNDARY_H