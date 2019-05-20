import sys
import math
import shapefile
from progress.bar import IncrementalBar
from django.contrib.gis.gdal import DataSource


def dist(p, q):
    return math.sqrt(math.pow(p[0]-q[0], 2)+math.pow(p[1]-q[1],2))

def get(shapefile_obj, id):
    return shapefile_obj[id].points

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
    return precinct_queue[:300]

#def get_adjacency_list(file_name, outfile, threshold=10, fid_field=None):
def get_adjacency_list(file_name, threshold=10, fid_field=None):
    sf = shapefile.Reader(file_name).shapes()
    summary = summarize_precincts_info(sf)

    ds = DataSource(file_name)
    ds2 = DataSource(file_name)
    layer = ds[0]
    layer2 = ds2[0]

    all_edges = set()
    black_list = set()
    #outfh = open(outfile, 'w')
    target = len(layer)
    bar = IncrementalBar("creating adjacency list...".format(target), max=target)
    for i, feat in enumerate(layer):
        if fid_field == None:
            fid = feat.fid
        else:
            fid = feat[fid_field]

        try:
            #geom_orig = feat.geom
            geom_buf = feat.geom.geos.buffer(threshold)
        except:
            _temp = 1 # do nothing

        close_ones = get_close_precincts(sf, summary, feat.fid)
        layer2.spatial_filter = geom_buf.extent
        #new_edges = set()
        #for feat2 in layer2:
        for _fid in close_ones:
            feat2 = layer2[_fid]

            if fid_field == None:
                fid2 = feat2.fid
            else:
                fid2 = feat2[fid_field]

            #curr_edge = (fid, fid2)
            if fid2 <= fid:
                continue

            try:
                # Determine adjacency
                # Using the distance method is ~ 4X slower than buffer->intersect
                # adjacent = feat2.geom.geos.distance(geom_orig.geos) <= threshold
                adjacent = feat2.geom.geos.intersects(geom_buf)

                if adjacent:
                    all_edges.add((fid, fid2))
                    #new_edges.add(curr_edge)
                    #outfh.write("%d,%d\n" % (fid, fid2))
            except:
                _temp = 1 # do nothing
        #print(fid, " : " , new_edges)
        #outfh.flush()
        layer2.spatial_filter = None
        bar.next()

    #outfh.close()
    print(".")
    return list(all_edges)

get_adjacency_list("../shp/ohio/precincts_results.shp")
