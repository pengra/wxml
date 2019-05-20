import shapefile
import math
import matplotlib.pyplot as plt
from progress.bar import IncrementalBar

ROUND_M = 0.1 #digits
ROUND_B = 10 # digits

BOTH_LABEL = True
VIS_PRINT = False
IS_NEIGHBOR_PRINT = True

DEFAULT_VIS_FILE_NAME = './vis'
EDGES_OF_OHIO = [4149, 3165, 1824, 10215, 8498]
PROBLEMS = {
    50: [204, 205, 206, 207, 47, 40],
    58: [59, 204, 205, 206, 207, 200, 201, 202, 203, 64, 33, 47],
    61: [63, 62, 65, 47, 175],
    96: [91, 92, 93, 94, 95, 99, 100, 85],
    155: [158, 157, 199, 216, 198, 164],
    159: [158, 216],
    164: [158, 196, 157, 154, 155],
    179: [42, 45, 37, 176, 177, 178, 6023, 34, 6147],
    181: [70, 67, 62, 69, 6025, 85, 6154, 175, 6024, 6147, 105, 106, 107, 60],
    194: [187, 193, 195, 196, 191, 188],
    197: [167, 185, 189, 151, 134, 135, 136, 172, 168],
    224: [294, 245, 247, 229, 241, 223],
    226: [288, 286, 289, 7690, 284],
    231: [232, 283, 7703, 284, 279, 280],
    238: [291, 4293, 8018, 272, 273, 8017, 8014],
    249: [248, 251, 220, 250, 253, 1489, 1455],
    257: [222, 258, 293, 225],
    281: [279, 278, 276, 7235, 277, 7236, 7788, 7703],
    283: [284, 231, 289, 266, 7689],
    319: [317, 320, 313, 321, 309]
}


def create_adjacency_list(shape_file_name="../shp/ohio/precincts_results"):
    sf = read_shapefile(shape_file_name)
    summary = summarize_precincts_info(sf)

    print("starting...")
    measure_priority_depth(sf, summary)
    #b = is_neighbor(sf, 50, 40)
    #print(b)
    #visualize_multiple(sf, [58, 69])
    #n = get_neighbors(sf, summary, 58)
    #print(n)
    #visualize_single(sf, 96)
    #visualize_multiple(sf, [181, 6024])
    #test(sf, summary)

    '''
    target = len(sf)
    bar = IncrementalBar("finding neighbors for each precinct...".format(target), max=target)
    for i in range(117,target):
        if len(get(sf, i)) == 0:
            bar.next()
            continue
        n = get_neighbors(sf, summary, i)
        visualize_multiple(sf, [i]+n)
        bar.next()
    '''
    print('done')

def get_close_precincts(sf, summary, id):
    # create a queue of precincts to check
    precinct_dict = {}
    for i in summary.keys():
        if i == id:
            continue
        distance = dist(summary[id], summary[i])
        if distance not in precinct_dict:
            precinct_dict[distance] = []
        precinct_dict[distance].append(i)

    # convert the dictionary into an array
    precinct_queue = []
    for k in sorted(precinct_dict.keys()):
        precinct_queue = precinct_queue + precinct_dict[k]
    return precinct_queue

def measure_priority_depth(sf, summary):
    for i in PROBLEMS.keys():
        queue = get_close_precincts(sf, summary, i)
        precinct_list = PROBLEMS[i]
        result = 0
        for p in precinct_list:
            val = queue.index(p)
            if val > result:
                result = val
        print(i, " : ", result)


def test(sf, summary):
    print("testing...")
    for i in PROBLEMS.keys():
        n = get_neighbors(sf, summary, i)
        b = set(n) - set(PROBLEMS[i])
        c = set(PROBLEMS[i]) - set(n)

        if len(b) == 0 and len(c) == 0:
            print("{}:".format(i))
        else:
            m = "{}: ".format(i)
            if len(b) != 0:
                m += " EXTRA: {}".format(b)
            if len(c) != 0:
                m += " MISSING: {}".format(c)
            print(m)

        #visualize_multiple(sf, [i]+n)

def summarize_precincts_info(sf):
    result = {}
    #limits = [math.inf, -math.inf, math.inf, -math.inf]
    for i in range(len(sf)):
        x = 0
        y = 0
        points = get(sf, i)
        if len(points) == 0:
            continue
        for p in points:
            #limits = [min(limits[0], p[0]), max(limits[1], p[0]), min(limits[2], p[1]), max(limits[3], p[1])]
            x += p[0]
            y += p[1]
        x /= len(points)
        y /= len(points)
        result[i] = (x,y)
    return result

def get_neighbors(sf, summary, id):
    total_points_in_id = len(get(sf, id))
    neighbors = []

    # create a queue of precincts to check
    precinct_dict = {}
    for i in summary.keys():
        if i == id:
            continue
        distance = dist(summary[id], summary[i])
        if distance not in precinct_dict:
            precinct_dict[distance] = []
        precinct_dict[distance].append(i)

    # convert the dictionary into an array
    precinct_queue = []
    for k in sorted(precinct_dict.keys()):
        precinct_queue = precinct_queue + precinct_dict[k]

    # find the neighbors
    stale_precinct_count = 0
    for precinct in precinct_queue:
        if get(sf, id) != get(sf, precinct) and is_neighbor(sf, id, precinct):
            neighbors.append(precinct)
            stale_precinct_count = 0
            #print(precinct, ": ADDED")
        else:
            stale_precinct_count += 1
            #print(precinct, ":")
        if stale_precinct_count >= 100:
            break
    return neighbors

def is_neighbor(sf, id1, id2):
    id1_points = get(sf, id1)
    id1_edges = sorted(list(map(lambda i: (min(id1_points[i], id1_points[i + 1]), max(id1_points[i], id1_points[i + 1])), range(len(id1_points) - 1))))
    len_id1 = len(id1_edges)

    id2_points = get(sf, id2)
    id2_edges = sorted(list(map(lambda i: (min(id2_points[i], id2_points[i + 1]), max(id2_points[i], id2_points[i + 1])), range(len(id2_points) - 1))))
    len_id2 = len(id2_edges)

    all_points = sorted(list(map(lambda i: (id1_points[i][0], id1_points[i][1], i, 1), range(len(id1_points))))\
                + list(map(lambda i: (id2_points[i][0], id2_points[i][1], i, 2), range(len(id2_points)))))



    active_edge_1 = set()
    active_edge_2 = set()
    for p in all_points:
        x, y, index, family = p
        if family == 1:
            q = id1_points[(index - 1) % len(id1_points)]
            r = id1_points[(index + 1) % len(id1_points)]
            edge1 = (min((x,y), q), max((x,y), q))
            edge2 = (min((x,y), r), max((x,y), r))
            active_edges.add(edge1)
            active_edges.add(edge2)
        else:
            q = id2_points[index - 1]

    return False
    #return len(shared_edges) > 0

def read_shapefile(file_name):
    print("reading shapefile...")
    return shapefile.Reader(file_name).shapes()

def visualize_single(shapefile_obj, id):
    if VIS_PRINT:
        print("visualizing precinct " + str(id) + "...")
    points = get(shapefile_obj, id)
    x,y = convert_tuples_to_two_arrays(points)
    fig = plt.figure(figsize=(40, 40))
    plt.plot(x, y, 'C3', lw=3)
    plt.scatter(x, y, s=120)
    create_labels(plt, x, y)
    plt.tight_layout()
    plt.axis('off')
    plt.savefig(DEFAULT_VIS_FILE_NAME + "_" + str(id) + ".png")
    plt.close()

def visualize_multiple(sf, ids):
    if VIS_PRINT:
        print("visualizing precincts "+ str(ids) + "...")
    limits = [math.inf, -math.inf]
    plt.figure(figsize=(40, 40))
    for id in ids:
        points = get(sf, id)
        x,y = convert_tuples_to_two_arrays(points)
        limits = [min(min(x), limits[0]), max(max(y), limits[1])]
        if ids.index(id) == 0:
            plt.plot(x, y, 'C3', lw=2)
            plt.scatter(x, y, s=15)
            create_labels(plt, x, y)
        else:
            plt.plot(x, y, 'C3', lw=1)
            plt.scatter(x, y, s=10)
            if BOTH_LABEL:
                create_labels(plt, x, y)

    plt.tight_layout()
    plt.axis('off')
    vis_name = DEFAULT_VIS_FILE_NAME + "_" + str(ids).replace("[","").replace("]","").replace(" ","").replace(",","_") + ".png"
    vis_name = vis_name[:255] # file name cannot be longer than 255 characters
    plt.savefig(vis_name)
    plt.close()

def create_labels(figure, x, y):
    # assume that x and y have the same length
    for i in range(len(x)):
        figure.annotate(str(i), xy=(x[i],y[i]))

def dist(p, q):
    return math.sqrt(math.pow(p[0]-q[0], 2)+math.pow(p[1]-q[1],2))

def get(shapefile_obj, id):
    return shapefile_obj[id].points

def find_vector(p, q):
    if p == q:
        return (-math.inf, -math.inf), math.inf
    mag = math.sqrt((q[0] - p[0])**2 + (q[1] - p[1])**2)
    v = ((q[0] - p[0]) / mag, (q[1] - p[1]) / mag)
    if v[0] < 0:
        v = (-1 * v[0], -1 * v[1])
    return (custom_round(v[0], 100), custom_round(v[1], 100))

def magnitude(edge):
    point1, point2 = edge
    return math.sqrt(math.pow(point1[0] - point2[0], 2) + math.pow(point1[1] - point2[1],2))

def collinear(p1, p2, p3):
    if abs((p3[1] - p2[1])*(p2[0] - p1[0]) - (p2[1] - p1[1])*(p3[0] - p2[0])) < 2000:
        return True
    else:
        return False

def overlap(edge1, edge2):
    if edge1 == edge2:
        return True
    x = sorted([tuple(sorted([edge1[0][0], edge1[1][0]])), tuple(sorted([edge2[0][0], edge2[1][0]]))])
    y = sorted([tuple(sorted([edge1[0][1], edge1[1][1]])), tuple(sorted([edge2[0][1], edge2[1][1]]))])

    if IS_NEIGHBOR_PRINT:
        print("x: ", x)
        print("y: ", y)
        print("OVERLAP: ", (x[0][1] > x[1][0]), (y[0][1] > y[1][0]))

    return x[0][1] > x[1][0] and y[0][1] > y[1][0]

def collinear_edge(edge1, edge2):
    THRESH = 0.01
    v1 = (edge1[0][0] - edge1[1][0], edge1[0][1] - edge1[1][1])
    v2 = (edge2[0][0] - edge2[1][0], edge2[0][1] - edge2[1][1])

    if IS_NEIGHBOR_PRINT:
        print("COLLINEAR: ", abs(v1[0] * v2[1] - v1[1] * v2[0]))
    if abs(v1[0] * v2[1] - v1[1] * v2[0]) < THRESH:
        return True
    else:
        return False

def find_slope_and_intercept(p, q):
    if p == q:
        return -1000, -1000
    m = custom_round((q[1] - p[1])/(q[0] - p[0]), ROUND_M) if q[0] != p[0] else math.inf
    b = custom_round(p[1] - p[0] * (q[1] - p[1])/(q[0] - p[0]), ROUND_B) if q[0] != p[0] else q[0]
    return m, b

def custom_round(x, round_num):
    if x == math.inf:
        return math.inf
    return round(round_num * x) / round_num

def convert_tuples_to_two_arrays(points):
    x = []
    y = []
    for p in points:
        x.append(p[0])
        y.append(p[1])
    return x,y

'''

def get_total_shared_edges_and_points(sf, id1, id2):
    # relatively quick function. Don't need to print status update
    id1_points_array = get(sf, id1)
    id2_points_array = get(sf, id2)
    first = set(map(lambda p: (custom_round(p[0]), custom_round(p[1])), id1_points_array))
    second = set(map(lambda p: (custom_round(p[0]), custom_round(p[1])), id2_points_array))
    shared_points = first.intersection(second)

    # find the indicies of the shared edges
    shared_point_index_in_first = [-1]*len(shared_points)
    for i in range(len(id1_points_array)-1, -1, -1):
        t = (custom_round(id1_points_array[i][0]), custom_round(id1_points_array[i][1]))
        if t in shared_points:
            shared_point_index_in_first[list(shared_points).index(t)] = i
    shared_point_index_in_second = [-1]*len(shared_points)
    for i in range(len(id2_points_array)-1, -1, -1):
        t = (custom_round(id2_points_array[i][0]), custom_round(id2_points_array[i][1]))
        if t in shared_points:
            shared_point_index_in_second[list(shared_points).index(t)] = i
    edges = set()

    for i in range(len(shared_points)):
        j = shared_point_index_in_first[i]
        k = shared_point_index_in_second[i]
        j_less = find_far_enough_vertex(id1_points_array, j, -1)
        j_more = find_far_enough_vertex(id1_points_array, j, 1)
        k_less = find_far_enough_vertex(id2_points_array, k, -1)
        k_more = find_far_enough_vertex(id2_points_array, k, 1)
        j_first_slope = (id1_points_array[j_less][1] - id1_points_array[j][1])/abs(id1_points_array[j_less][0] - id1_points_array[j][0])
        j_second_slope = (id1_points_array[j_more][1] - id1_points_array[j][1])/abs(id1_points_array[j_more][0] - id1_points_array[j][0])
        k_first_slope = (id2_points_array[k_less][1] - id2_points_array[k][1])/abs(id2_points_array[k_less][0] - id2_points_array[k][0])
        k_second_slope = (id2_points_array[k_more][1] - id2_points_array[k][1])/abs(id2_points_array[k_more][0] - id2_points_array[k][0])
        if (abs(j_first_slope - k_first_slope) < 20 and j_first_slope * k_first_slope > 0)\
            or (abs(j_first_slope - k_second_slope) < 20 and j_first_slope * k_second_slope > 0):
            edges.add((min(j_less, j), max(j_less, j)))
            print(j_less, j, j_first_slope)
            print(k, k_more, k_second_slope)
        elif (abs(j_second_slope - k_first_slope) < 20 and j_second_slope * k_first_slope > 0)\
            or (abs(j_second_slope - k_second_slope) < 20  and j_second_slope * k_second_slope > 0):
            edges.add((min(j_more, j), max(j_more, j)))

            #print(abs(j_second_slope - k_first_slope) < 20)
            #print(j_second_slope * k_first_slope > 0)
            #print(abs(j_second_slope - k_second_slope) < 20)
            #print(j_second_slope * k_second_slope > 0)
            #print("HERE ARE THE POINTS THAT ARE SHARED: {}".format(shared_point_index_in_first))


        #print(abs(j_first_slope - k_first_slope))
        #print(abs(j_first_slope - k_second_slope))
        #print(abs(j_second_slope - k_first_slope))
        #print(abs(j_second_slope - k_second_slope))
        #print("{}: main\t\t{}\t- {}\t- {}\tdy: {}".format(i, j, j_first_slope, j_less, (id1_points_array[j_less][1] - id1_points_array[j][1]) > 0))
        #print("{}: main\t\t{}\t- {}\t- {}\tdy: {}".format(i, j, j_second_slope, j_more, (id1_points_array[j_more][1] - id1_points_array[j][1]) > 0))
        #print("{}: other\t{}\t- {}\t- {}\tdy: {}".format(i, k, k_first_slope, k_less, (id2_points_array[k_less][1] - id2_points_array[k][1]) > 0))
        #print("{}: other\t{}\t- {}\t- {}\tdy: {}".format(i, k, k_second_slope, k_more, (id2_points_array[k_more][1] - id2_points_array[k][1]) > 0))

    #print("Edges: {}".format(edges))
    return edges, shared_points


def is_neighbor(sf, id1, id2):
    id1_points = get(sf, id1)
    id2_points = get(sf, id2)

    SHIT = 0.01
    first = set(map(lambda p: (custom_round(p[0], SHIT), custom_round(p[1], SHIT)), id1_points))
    second = set(map(lambda p: (custom_round(p[0], SHIT), custom_round(p[1], SHIT)), id2_points))
    shared_points = first.intersection(second)

    # find the indicies of the shared edges
    p_list = []
    for i in range(len(id1_points)-1, -1, -1):
        t = (custom_round(id1_points[i][0], SHIT), custom_round(id1_points[i][1], SHIT))
        if t in shared_points:
            index = list(shared_points).index(t)
            p_list.append(i)

    for i in p_list:
        p = id1_points[i]
        p_next = id1_points[(i+1) % len(id1_points)]
        v = find_vector(p, p_next)
        n = set()
        for j in range(len(id2_points)):
            q = id2_points[j]

            #if i == 1797:
            #    p1 = p
            #    p2 = p_next
            #    p3 = q
            #    print(i, j, round(((p3[1] - p2[1])*(p2[0] - p1[0]) - (p2[1] - p1[1])*(p3[0] - p2[0]))))

            if collinear(p, p_next, q)\
                and q[0] > min(p[0], p_next[0]) and q[0] < max(p[0], p_next[0])\
                and q[1] > min(p[1], p_next[1]) and q[1] < max(p[1], p_next[1]):
                n.add(j)

        #if len(n) > 0:
        #    print(i, n)

        for j in n:
            q_less = id2_points[( j - 1 ) % len(id2_points)]
            q_more = id2_points[( j + 1 ) % len(id2_points)]
            if collinear(p, p_next, q_less) or collinear(p, p_next, q_more):
                return True

            #else:
            #    print(i, v, j, v_less, v_more)
    return False


def is_neighbor(sf, id1, id2):
    id1_points = get(sf, id1)
    id1_edges = sorted(list(map(lambda i: (min(id1_points[i], id1_points[i + 1]), max(id1_points[i], id1_points[i + 1])), range(len(id1_points) - 1))), key=lambda edge: (edge[0][0], magnitude(edge)))
    len_id1 = len(id1_edges)

    id2_points = get(sf, id2)
    id2_edges = sorted(list(map(lambda i: (min(id2_points[i], id2_points[i + 1]), max(id2_points[i], id2_points[i + 1])), range(len(id2_points) - 1))), key=lambda edge: (edge[0][0], magnitude(edge)))
    len_id2 = len(id2_edges)

    i = 0
    j = 0
    #shared_edges = []
    while i < len_id1 and j < len_id2:
        e = id1_edges[i]
        f = id2_edges[j]
        if IS_NEIGHBOR_PRINT:
            a = min(id1_points.index(e[0]), id1_points.index(e[1]))
            b = min(id2_points.index(f[0]), id2_points.index(f[1]))
            print("==========================================================================")
            print("INDEX: ", a, b)
        if  collinear_edge(e, f) and overlap(e, f):
                #print(a, b)
                return True
                #shared_edges.append((min(id1_points.index(e[0]), id1_points.index(e[1])), min(id2_points.index(f[0]), id2_points.index(f[1]))))

        if e[1][0] < f[1][0]:
            i += 1
        else:
            j += 1
    return False
    #return len(shared_edges) > 0

'''

create_adjacency_list()
