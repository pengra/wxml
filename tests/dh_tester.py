import os
import sys
sys.path.append("..") # Adds higher directory to python modules path.

from other_tools import dnx_handler as dh

json_obj = dh.dnx_to_JSON("../dnx/iowa.dnx");
dh.JSON_to_dnx(json_obj, "../dnx/shit.dnx")
os.system("python3 '../rakan' '../dnx/shit.dnx'")
