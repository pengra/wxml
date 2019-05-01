import shapefile
def create_adjacency_list(shape_file_name):
    sf = shapefile.Reader(shapeFileName).shape()
