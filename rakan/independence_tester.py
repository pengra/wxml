import re
import json
import warnings
import numpy
import math
import networkx
import matplotlib.pyplot as plt
import csv;
from base import BaseRakan as TestRakan
from random_sequence_tests import chisquare_independence_test
from random_sequence_tests import r_value_independence_test
from decimal import Decimal

TOLERANCE = 0.1 # tolerance to determine whether the sequence was independent
RID1 = 18 # Chosen b/c they are in the middle of the IOWA map
RID2 = 82 # Chosen b/c they are in the middle of the IOWA map
PRINT = True # Boolean to print the stepsize and correlation value

def getZTestPathName(path_name):
    number = path_name.rsplit('/',1)[1];
    path_name = path_name.rsplit('/',1)[0] + "/all_graphs/chi_and_r_test_{}.png";
    path_name = path_name.format(number);
    return path_name;

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
    # array to sequence
    if path_name.endswith(".txt"):
        sequence = []
        file = open(path_name, 'r');
        for line in file:
            map = re.split('\[|\]|,| ', line)
            rid1_district = map[rid1]
            rid2_district = map[rid2]
            sequence.append(int(rid1_district == rid2_district))
        return sequence;


    # Create Rakan
    rakan = TestRakan(0, 0)
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
        final_result_report = [rakan.precinct_in_same_district(
            rid1, rid2)]+final_result_report
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
def indpendence_test_from_report_file(path_name, rid1, rid2, step_size, r_test_flag = True):
    sequence = get_sequence_from_file(path_name, rid1, rid2)
    try:
        if r_test_flag:
            v = r_value_independence_test(sequence, step_size);
            return v;
        else:
            v = chisquare_independence_test(sequence, step_size)
            return v
    except Exception as e:
        if PRINT: print(e)
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
    r_val_results = []
    chi_squared_results = []
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    sequence = get_sequence_from_file(path_name, rid1, rid2)
    min_step_r = 1
    min_r_val = 1
    max_step_chi = 1
    max_chi_val = 0
    # print(sequence)

    for i in range(1,round(len(sequence)/2)):
        # chi squared
        v = abs(chisquare_independence_test(sequence, i))
        chi_squared_results.append(v);
        if v > max_chi_val:
            max_step_chi = i
            max_chi_val = v

        # r value
        if numpy.cov(sequence) != 0:
            v = abs(r_value_independence_test(sequence, i))
            r_val_results.append(v);

            if v < min_r_val:
                min_step_r = i
                min_r_val = v
        else:
            r_val_results.append(numpy.nan);
            continue;

    if PRINT:
        # temporary
        if path_name.endswith(".txt"):
            path_name = path_name.replace(".txt", ".png")
        #path_name = getZTestPathName(path_name);

        plt.figure(1)
        plt.plot(r_val_results)
        plt.xlabel('Step Size (N)')
        plt.ylabel('Correlation')
        plt.title('R Value Test Results')
        #plt.savefig(path_name+'/r_value.png')

        plt.plot(chi_squared_results)
        plt.xlabel('Step Size (N)')
        plt.ylabel('Chi Squared Values')
        plt.title('Chi Squared Test Results')
        #plt.savefig(path_name+'/chi_test.png')
        plt.savefig(path_name);
        plt.close();
    return [min_step_r, max_step_chi]


'''
Description: This method determines whether the walk was independent or not
Input:
    - path_name: this is the path to the Rakan.report folder
Output:
    - True or False
'''


def test(report_folder_name, rid1=RID1, rid2=RID2):
    min_step = find_opt_stepsize(report_folder_name, rid1, rid2)
    r_val = indpendence_test_from_report_file(report_folder_name, rid1, rid2, min_step[0], True)
    chi_val = indpendence_test_from_report_file(report_folder_name, rid1, rid2, min_step[1], False)
    if r_val == -10: return False
    if PRINT:
        print("\nR   - Step Size: {}  Correlation: {}".format(min_step[0], r_val))
        print("Chi - Step Size: {}  P Value: {}".format(min_step[1], chi_val))
        '''
        with open(getZTestPathName(report_folder_name), 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerows(numpy.array([min_step, r_val, min_step[1], chi_val]))
        '''
    return r_val < TOLERANCE and chi_val < TOLERANCE

'''
Description: This method is separate from the entire project. It is used for
        converting multiple dnx files into array.txt files
Note: the dnx files must be in a specific file structure for this method to run
        appropriately
'''
def files_to_array(path_name, n):
    total = []
    for i in range(n):
        a = networkx.read_gpickle(path_name+"/{}/save.dnx".format(i))
        s = [a.node[i]['dis'] for i in range(99)]
        total.append(s)
    np_total = numpy.array(total)
    numpy.savetxt(fname=path_name+'/newPicksData.txt', X=np_total.astype(int), fmt = '%.0f')


'''
Description: This method is separate from the entire project. It is used for
        converting a json file into a array.txt file
Note: JSON file must be in the form specified by gis.pengra.io website
'''
def json_to_array(json_file_name):
    total = []
    jobject = json.load(open(json_file_name));
    for i in range(len(jobject['data'])):
        map_array = jobject['data'][i]['map']
        total.append(map_array)
    print(total)
    np_total = numpy.array(total)
    new_txt_file_name = json_file_name.replace(".json", ".txt")
    numpy.savetxt(fname=new_txt_file_name, X=np_total.astype(int), fmt = '%i')


'''
Description: This method is separate from the entire project. It is used for
        displaying stats about the input json file.
Note: JSON file must be in the form specified by gis.pengra.io website
'''
def json_to_stats(json_file_name):
    jobject = json.load(open(json_file_name))['data'];

    p = [jobject[i]['scores']['population'] for i in range(len(jobject))]
    c = [jobject[i]['scores']['compactness'] for i in range(len(jobject))]
    print("Pop.STD: {}\t Pop.Mean: {}\n Comp.STD: {}\t Comp.Mean: {}".format(numpy.std(p), numpy.mean(p), numpy.std(c), numpy.mean(c)))
