#include "tests.h"

using namespace std;
using namespace rakan;

typedef pair<int, int> a_move;

TEST_CASE("Santiy Dynamic Boundary", "[sanity]") {
    
    DynamicBoundary boundary = DynamicBoundary(1);
    
    SECTION("Initialization") {
        REQUIRE(boundary.node_count() == 0);
        REQUIRE(boundary.edge_count() == 0);
    }

    SECTION("More nodes than allowed") {
        boundary.add_node(0);
        REQUIRE_THROWS(boundary.add_node(1));
    }

    SECTION("Creating an with nodes that DNE") {
        REQUIRE_THROWS(boundary.add_edge(0, 1, true));
        REQUIRE_THROWS(boundary.add_edge(0, 1, false));
    }

    SECTION("Disallow adding the same edge twice") {
        boundary = DynamicBoundary(2);
        boundary.add_node(0);
        boundary.add_node(1);
        boundary.add_edge(0, 1, false);
        REQUIRE_THROWS(boundary.add_edge(0, 1, false));
        REQUIRE_THROWS(boundary.add_edge(0, 1, true));
    }
}

TEST_CASE("District Boundary Retrieval", "[bound]") {

    DynamicBoundary boundary = DynamicBoundary(10);
    for (int i = 0; i < 10; i++) {
        boundary.add_node(i);
    }

    boundary.add_edge(2, 5, true);
    boundary.add_edge(2, 3, false);
    boundary.add_edge(4, 9, false);
    boundary.add_edge(4, 5, false);
    boundary.add_edge(5, 9, false);
    boundary.add_edge(1, 6, false);
    boundary.add_edge(7, 8, false);
    boundary.add_edge(7, 0, false);
    boundary.add_edge(1, 5, true);
    boundary.add_edge(6, 5, true);
    boundary.add_edge(8, 9, true);
    boundary.add_edge(8, 5, true);
    boundary.add_edge(6, 7, true);
    boundary.add_edge(2, 1, true);
    boundary.add_edge(3, 4, true);
    boundary.add_edge(0, 6, true);
    boundary.add_edge(0, 1, true);
    
    SECTION("District Boundaries") {
        REQUIRE(boundary._d_edges == (10 * 2));
        REQUIRE_THROWS(boundary.get_district_edge(-1));
        REQUIRE(boundary.get_district_edge(0) == a_move(0, 6));
        REQUIRE(boundary.get_district_edge(1) == a_move(0, 1));
        REQUIRE(boundary.get_district_edge(2) == a_move(1, 5));
        REQUIRE(boundary.get_district_edge(3) == a_move(1, 2));
        REQUIRE(boundary.get_district_edge(4) == a_move(1, 0));
        REQUIRE(boundary.get_district_edge(5) == a_move(2, 5));
        REQUIRE(boundary.get_district_edge(6) == a_move(2, 1));
        REQUIRE(boundary.get_district_edge(7) == a_move(3, 4));
        REQUIRE(boundary.get_district_edge(8) == a_move(4, 3));
        REQUIRE(boundary.get_district_edge(9) == a_move(5, 2));
        REQUIRE(boundary.get_district_edge(10) == a_move(5, 1));
        REQUIRE(boundary.get_district_edge(11) == a_move(5, 6));
        REQUIRE(boundary.get_district_edge(12) == a_move(5, 8));
        REQUIRE(boundary.get_district_edge(13) == a_move(6, 5));
        REQUIRE(boundary.get_district_edge(14) == a_move(6, 7));
        REQUIRE(boundary.get_district_edge(15) == a_move(6, 0));
        REQUIRE(boundary.get_district_edge(16) == a_move(7, 6));
        REQUIRE(boundary.get_district_edge(17) == a_move(8, 9));
        REQUIRE(boundary.get_district_edge(18) == a_move(8, 5));
        REQUIRE(boundary.get_district_edge(19) == a_move(9, 8));
        REQUIRE_THROWS(boundary.get_district_edge(20));
    }
}

