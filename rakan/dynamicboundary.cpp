#include "dynamicboundary.h"

#define TREE_RID_CHECK(RID) if (RID >= (int)this->_tree.size() || RID < 0) { throw std::invalid_argument("Invalid RID: " + std::to_string(RID)); }

// Simple dynamic boundary via just marking edges

namespace rakan {
    
    // Build a false tree
    DynamicBoundary::DynamicBoundary(int size) {
        this->_tree = false_tree(size);
    }

    // Build a false tree with default size
    // Javastyle'd defaults because I'm bad at coding
    DynamicBoundary::DynamicBoundary() {
        this->_tree = false_tree();
    }

    // add a node to the tree (no edges are added in this step)
    void DynamicBoundary::add_node(int rid) {
        // In python:
        // self._tree[rid] = [[diff district neighbors], [same district neighbors]]
        TREE_RID_CHECK(rid);
        this->_tree[rid] = false_node();
        this->_nodes++;
    }

    // add an edge to the tree (two directional)
    // both rids must already be added to the tree via add_node
    void DynamicBoundary::add_edge(int rid1, int rid2, bool diff) {
        TREE_RID_CHECK(rid1);
        TREE_RID_CHECK(rid2);

        // Check that the edge hasn't already been added.
        // This operation is expensive, but since it's occurring in the construction
        // and not in the walk, it only needs to occur once.
        if (std::find(this->_tree[rid1].first.begin(), this->_tree[rid1].first.end(), rid2) != this->_tree[rid1].first.end()) {
            throw std::invalid_argument("Cannot add the same edge twice.");
        } else if (std::find(this->_tree[rid1].second.begin(), this->_tree[rid1].second.end(), rid2) != this->_tree[rid1].second.end()) {
            throw std::invalid_argument("Cannot add the same edge twice.");
        }

        if (diff) { // create an edge of two precincts in different districts
            this->_d_edges += 2; // because two edges are established
            this->_tree[rid1].first.push_back(rid2);
            this->_tree[rid2].first.push_back(rid1);
        } else { // create an edge of two precincts in the same district
            this->_s_edges += 2; // because two edges are established
            this->_tree[rid1].second.push_back(rid2);
            this->_tree[rid2].second.push_back(rid1);
        }

    }

    // return a pair of rids of two neighboring precincts that are
    // are in two different districts
    std::pair<int, int> DynamicBoundary::get_random_district_edge() {
        // In C++ 0%0 does not throw an exception, need to check ahead of time
        if (this->_d_edges <= 0) {
            throw std::logic_error("No district edges to select from");
        }
        // Grab a random edge, where each edge has equal probability of being
        // selected.
        return this->get_district_edge(rand() % this->_d_edges);
    }

    // return the nth different district edge of this tree
    std::pair<int, int> DynamicBoundary::get_district_edge(int index) {
        // If the overall structure is [([0,1], [2,3]), ([4,5,6], [7])]
        // Then _d_edges will be 5 and the return values are as follows:
        // get_district_edge(0) -> 0
        // get_district_edge(1) -> 1
        // get_district_edge(2) -> 4
        // get_district_edge(3) -> 5
        // get_district_edge(4) -> 6
        // get_district_edge(5) -> out_of_range exception

        if (index >= this->_d_edges || index < 0) {
            throw std::out_of_range("invalid index: " + std::to_string(index));
        }

        // Overall logic: iterate through the pairs
        // get the length of the first item in the pairs
        // decrement index by that length
        // Repeat until the length > index and return the index
        // of the first item of that pair.
        
        int rid = 0;
        while (index >= (int)this->_tree[rid].first.size()) {
            // decrement index
            index -= this->_tree[rid].first.size();
            // increment rid
            rid++;
        }

        // We've reached a list n where the length of n > index
        std::list<int>::iterator it = this->_tree[rid].first.begin();
        // Advance index units in the list
        std::advance(it, index);
        // return (rid, item at index)
        return std::pair<int, int>(rid, *it);
    }

    // Toggles how the edges are marked in the dynamic boundary
    // If the two two nodes are marked as different-district precincts, they're marked as same-district precincts after this operation
    // Similarly, two nodes are marked as different-district precincts if they were originally different-district precincts.
    void DynamicBoundary::toggle_edge(int rid1, int rid2) {
        // Must use pointers because otherwise you're not modifying the right thing.
        false_node * node = &this->_tree[rid1];
        false_node * node2 = &this->_tree[rid2];

        // both are iterators        
        auto node_first_pos = std::find(node->first.begin(), node->first.end(), rid2);
        auto node_second_pos = std::find(node->second.begin(), node->second.end(), rid2);

        if (node_first_pos != node->first.end()) {
            // is rid2 in rid1's different district neighbor list? yes.
            node->first.erase(node_first_pos);
            node->second.push_back(rid2);
            node2->first.remove(rid1);
            node2->second.push_back(rid1);
            this->_d_edges -= 2;
            this->_s_edges += 2;
        
        } else if (node_second_pos != node->second.end()) {
            // is rid2 in rid1's same district neighbor list? yes.
            node->second.erase(node_second_pos);
            node->first.push_back(rid2);
            node2->second.remove(rid1);
            node2->first.push_back(rid1);
            this->_s_edges -= 2;
            this->_d_edges += 2;
        } else {
            // desired edge dne
            throw std::invalid_argument("Unable to find desired edge");
        }
    }

    // returns the number of edges
    int DynamicBoundary::edge_count() {
        // syntatic sugar for adding up the edges
        return this->_d_edges + this->_s_edges;
    }

    // returns the number of nodes
    int DynamicBoundary::node_count() {
        // syntatic sugar for counting nodes
        // kinda pointless because they're public anyways.
        return this->_nodes;
    }
}

