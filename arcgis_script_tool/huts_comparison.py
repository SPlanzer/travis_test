# -*- coding: utf-8 -*-

################################################################################
#
# Copyright 2017 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the
# LICENSE file for more information.
#
################################################################################

""" Finds out "DESCRIPTIO" differences between 2 DOC huts datasets

Huts in newer dataset sometimes have different "DESCRIPTIO" even they are
referring to the same hut as the older dataset. This script finds out those
mismatches.

Args:
    Argument 1 (feature layer): older hut dataset
    Argument 2 (feature layer): newer hut dataset
    Argument 3 (double): search radius to compare huts, huts within the search
        radius are regarded to be the same hut
    Argument 4 (folder): output location
    Argument 5 (string): output file name
    Argument 6 (boolean): true if the user wants the resulting shapefile to
        be added to map canvas

Returns:
    A point shapefile of huts mismatches.

Todo:

"""
import arcpy

old_hut = arcpy.GetParameterAsText(0)
new_hut = arcpy.GetParameterAsText(1)
search_radius = float(arcpy.GetParameterAsText(2))
out_fol = arcpy.GetParameterAsText(3)+ "\\"
out_file = arcpy.GetParameterAsText(4)
add_to_map = arcpy.GetParameterAsText(5)
fields = ["DESCRIPTIO", "SHAPE@"]

old_crs = arcpy.Describe(old_hut).spatialReference
new_crs = arcpy.Describe(new_hut).spatialReference

if old_crs.name != new_crs.name:
    arcpy.AddMessage( "\nError: Both dataset must have the same spatial reference" )
else:

    feat_counter = -1
    pt_list = []

    cursor1 = arcpy.da.SearchCursor (old_hut, fields, None, old_crs, False, (None, None))
    for i in cursor1:

        if (feat_counter + 1) % 100 == 0:
            arcpy.AddMessage( "Processing: " + str(feat_counter + 1) )

        cursor2 = arcpy.da.SearchCursor (new_hut, fields, "FID > %s" % feat_counter, old_crs, False, (None, None))
        for j in cursor2:

            if i[0] != j[0] and i[1].distanceTo(j[1]) < search_radius:

                if i[1] not in pt_list:
                    pt_list.append(i[1])
                if j[1] not in pt_list:
                    pt_list.append(j[1])

        feat_counter += 1


    if not pt_list:
        arcpy.AddMessage( "No mismatch was found" )
    else:
        ptGeoms = []
        for p in pt_list:
            ptGeoms.append(p)
        arcpy.CopyFeatures_management(ptGeoms, out_fol + out_file)

    if add_to_map == "true":
    	mxd = arcpy.mapping.MapDocument("CURRENT")
    	dataFrame = arcpy.mapping.ListDataFrames(mxd, "*")[0]
        addLayer = arcpy.mapping.Layer(out_fol + out_file)
        arcpy.mapping.AddLayer(dataFrame, addLayer)

    arcpy.AddMessage( "Process Finished" )