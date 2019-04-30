#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 29 10:12:23 2019

@author: zackbarnes
"""
import shapefile

#Read in shp file
sf = shapefile.Reader('/Users/zackbarnes/Downloads/shp/precincts_results')
coor = sf.shapes()
records = sf.records()

#initialize dictionary
no_shp = {}
big_dct2 = {}


#Populate big dict of all Ohio precincts
for i in range(len(records) - 1):
    big_dct2[i] = records[i].as_dict()

#Save the precints with no shape in no_shp dict
for i, item in enumerate(coor):
    if item.shapeType == 0:
        no_shp[len(no_shp)] = records[i].as_dict()   
    

#Delete the shit we dont need
for i in range(len(big_dct2)-1):
    del big_dct2[i]['COUNTYGEOI']
    del big_dct2[i]['PRECINCTCO']
    del big_dct2[i]['PRECINCT_e']
    del big_dct2[i]['PRECINCT_m']
    del big_dct2[i]['global_id']
    del big_dct2[i]['pres_16_tu']
    del big_dct2[i]['media_mark']
    del big_dct2[i]['precinct_c']
    del big_dct2[i]['pres_16__1']
    del big_dct2[i]['pres_16__2']
    del big_dct2[i]['pres_16__3']
    del big_dct2[i]['pres_16__4']
    del big_dct2[i]['pres_16__5']
    del big_dct2[i]['pres_16__6']
    del big_dct2[i]['pres_16__7']
    del big_dct2[i]['pres_16_to']
    del big_dct2[i]['pres_16_ba']
    del big_dct2[i]['pres_16_be']
    del big_dct2[i]['pres_16_br']
    del big_dct2[i]['pres_16_ch']
    del big_dct2[i]['pres_16_da']
    del big_dct2[i]['pres_16_do']
    del big_dct2[i]['pres_16_ev']
    del big_dct2[i]['pres_16_ga']
    del big_dct2[i]['pres_16_hi']
    del big_dct2[i]['pres_16_ja']
    del big_dct2[i]['pres_16_ji']
    del big_dct2[i]['pres_16_jo']
    del big_dct2[i]['pres_16_la']
    del big_dct2[i]['pres_16_mi']
    del big_dct2[i]['pres_16_mo']
    del big_dct2[i]['pres_16_ri']
    del big_dct2[i]['region_nam']

#delete un-needed fields in no_shp
for i in range(len(no_shp)-1):
    del no_shp[i]['COUNTYGEOI']
    del no_shp[i]['PRECINCTCO']
    del no_shp[i]['PRECINCT_e']
    del no_shp[i]['PRECINCT_m']
    del no_shp[i]['global_id']
    del no_shp[i]['pres_16_tu']
    del no_shp[i]['media_mark']
    del no_shp[i]['precinct_c']
    del no_shp[i]['pres_16__1']
    del no_shp[i]['pres_16__2']
    del no_shp[i]['pres_16__3']
    del no_shp[i]['pres_16__4']
    del no_shp[i]['pres_16__5']
    del no_shp[i]['pres_16__6']
    del no_shp[i]['pres_16__7']
    del no_shp[i]['pres_16_to']
    del no_shp[i]['pres_16_ba']
    del no_shp[i]['pres_16_be']
    del no_shp[i]['pres_16_br']
    del no_shp[i]['pres_16_ch']
    del no_shp[i]['pres_16_da']
    del no_shp[i]['pres_16_do']
    del no_shp[i]['pres_16_ev']
    del no_shp[i]['pres_16_ga']
    del no_shp[i]['pres_16_hi']
    del no_shp[i]['pres_16_ja']
    del no_shp[i]['pres_16_ji']
    del no_shp[i]['pres_16_jo']
    del no_shp[i]['pres_16_la']
    del no_shp[i]['pres_16_mi']
    del no_shp[i]['pres_16_mo']
    del no_shp[i]['pres_16_ri']
    del no_shp[i]['region_nam']

#Delete any precinct with zero votes from ghost
for i in range(len(no_shp) - 1):
    if(no_shp[i]['pres_16_re'] == None or no_shp[i]['pres_16_re'] == 0):
        del no_shp[i]

#Trying to find a matching county to merge non-shp precincts to 
'''
throws errors when i == 5, as 5 was a deleted precinct
Consider using pop?
'''

for i in range(len(no_shp) -1):
    for j in range(len(big_dct2)-1):
        if(no_shp[i]['COUNTY'] == big_dct2[j]['COUNTY'] or no_shp[i]['county_nam'] == big_dct2[j]['county_nam']):
            print(i, j)
