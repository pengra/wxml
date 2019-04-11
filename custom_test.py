from rakan.base import Rakan
from other_tools.simplify_vertices import newGraph

newGraph("WA.dnx")
r = Rakan()
r.read_nx("holy.dnx")
r.report("something");
