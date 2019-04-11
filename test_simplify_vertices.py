from rakan.base import Rakan
from other_tools.simplify_vertices import newGraph

newGraph("./dnx/WA.dnx")
r = Rakan()
r.read_nx("./dnx/holy.dnx")
r.report("something");
