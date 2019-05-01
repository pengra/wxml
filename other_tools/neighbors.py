################################################################################
# Copyright 2014 Ujaval Gandhi
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
################################################################################
import sys
from PyQt5.QtWidgets import QApplication
from qgis.core import QgsVectorLayer, QgsSpatialIndex, QgsApplication

def getLayer(shape_file_name):
    print("\tgetLayer started");
    app = QApplication([])
    print("\t1");
    QgsApplication.setPrefixPath("C:/OSGeo4W64/apps/qgis/", True) # Adjust prefix path according to your installation (see note below)
    print("\t2");
    QgsApplication.initQgis()
    print("\t3");

    #gpkg_places_layer = shape_file_name + "|layername=places"
    # e.g. gpkg_places_layer = "/home/project/data/data.gpkg|layername=places"
    #vlayer = QgsVectorLayer(gpkg_places_layer, "Precincts layer", "ogr")
    vlayer = QgsVectorLayer("../shp/ohio/precincts_results.shp", "Precincts layer", "ogr")
    print("\tQgsVectorLayer created");
    if not vlayer.isValid():
        print("Layer failed to load!")
    return vlayer


def getAllEdges(shape_file_name):
    # Replace the values below with values from your layer.
    # For example, if your identifier field is called 'XYZ', then change the line
    # below to _NAME_FIELD = 'XYZ'
    _NAME_FIELD = 'fid'
    layer = getLayer(shape_file_name)

    # Create a dictionary of all features
    feature_dict = {f.id(): f for f in layer.getFeatures()}

    # Build a spatial index
    index = QgsSpatialIndex()
    for f in feature_dict.values():
        index.insertFeature(f)

    result = {}
    # Loop through all features and find features that touch each feature
    for f in feature_dict.values():
        print('Working on %s' % f[_NAME_FIELD])
        geom = f.geometry()
        # Find all features that intersect the bounding box of the current feature.
        # We use spatial index to find the features intersecting the bounding box
        # of the current feature. This will narrow down the features that we need
        # to check neighboring features.
        intersecting_ids = index.intersects(geom.boundingBox())
        # Initalize neighbors list and sum
        neighbors = []
        for intersecting_id in intersecting_ids:
            # Look up the feature from the dictionary
            intersecting_f = feature_dict[intersecting_id]

            # For our purpose we consider a feature as 'neighbor' if it touches or
            # intersects a feature. We use the 'disjoint' predicate to satisfy
            # these conditions. So if a feature is not disjoint, it is a neighbor.
            if (f != intersecting_f and
                not intersecting_f.geometry().disjoint(geom)):
                neighbors.append(intersecting_f[_NAME_FIELD])
        result[f[_NAME_FIELD]] = neighbors
    return result
