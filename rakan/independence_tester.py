import json
import warnings
import numpy
import matplotlib.pyplot as plt
from base import BaseRakan as TestRakan
from random_sequence_tests import r_value_independence_test
from decimal import Decimal

TOLERANCE = 0.1 # tolerance to determine whether the sequence was independent
RID1 = 82 # Chosen b/c they are in the middle of the IOWA map
RID2 = 48 # Chosen b/c they are in the middle of the IOWA map
PRINT = True # Boolean to print the stepsize and correlation value

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
    rakan = TestRakan(0,0)
    rakan.read_nx(path_name+"/save.dnx")
    moves = json.load(open(path_name+"/moves.json"))

    final_result_report = [rakan.precinct_in_same_district(rid1, rid2)]
    # iterate through all moves (Going backwards)
    for i in range(len(moves) - 1, 1, -1):
        move_obj = moves[i]
        if move_obj[0] == "fail" or move_obj[0] == "weight":
            continue
        precinct_id, old_district_id, new_district_id = moves[i][-1]
        rakan.move_precinct(precinct_id, old_district_id)
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
    try:
        v = r_value_independence_test(sequence, step_size)
        return v
    except Exception as e:
        if PRINT: print(e.message())
        return -10 # Invalid input exception

'''
Description: This method finds the ideal step_size for the given sequence
Input:
    - path_name: this is the path that map.geojson and moves.json should be located
    - rid1: the ID of the first precinct to be used in the test
    - rid2: the ID of the second precinct to be used in the test
Output:
    - the step_size with the least correlation value
Note:
    - when the PRINT bool is True, it creates a graph
    - it tries all the possible stepsizes. Could be optimized further
'''
def find_opt_stepsize(path_name, rid1, rid2):
    step_to_corr = []
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    sequence = get_sequence_from_file(path_name, rid1, rid2)
    min_step = 1
    min_r_val = 1
    print(sequence)
    for i in range(1,len(sequence) - 1):
        v = 1
        try:
            v = abs(r_value_independence_test(sequence, i))
            print("{} : {}".format(i, v))
        except Exception:
            # skip this map/ sampling if r_value_independence fails
            continue

        step_to_corr.append(v);

        if v < min_r_val:
            min_step = i
            min_r_val = v
    if PRINT:
        plt.plot(step_to_corr)
        plt.xlabel('Step Size (N)')
        plt.ylabel('Correlation')
        plt.title('Correlation Between N Steps Removed Independence Test Results')
        plt.savefig(path_name+'/step_size_to_corr.png')
    return min_step

'''
Description: This method determines whether the walk was independent or not
Input:
    - path_name: this is the path to the Rakan.report folder
Output:
    - True or False
'''
def test(report_folder_name, rid1=RID1, rid2=RID2):
    min_step = find_opt_stepsize(report_folder_name, rid1, rid2)
    cor = indpendence_test_from_report_file(report_folder_name, rid1, rid2, min_step)
    if cor == -10: return False
    if PRINT: print("Step Size: {}  Correlation: {}".format(min_step, cor))
    return cor < TOLERANCE
