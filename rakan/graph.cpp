#include "graph.h"
#include <stdio.h>

// Some syntatic that should be defined in production.h/development.h but stored here because I'm assuming we're always in development
#define ATLAS_RID_CHECK(RID)                                                \
    if (RID >= (int)this->_atlas.size() || RID < 0)                         \
    {                                                                       \
        throw std::invalid_argument("Invalid RID: " + std::to_string(RID)); \
    }
#define DISTRICT_CHECK(DISTRICT)                                                    \
    if (district >= (int)this->_districts.size() || district < 0)                   \
    {                                                                               \
        throw std::invalid_argument("Invalid District" + std::to_string(DISTRICT)); \
    }

namespace rakan
{
// Simple Precinct Struct Constructors.
Precinct::Precinct(int rid, int district)
    : rid(rid), district(district), area(0), democrat_votes(0), republican_votes(0), other_votes(0){};

Precinct::Precinct(int rid, int district, std::list<Precinct *> neighbors)
    : rid(rid), district(district), democrat_votes(0), republican_votes(0), other_votes(0), neighbors(neighbors){};

District::District()
    : population(0), area(0), democrat_votes(0), republican_votes(0), other_votes(0){};

Rakan::Rakan()
{
    // Data Structures:
    // Atlas is a vector of pointers to precincts
    // edges is the dynamicboundary object instance
    // districts is a vector of lists of integers
    this->_atlas = Atlas();
    this->_edges = DynamicBoundary();
    this->_districts = Districts();
    this->generator.seed(time(NULL));
}

// Rakan Class.
Rakan::Rakan(int size, int districts)
{
    // Vectors take size parameters.
    // same exact data structures
    this->_atlas = Atlas();
    this->_atlas.reserve(size);
    this->_edges = DynamicBoundary(size);
    this->_districts = Districts(districts);
    this->generator.seed(time(NULL));

    // Spawn Districts
    for (int i = 0; i < districts; i++)
    {
        this->_districts[i] = new District;
    }
};

// == API FOR DEBUGGING IN PYTHON ==

Districts Rakan::districts()
{
    return this->_districts;
}

Atlas Rakan::atlas()
{
    return this->_atlas;
}

DynamicBoundary Rakan::edges()
{
    return this->_edges;
}

// == API FOR CONSTRUCTION ==

// add a precinct with specified district
// Each precinct is assigned an rid that will be used to reference
// that precinct from now on. rids start at 0 and increment by one.
// the return value of this method is the rid.
int Rakan::add_precinct(int district, int population, int d_pop, int r_pop, int o_pop)
{
    DISTRICT_CHECK(district);
    if (population < 0)
    {
        throw std::invalid_argument("Population is negative");
    }
    else if (d_pop < 0)
    {
        throw std::invalid_argument("Democratic Population is negative");
    }
    else if (r_pop < 0)
    {
        throw std::invalid_argument("Republican Population is negative");
    }
    else if (o_pop < 0)
    {
        throw std::invalid_argument("Other Population is negative");
    }

    int new_rid = this->_atlas.size();

    // update atlas
    this->_atlas.push_back(new Precinct(new_rid, district));
    this->_atlas[new_rid]->population = population; // Not defined in constructor because there could be more attributes.
    this->_atlas[new_rid]->democrat_votes = d_pop;
    this->_atlas[new_rid]->republican_votes = r_pop;
    this->_atlas[new_rid]->other_votes = o_pop;

    // update dynamic boundary
    this->_edges.add_node(new_rid);

    // update district table
    this->_districts[district]->precincts.push_back(new_rid);
    this->_districts[district]->population += this->_atlas[new_rid]->population;
    this->_districts[district]->area += this->_atlas[new_rid]->area;
    this->_districts[district]->republican_votes += this->_atlas[new_rid]->republican_votes;
    this->_districts[district]->democrat_votes += this->_atlas[new_rid]->democrat_votes;
    this->_districts[district]->other_votes += this->_atlas[new_rid]->other_votes;

    // add to unchecked changes
    this->_unchecked_changes.push_back(new_rid);

    return new_rid;
}

Rakan::~Rakan()
{
    // destructor for the atlas
    for (Precinct *precinct : this->_atlas)
    {
        delete precinct;
    }
}

// set two precincts to be neighbors. Requires precincts to have been added to district.
// Note that it's not possible at this time to remove neighbors once they've been set.
void Rakan::set_neighbors(int rid1, int rid2)
{
    // get precincts in question
    ATLAS_RID_CHECK(rid1);
    ATLAS_RID_CHECK(rid2);

    Precinct *precinct1 = this->_atlas[rid1];
    Precinct *precinct2 = this->_atlas[rid2];

    // update atlas's neighbors property
    precinct1->neighbors.push_back(precinct2);
    precinct2->neighbors.push_back(precinct1);

    // update dynamic boundary, notes if the precincts are in the same district or not.
    this->_edges.add_edge(rid1, rid2, precinct1->district != precinct2->district);
    if (precinct1->district != precinct2->district)
    {
        this->_districts[precinct1->district]->border += 1;
        this->_districts[precinct2->district]->border += 1;
    }

    // add to _unchecked_changes. Only need to be done once. So check real quick.
    if (std::find(this->_unchecked_changes.begin(), this->_unchecked_changes.end(), rid1) == this->_unchecked_changes.end())
    {
        this->_unchecked_changes.push_back(rid1);
    }
}

// == API FOR NERDS ==

// get the neighbors of the given rid
// Returned as a map where {district: [rids], district: [rids], ..}
std::map<int, std::list<int>> Rakan::get_neighbors(int rid)
{
    ATLAS_RID_CHECK(rid);

    std::map<int, std::list<int>> neighbors;

    for (Precinct *neighbor : this->_atlas[rid]->neighbors)
    {
        // Return only the RID
        // Don't return the object because that's dangerous
        // Especially when interacting with them via Python
        neighbors[neighbor->district].push_back(neighbor->rid);
    }

    return neighbors;
}

// get the neighbors of different districts for the given rid
// Just calls get_neighbors but ignores the entries that are in the same
// district.
std::map<int, std::list<int>> Rakan::get_diff_district_neighbors(int rid)
{
    ATLAS_RID_CHECK(rid);

    std::map<int, std::list<int>> neighbors;
    int current_district = this->_atlas[rid]->district;

    for (Precinct *neighbor : this->_atlas[rid]->neighbors)
    {
        if (neighbor->district != current_district)
        {
            neighbors[neighbor->district].push_back(neighbor->rid);
        }
    }
    return neighbors;
}

// are the two precincts connected via the same district path?
// Will not use the black_listed_rid as part of path.
bool Rakan::are_connected(int rid1, int rid2, int black_listed_rid = -1, int kill_multiplier = 1)
{
    // This works by doing a double breadth first search
    ATLAS_RID_CHECK(rid1);
    ATLAS_RID_CHECK(rid2);

    if (this->_atlas[rid1]->district != this->_atlas[rid2]->district)
    {
        throw std::invalid_argument("Districts between selected precincts are different");
    }
    else if (rid1 == black_listed_rid || rid2 == black_listed_rid)
    {
        throw std::invalid_argument("Cannot blacklist the precinct that is undergoing the connectivitiy test");
    }

    // Begin by assuming the two precincts are not connected
    bool connected = false;

    // Get the district we must traverse through
    int district = this->_atlas[rid1]->district;

    // Build two pools. Each one stores the "seen" values of the BFT.
    // When these two pools intersect, we consider the two initial rids to be
    // connected.
    std::vector<bool> pool1 = std::vector<bool>(this->_atlas.size()); // items cursor1 has traversed
    std::vector<bool> pool2 = std::vector<bool>(this->_atlas.size()); // items cursor2 has traversed

    // Classic BFT but with 2 queues for both sides.
    std::list<int> rid1queue = std::list<int>{rid1};
    std::list<int> rid2queue = std::list<int>{rid2};
    int cursor1, cursor2;

    // Assume that if the script runs for more than the number of precincts
    // something went wrong and terminate.
    int auto_kill = this->_atlas.size() * kill_multiplier;

    // The traversals. While we haven't initiated the auto_kill and one queue has at least one item...
    while ((!rid1queue.empty() || !rid2queue.empty()) && auto_kill-- > 0)
    {
        // Check out the first queue.
        if (!rid1queue.empty())
        {
            // grab the first item of the queue.
            cursor1 = rid1queue.front();
            rid1queue.pop_front();

            // Skip this entire loop if the cursor is blacklisted
            if (cursor1 == black_listed_rid)
            {
                continue;
            }

            // If the other cursor has encountered this spot,
            // mark connected as true and break
            if (pool2[cursor1])
            {
                connected = true;
                break;
            }

            // Mark this value in the pool as a value we've seen
            pool1[cursor1] = true;

            // Iterate through the neighbors of this cursor and add them to the queue
            // Make sure they already aren't in the queue
            for (Precinct *neighbor : this->_atlas[cursor1]->neighbors)
            {
                if (neighbor->district == district && std::find(rid1queue.begin(), rid1queue.end(), neighbor->rid) == rid1queue.end())
                {
                    rid1queue.push_back(neighbor->rid);
                }
            }
        }

        // Same exact logic but with the second queue now.
        if (!rid2queue.empty())
        {
            cursor2 = rid2queue.front();
            rid2queue.pop_front();

            if (cursor2 == black_listed_rid)
            {
                continue;
            }

            if (pool1[cursor2])
            {
                connected = true;
                break;
            }

            pool2[cursor2] = true;

            for (Precinct *neighbor : this->_atlas[cursor2]->neighbors)
            {
                if (neighbor->district == district && std::find(rid2queue.begin(), rid2queue.end(), neighbor->rid) == rid2queue.end())
                {
                    rid2queue.push_back(neighbor->rid);
                }
            }
        }
    }

    return connected;
}

// is the graph still valid?
bool Rakan::is_valid()
{
    // Go through _unchecked_changes if it's not empty.
    if (!this->_unchecked_changes.empty())
        return this->_is_valid();
    return this->__is_valid;
}

// Propose a random move
// all edges involving two different districted precincts are equally likely to be proposed
// Move proposed as pair integers, where the first integer is the rid
// and the second integer is the district number to convert it to.
std::vector<int> Rakan::propose_random_move()
{
    // Get a random pair of districts that are adjacent but in different districts
    std::pair<int, int> random_rids = this->_edges.get_random_district_edge();
    // Get the district of the second value and propose to move the first precinct into that district.
    std::vector<int> result(3);
    result = {random_rids.first, this->_atlas[random_rids.first]->district, this->_atlas[random_rids.second]->district};
    return result;
}

// Check that the district isn't being deleted.
// Just check that there's at least one precinct in the distrct.
bool Rakan::_destroys_district(int rid)
{
    int district = this->_atlas[rid]->district;
    return this->_districts[district]->precincts.size() <= 1;
}

// move the specified rid to the new district
// if the move is illegal, exceptions will be thrown
void Rakan::move_precinct(int rid, int district)
{
    if (rid < 0 || rid >= (int)this->_atlas.size())
    {
        throw std::invalid_argument("Illegal Move (Reason: No such rid)");
    }
    else if (district < 0 || district >= (int)this->_districts.size())
    {
        throw std::invalid_argument("Invalid Move (Reason: No such district)");
    }
    else if (!this->is_valid())
    {
        throw std::logic_error("Cannot make move when graph is invalid");
    }
    else if (!this->_is_legal_new_district(rid, district))
    {
        throw std::invalid_argument("Illegal Move (Reason: No neighbors have this district)");
    }
    else if (this->_severs_neighbors(rid))
    {
        throw std::invalid_argument("Illegal Move (Reason: Severs the neighboring district(s))");
    }
    else if (this->_destroys_district(rid))
    {
        throw std::invalid_argument("Illegal Move (Reason: Eliminates a district)");
    }

    // update this->_districts
    this->_update_districts(rid, district);

    // update dynamic boundary
    this->_update_district_boundary(rid, district);

    // update atlas
    this->_update_atlas(rid, district);
}

// return a set of rid pairs that need are_connected checks given that the
// passed in rid is switching districts. Created by getting a list of neighbors,
// and returning a set of pairs of neighbors in the same district.
std::set<std::pair<int, int>> Rakan::_checks_required(int rid)
{
    int first, second;

    std::set<std::pair<int, int>> to_check;
    std::map<int, std::list<int>> pool = this->get_neighbors(rid);

    // Essentially, if a group of neighbors is as so: [1,2,3,4]
    // Return: [(1, 2), (1,3), (1, 4)]
    for (auto it = pool.begin(); it != pool.end(); ++it)
    {
        auto it2 = it->second.begin();
        first = *it2;
        for (it2++; it2 != it->second.end(); it2++)
        {
            second = *it2;
            to_check.insert(std::pair<int, int>(first, second));
        }
    }
    return to_check;
}

// perform checks if there are unchecked changes
// As of now, unchecked changes occur when adding precincts
bool Rakan::_is_valid()
{
    // keep popping items off of _unchecked_changes
    // run are_connected tests on all of its neighbors
    while (!this->_unchecked_changes.empty())
    {
        int rid = this->_unchecked_changes.front();
        std::set<std::pair<int, int>> pool = this->_checks_required(rid);
        for (std::pair<int, int> item : pool)
        {
            if (!this->are_connected(item.first, item.second, -1, 2))
            {
                // if the test failed, break immediately
                // Assume the user does some set_neighbor calls
                // So this test can be called again
                std::cout << "[CRakan] Check failed on " << item.first << " and " << item.second << std::endl;
                this->__is_valid = false;
                return false;
            }
            // Remove from unchecked.
        }
        this->_unchecked_changes.pop_front();
    }
    // Got through the whole list, everything checked out.
    this->__is_valid = true;
    return true;
}

// is it legal to attain this new district?
// Checks that at least one neighbor shares this district
bool Rakan::_is_legal_new_district(int rid, int district)
{
    Precinct precinct = *(this->_atlas[rid]);

    // If the precinct is in the district, of course the move is valid
    // Assuming all moves prior to this were valid and that the map
    // was valid at the start.
    if (precinct.district == district)
    {
        return true;
    }

    // Check all the neighbors, if one of them has the district
    // requested, return true.
    for (Precinct *neighbor : precinct.neighbors)
    {
        if (neighbor->district == district)
        {
            return true;
        }
    }

    // None of the neighbors has the district, which means the move
    // is invalid.
    return false;
}

// Check all the neighbors are still connected one way or another.
bool Rakan::_severs_neighbors(int rid)
{
    // Make sure we're not cutting off a district in half
    std::set<std::pair<int, int>> checks = this->_checks_required(rid);

    // Go through the checks and make sure they're all connected
    for (std::pair<int, int> item : checks)
    {
        // Run all the connection tests in different threads.
        auto future = std::async(&Rakan::are_connected, this, item.first, item.second, rid, 1);
        if (!future.get())
        {
            // If something becomes disconnected, it means a district got severed
            return true;
        }
    }
    // If all checks pass, no neighboring districts were severed
    return false;
}

// update the dynamic boundary tree
void Rakan::_update_district_boundary(int rid, int district)
{
    // In the dynamic boundary, update the fact that an rid is in a different district
    for (Precinct *neighbor : this->_atlas[rid]->neighbors)
    {
        // update boundary lengths for the districts
        int oldDistrict = this->_atlas[rid]->district;
        if (neighbor->district == district)
        {
            this->_districts[district]->border -= 1;
        }
        if (neighbor->district == oldDistrict)
        {
            this->_districts[oldDistrict]->border += 1;
        }

        // Only toggle the edge if the neighbor is in this rid's old district
        // or if the neighbor is in the rid's new district.
        if (neighbor->district == district || neighbor->district == oldDistrict)
        {
            this->_edges.toggle_edge(rid, neighbor->rid);
        }
    }
}

// update the atlas
void Rakan::_update_atlas(int rid, int district)
{
    // Simple district update on the graph
    this->_atlas[rid]->district = district;
}

// update district map
void Rakan::_update_districts(int rid, int district)
{
    int oldDistrict = this->_atlas[rid]->district;

    // update district population totals
    this->_districts[oldDistrict]->population -= this->_atlas[rid]->population;
    this->_districts[district]->population += this->_atlas[rid]->population;

    // update district areas (geographic?)
    this->_districts[oldDistrict]->area -= this->_atlas[rid]->area;
    this->_districts[district]->area += this->_atlas[rid]->area;

    // update voting data
    this->_districts[oldDistrict]->republican_votes -= this->_atlas[rid]->republican_votes;
    this->_districts[district]->republican_votes += this->_atlas[rid]->republican_votes;

    this->_districts[oldDistrict]->democrat_votes -= this->_atlas[rid]->democrat_votes;
    this->_districts[district]->democrat_votes += this->_atlas[rid]->democrat_votes;

    this->_districts[oldDistrict]->other_votes -= this->_atlas[rid]->other_votes;
    this->_districts[district]->other_votes += this->_atlas[rid]->other_votes;

    // Remove the rid from the district map and add it to the correct one
    this->_districts[oldDistrict]->precincts.remove(rid);
    this->_districts[district]->precincts.push_back(rid);
}

// Calculate the standard deviation of the populations
double Rakan::population_score()
{
    double mean = 0;
    double score = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        mean += this->_districts[i]->population;
    }
    mean /= this->_districts.size();
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        double diff = this->_districts[i]->population - mean;
        score += diff * diff;
    }
    score /= this->_districts.size() - 1;
    return score;
}

// Calculate the standard deviation of the population for a proposed move
double Rakan::population_score(int rid, int district)
{
    double mean = 0;
    double score = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        mean += this->_districts[i]->population;
    }
    mean /= this->_districts.size();
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        double diff = this->_districts[i]->population - mean;
        if (this->_atlas[rid]->district == i)
        {
            diff -= this->_atlas[rid]->population;
        }
        if (district == i)
        {
            diff += this->_atlas[rid]->population;
        }
        score += diff * diff;
    }
    score /= this->_districts.size() - 1;
    return score;
}

// Give the number of edges on the boundary of the districts
int Rakan::total_boundary_length()
{
    return this->_edges._d_edges;
}

// Give the number of edges on the boundary of the districts after a proposed move
int Rakan::total_boundary_length(int rid, int district)
{
    int score = this->_edges._d_edges;
    std::list<Precinct *>::iterator prcnct = this->_atlas[rid]->neighbors.begin();

    for (int i = 0; i < (int)this->_atlas[rid]->neighbors.size() - 1; i++)
    {
        int neighbor_rid = (*prcnct)->rid;
        if (this->_atlas[neighbor_rid]->district == district)
        {
            score -= 2;
        }
        if (this->_atlas[neighbor_rid]->district == this->_atlas[rid]->district)
        {
            score += 2;
        }
        std::advance(prcnct, 1);
    }
    int neighbor_rid = (*prcnct)->rid;
    if (this->_atlas[neighbor_rid]->district == district)
    {
        score -= 2;
    }
    if (this->_atlas[neighbor_rid]->district == this->_atlas[rid]->district)
    {
        score += 2;
    }
    return score;
}

double Rakan::compactness_score()
{
    double score = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        int len = _districts[i]->border;
        score += ((double)len * len) / _districts[i]->precincts.size();
    }
    return score;
}

double Rakan::compactness_score(int rid, int district)
{
    double score = 0;
    int oldDistrict = this->_atlas[rid]->district;
    int lens[this->_districts.size()];
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        lens[i] = this->_districts[i]->border;
    }
    for (Precinct *neighbor : this->_atlas[rid]->neighbors)
    {
        // update boundary lengths for the districts
        if (neighbor->district == district)
        {
            lens[district] -= 1;
        }
        if (neighbor->district == oldDistrict)
        {
            lens[oldDistrict] += 1;
        }
    }
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        int len = lens[i];
        score += ((double)len * len) / _districts[i]->precincts.size();
    }
    return score;
}

// Give the number of democratic seats in a simulated election
int Rakan::democrat_seats()
{
    int seats = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        int d_votes = this->_districts[i]->democrat_votes;
        int r_votes = this->_districts[i]->republican_votes;
        int o_votes = this->_districts[i]->other_votes;
        if (d_votes > r_votes && d_votes > o_votes)
        {
            seats += 1;
        }
    }
    return seats;
}

// Give the number of democratic seats in a simulated election
// after a proposed move
int Rakan::democrat_seats(int rid, int district)
{
    int seats = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        int d_votes = this->_districts[i]->democrat_votes;
        int r_votes = this->_districts[i]->republican_votes;
        int o_votes = this->_districts[i]->other_votes;
        if (this->_atlas[rid]->district == i)
        {
            d_votes -= this->_atlas[rid]->democrat_votes;
            r_votes -= this->_atlas[rid]->republican_votes;
            o_votes -= this->_atlas[rid]->other_votes;
        }
        if (district == i)
        {
            d_votes += this->_atlas[rid]->democrat_votes;
            r_votes += this->_atlas[rid]->republican_votes;
            o_votes += this->_atlas[rid]->other_votes;
        }
        if (d_votes > r_votes && d_votes > o_votes)
        {
            seats += 1;
        }
    }
    return seats;
}

// Give the number of republican seats in a simulated election
int Rakan::republican_seats()
{
    int seats = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        int d_votes = this->_districts[i]->democrat_votes;
        int r_votes = this->_districts[i]->republican_votes;
        int o_votes = this->_districts[i]->other_votes;
        if (r_votes > d_votes && r_votes > o_votes)
        {
            seats += 1;
        }
    }
    return seats;
}

// Give the number of republican seats in a simulated election
// after a proposed move
int Rakan::republican_seats(int rid, int district)
{
    int seats = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        int d_votes = this->_districts[i]->democrat_votes;
        int r_votes = this->_districts[i]->republican_votes;
        int o_votes = this->_districts[i]->other_votes;
        if (this->_atlas[rid]->district == i)
        {
            d_votes -= this->_atlas[rid]->democrat_votes;
            r_votes -= this->_atlas[rid]->republican_votes;
            o_votes -= this->_atlas[rid]->other_votes;
        }
        if (district == i)
        {
            d_votes += this->_atlas[rid]->democrat_votes;
            r_votes += this->_atlas[rid]->republican_votes;
            o_votes += this->_atlas[rid]->other_votes;
        }
        if (r_votes > d_votes && r_votes > o_votes)
        {
            seats += 1;
        }
    }
    return seats;
}

// Give the number of other seats in a simulated election
int Rakan::other_seats()
{
    int seats = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        int d_votes = this->_districts[i]->democrat_votes;
        int r_votes = this->_districts[i]->republican_votes;
        int o_votes = this->_districts[i]->other_votes;
        if (o_votes > r_votes && o_votes > d_votes)
        {
            seats += 1;
        }
    }
    return seats;
}

// Give the number of other seats in a simulated election
// after a proposed move
int Rakan::other_seats(int rid, int district)
{
    int seats = 0;
    for (int i = 0; i < (int)this->_districts.size(); i++)
    {
        int d_votes = this->_districts[i]->democrat_votes;
        int r_votes = this->_districts[i]->republican_votes;
        int o_votes = this->_districts[i]->other_votes;
        if (this->_atlas[rid]->district == i)
        {
            d_votes -= this->_atlas[rid]->democrat_votes;
            r_votes -= this->_atlas[rid]->republican_votes;
            o_votes -= this->_atlas[rid]->other_votes;
        }
        if (district == i)
        {
            d_votes += this->_atlas[rid]->democrat_votes;
            r_votes += this->_atlas[rid]->republican_votes;
            o_votes += this->_atlas[rid]->other_votes;
        }
        if (o_votes > d_votes && o_votes > r_votes)
        {
            seats += 1;
        }
    }
    return seats;
}

// A Metropolis Hastings Algorithm Step.
// Argument can be passed in.
// Arguments are completely arbritary and can be rewritten by the user.

// Example of a Python function hardened into C++
// Returns true when a change in the map has been made
bool Rakan::step()
{
    std::vector<int> move = this->propose_random_move();
    int rid = move.at(0);
    int new_district = move.at(2);
    try
    {
        // Sometimes propose_random_move severs districts, and move_precinct will catch that.
        if (this->distribution(this->generator) <= (this->score() / this->score(rid, new_district)))
        {
            this->move_precinct(rid, new_district);
            this->_last_move = std::vector<int>(move);
            this->iterations++;
            return true;
        }
        else
        {
            this->iterations++;
            return false;
        }
    }
    catch (std::exception e)
    {
        // Sometimes the proposed move severs the district
        // Just try again
        return this->step();
    }
}

// Score
double Rakan::score()
{
    return std::exp(
        (this->alpha * this->population_score()) +
        (this->beta * this->compactness_score()));
}

// Score of a proposed move.
double Rakan::score(int rid, int district)
{
    return std::exp(
        (this->alpha * this->population_score(rid, district)) +
        (this->beta * this->compactness_score(rid, district)));
}

} // namespace rakan
