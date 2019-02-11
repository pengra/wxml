import json
import warnings
import numpy
from base import BaseRakan
from random_sequence_tests import r_value_independence_test
from decimal import Decimal

TOLERANCE = 0.1 # tolerance to determine whether the sequence was independent
RID1 = 82 # Chosen b/c they are in the middle of the IOWA map
RID2 = 48 # Chosen b/c they are in the middle of the IOWA map
PRINT = False # Boolean to print the stepsize and correlation value

class Rakan(BaseRakan):
    """
    A statistical test to check two specified precincts are in the same district
    """
    def precinct_in_same_district(self, rid1, rid2):
        return self.precincts[rid1].district == self.precincts[rid2].district


'''
Description: This method creates the sequence from the walk specified by 'path_name'
Input:
    - path_name: this is the path that map.geojson and moves.json should be located
    - rid1: the ID of the first precinct to be used in the test
    - rid2: the ID of the second precinct to be used in the test
Output:
    - sequence of 0's and 1's
'''
def get_sequence_from_file(path_name, rid1, rid2):
    final_result_report = []

    # Create Rakan
    rakan = Rakan(0,0)
    rakan.read_nx(path_name+"/save.dnx")
    moves = json.load(open(path_name+"/moves.json"))

    final_result_report = [rakan.precinct_in_same_district(rid1, rid2)]
    # iterate through all moves (Going backwards)
    for i in range(len(moves) - 1, 0, -1):
        move_obj = moves[i]
        precinct_id, new_district_id = move_obj['prev']
        rakan.move_precinct(precinct_id, new_district_id)
        final_result_report = [rakan.precinct_in_same_district(rid1, rid2)]+final_result_report;
    return final_result_report

'''
Description: This method tests the independence of the walk given report path_name
Input:
    - path_name: this is the path that map.geojson and moves.json should be located
    - rid1: the ID of the first precinct to be used in the test
    - rid2: the ID of the second precinct to be used in the test
    - step_size: step_size to be used in the test
Output:
    - the correlation value of the sequence
'''
def indpendence_test_from_report_file(path_name, rid1, rid2, step_size):
    sequence = get_sequence_from_file(path_name, rid1, rid2)
    return r_value_independence_test(sequence, step_size)

'''
Description: This method finds the ideal step_size for the given sequence
Input:
    - path_name: this is the path that map.geojson and moves.json should be located
    - rid1: the ID of the first precinct to be used in the test
    - rid2: the ID of the second precinct to be used in the test
Output:
    - the step_size with the least correlation value
'''
def find_opt_stepsize(path_name, rid1, rid2):
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    sequence = get_sequence_from_file(path_name, rid1, rid2)
    min_step = 1
    min_r_val = 1
    for i in range(1,len(sequence) - 1):
        v = 1
        try:
            v = abs(r_value_independence_test(sequence, i))
        except Exception:
            # skip this map/ sampling if r_value_independence fails
            continue

        if v < min_r_val:
            min_step = i
            min_r_val = v
    return min_step


'''
Description: This method determines whether the walk was independent or not
Input:
    - path_name: this is the path to the Rakan.report folder
Output:
    - True or False
'''
def test(report_folder_name):
    min_step = find_opt_stepsize(report_folder_name, RID1, RID2)
    cor = indpendence_test_from_report_file("../hello", RID1, RID2, min_step)
    if PRINT: print("Step Size: {}  Correlation: {}".format(min_step, v))
    return cor < TOLERANCE

print(test("../hello"))
