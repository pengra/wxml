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
    for i in range(len(sf)):
        x = 0
        y = 0
        points = get(sf, i)
        if len(points) == 0:
            continue
        for p in points:
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

def get_adjacency_list(file_name, threshold=10):
    sf = shapefile.Reader(file_name).shapes()
    summary = summarize_precincts_info(sf)

    ds = DataSource(file_name)
    ds2 = DataSource(file_name)
    layer = ds[0]
    layer2 = ds2[0]

    all_edges = set()
    target = len(layer)
    bar = IncrementalBar("creating adjacency list...", max=target)
    for i, feat in enumerate(layer):
        bar.next()
        # If polygon have no points, skip
        if i not in summary.keys():
            continue
        fid = feat.fid

        geom_buf = feat.geom.geos.buffer(threshold)
        close_ones = get_close_precincts(sf, summary, feat.fid)
        layer2.spatial_filter = geom_buf.extent
        for _fid in close_ones:
            feat2 = layer2[_fid]
            fid2 = feat2.fid

            # efficiency improvement
            if fid2 <= fid:
                continue
            adjacent = feat2.geom.geos.intersects(geom_buf)
            pattern = feat2.geom.geos.relate(feat.geom.geos)

            # second part removes diagonals. "FF2F1" and "21210" are first 4 digits of DE-9IM Matrix code
            if adjacent and (pattern[:5] == "FF2F1" or pattern[:5] == "21210"):
                all_edges.add((fid, fid2))

        layer2.spatial_filter = None

    print(".")
    return list(all_edges)
