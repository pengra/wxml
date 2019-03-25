# Project Rakan

A simple Python API for some redistricting code.

## Compiling + Running

After modifying the `__main__.py` file to how you see fit, run `./run`.

## File Formats

`file.dnx` = nodes have districts assigned to them
`file.snx` = nodes do not have districts assigned to them, just a map of the state's precincts.

## Building a State

Modify the `__main__.py` file to how you see fit. The standards for `networkx` "dnx"/"rnx" files are defined as below:

Note the `networkx` file must contain the following properties:

- meta properties:
    - Include _all_ census precincts, including bodies of water and non-precincts.
    - Nodes are referenced by integer (starting from 0)
    - Super precinct nodes only need the `is_super`, `super_layer` and `children` property.
- node properties:
    - `pop` (integer value) the population of the node.
    - `dis` (integer value) the district number this node is part of (indexed from 0). Use `-1` if no district assigned.
    - `name` (string value) human friendly name of this node.
    - `vertexes` (list of pairs of floats) A list of the coordinates that describe the geographic shape of this node.
    - `super_level` (integer) Describes what super precinct layer this is. You can have super precincts of super precincts. The larger this number is, the larger the super_precinct is. This number does not describe the number of children in this super precinct. The value `0` should be used for non super precincts.
    - `is_super` (boolean) Describes if this node is a super precinct. May not exist.
    - `children` (list of integers) If this precinct is a super precinct, notate which nodes are part of this super precinct by `rid`.
    - (more to come as the project matures)
- graph properties:
    - `fips` (integer value) the FIPS code of the state represented (e.g. 53)
    - `code` (2 digit string) the 2 digit code of the state (e.g. WA)
    - `state` (string) the full state name (e.g. Washington)
    - `districts` (integer) the number of districts in this graph. Use `-1` if no districts assigned (`.dnx` files should always have districts).
    - `is_super` (integer value) describes whether this networkx file contains super precincts. Super precincts should be stored in the same graph, but should not be connected to the non-super precincts in any way. All nodes that are super precincts must be marked with the `is_super` property. If 0, then there are no super layers.
    - `iterations` (integer value) describes the number of iterations this graph has gone through. Assumes value is 0 if not present.
    - `move_history` (list of dictionaries) describes the move history of the saved file.

## Todo:

- Harden scoring and step to c++
- Set a "burn in" process
- Spawn a thread that `requests.post` the map
    - Runtime statistics too
- Algorithm Scoring:
    - 15/20/25 node network
    - 2/3 districts