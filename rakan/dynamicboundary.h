#ifndef DYNAMICBOUNDARY_H
#define DYNAMICBOUNDARY_H
#include <vector>
#include <list>
#include <algorithm>
#include <string>
#include <iostream>
#include <stdio.h>

namespace rakan {
    
    typedef std::pair<std::list<int>, std::list<int>> false_node;
    typedef std::vector<false_node> false_tree;

    class DynamicBoundary {
    public: // for python
        false_tree _tree;
        int _d_edges = 0;
        int _s_edges = 0;
        int _nodes = 0;
    public:
        // Constructing the tree
        DynamicBoundary();
        DynamicBoundary(int size);
        void add_node(int rid);
        void add_edge(int rid1, int rid2, bool diff); // add an edge

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