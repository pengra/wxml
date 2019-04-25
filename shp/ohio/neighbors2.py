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
from qgis.utils import iface
from PyQt5.QtCore import QVariant

# Replace the values below with values from your layer.
# For example, if your identifier field is called 'XYZ', then change the line
# below to _NAME_FIELD = 'XYZ'
_NAME_FIELD = 'fid'
# Replace the value below with the field name that you want to sum up.
# For example, if the # field that you want to sum up is called 'VALUES', then
# change the line below to _SUM_FIELD = 'VALUES'
_SUM_FIELD = 'pres_16_re'

layer = iface.activeLayer()
# Create a dictionary of all features
feature_dict = {f.id(): f for f in layer.getFeatures()}

# Build a spatial index
index = QgsSpatialIndex()
for f in feature_dict.values():
    index.insertFeature(f)


with open('output.txt', 'w') as file_output:
    # Loop through all features and find features that touch each feature
    for f in feature_dict.values():
        geom = f.geometry()
        # Find all features that intersect the bounding box of the current feature.
        # We use spatial index to find the features intersecting the bounding box
        # of the current feature. This will narrow down the features that we need
        # to check neighboring features.
        intersecting_ids = index.intersects(geom.boundingBox())
        # Initalize neighbors list and sum
        #neighbors_sum = 0
        
        if f[_NAME_FIELD] % 1000 == 0:
            print(f[_NAME_FIELD]);
        
        for intersecting_id in intersecting_ids:
            # Look up the feature from the dictionary
            intersecting_f = feature_dict[intersecting_id]
            
            # For our purpose we consider a feature as 'neighbor' if it touches or
            # intersects a feature. We use the 'disjoint' predicate to satisfy
            # these conditions. So if a feature is not disjoint, it is a neighbor.
            if (f != intersecting_f and
                not intersecting_f.geometry().disjoint(geom)):
                t = (int(f[_NAME_FIELD]),int(intersecting_f[_NAME_FIELD]))
                file_output.write("{}\n".format(t))
                #print("({},{})".format(int(f[_NAME_FIELD]),int(intersecting_f[_NAME_FIELD]))); 
                #neighbors.append(intersecting_f[_NAME_FIELD])
                #neighbors_sum += intersecting_f[_SUM_FIELD]
            
        #f[_NEW_NEIGHBORS_FIELD] = ','.join(neighbors)
        #f[_NEW_SUM_FIELD] = neighbors_sum
        # Update the layer with new attribute values.
        #layer.updateFeature(f)

print("finished");

#layer.commitChanges()
print('Processing complete.')
