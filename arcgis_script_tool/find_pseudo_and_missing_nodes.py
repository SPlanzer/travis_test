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

""" Finds pseudo nodes and missing nodes of the input line layer

When finding pseudo nodes, it ignore nodes found on a looping road and nodes
that are within 1 metre of the map sheet boundaries

Args:
    Argument 1 (feature layer): Input line layer
    Argument 2 (feature layer): Linz map sheet
    Argument 3 (boolean): true if input layer is road
    Argument 4 (boolean): true if input layer is track
    Argument 5 (boolean): true if input layer is not road nor track
    Argument 6 (folder): output location
    Argument 7 (boolean): true if the user wants to find pseudo nodes
    Argument 8 (string): enabled only when argument 7 is true. Output pseudo
        nodes file name
    Argument 9 (boolean): true if the user wants to find missing nodes
    Argument 10 (string): enabled only when argument 9 is true. Output missing
        nodes file name
    Argument 11 (boolean): true if the user wants the resulting shapefile to
        be added to map canvas

Returns:
    1 point shapefile of pseudo nodes, 1 point shapefile of missing nodes.

Todo:
    The script is slow when handling input layer that is not road nor track. The
    "Generate Near Table" Tool in ArcGIS may provide an faster alternative.
"""

import arcpy

in_line_layer = arcpy.GetParameterAsText(0)
map_sheet_pol = arcpy.GetParameterAsText(1)
road_test = arcpy.GetParameterAsText(2)
track_test = arcpy.GetParameterAsText(3)
other_test = arcpy.GetParameterAsText(4)
out_fol = arcpy.GetParameterAsText(5) + "\\"
find_pseudo_nodes = arcpy.GetParameterAsText(6)
out_pseudo_layer = out_fol + arcpy.GetParameterAsText(7)
find_missing_nodes = arcpy.GetParameterAsText(8)
out_missing_layer = out_fol + arcpy.GetParameterAsText(9)
add_to_map = arcpy.GetParameterAsText(10)

if road_test == "true":
    fields = ["FID", "name", "hway_num", "lane_count", "status", "surface", "SHAPE@"]
elif track_test == "true":
    fields = ["FID", "name", "status", "track_type", "track_use", "SHAPE@"]
elif other_test == "true":
    fields = ["FID", "SHAPE@"]
crs = arcpy.Describe(in_line_layer).spatialReference

""" Find Pseudo Nodes """
if find_pseudo_nodes == "true":
	arcpy.AddMessage( "\nFinding Pseudo Nodes..." )

	def neighbour_test(pt):

		# Test if the node is on an intersecting road (more than 2 neighbours)
		neighbour = 0
		cursor3 = arcpy.da.SearchCursor (in_line_layer, ["SHAPE@"], None, crs, False, (None, None))
		for k in cursor3:
			if pt.touches(k[0]):
				neighbour += 1
		if neighbour < 3:

			# Test if the node is near the edge of the map_sheet_layer (less than 1 metre)
			cursor4 = arcpy.da.SearchCursor (map_sheet_pln, ["SHAPE@"], None, crs, False, (None, None))
			is_near_edge = False
			for l in cursor4:
				if l[0].distanceTo(pt) < 1:
					is_near_edge = True
					break
			if is_near_edge == False:
				pseudo_list.append(pt)

	arcpy.PolygonToLine_management (map_sheet_pol, out_fol + "line.shp", False)
	map_sheet_pln = out_fol + "line.shp"
	feature_counter = 0
	completed = []
	pseudo_list =[]

	cursor1 = arcpy.da.SearchCursor (in_line_layer, fields, None, crs, False, (None, None))
	for i in cursor1:
		if feature_counter % 50 == 0:
			arcpy.AddMessage( "Processing: " + str(feature_counter) )

		if str(i[-1].firstPoint) != str(i[-1].lastPoint):		# Ignore the looping road (i)
			if i[0] not in completed:

				cursor2 = arcpy.da.SearchCursor (in_line_layer, fields, "FID > %s" % feature_counter, crs, False, (None, None)) # cursor2 does not search the nodes that has been gone through by cursor1
				for j in cursor2:

					# Test if they have same attributes
					if road_test == "true":
						attr_test = i[0] != j[0] and i[1] == j[1] and i[2] == j[2] and i[3] == j[3]and i[4] == j[4] and i[5] == j[5]
					elif track_test == "true":
						attr_test = i[0] != j[0] and i[1] == j[1] and i[2] == j[2] and i[3] == j[3] and i[4] == j[4]
					elif other_test == "true":
						attr_test = i[0] != j[0]

					if attr_test:
						# Ignore the looping road (j)
						if str(j[-1].firstPoint) != str(j[-1].lastPoint):

							# Test if they are connected lines (at i's first point)
							if str(i[-1].firstPoint) == str(j[-1].firstPoint) or str(i[-1].firstPoint) == str(j[-1].lastPoint):
								pt = i[-1].firstPoint
								completed.append(j[0])
								if pt not in pseudo_list:
									neighbour_test(pt)

							# Test if they are connected lines (at i's last point)
							elif str(i[-1].lastPoint) == str(j[-1].lastPoint) or str(i[-1].lastPoint) == str(j[-1].firstPoint):
								pt = i[-1].lastPoint
								completed.append(j[0])
								if pt not in pseudo_list:
									neighbour_test(pt)
		feature_counter += 1

	arcpy.Delete_management(map_sheet_pln)

	# Create a Point shp for every point in pseudo_list
	if not pseudo_list:
		arcpy.AddMessage( "No Pseudo Nodes Found in Layer" )
	else:
		arcpy.AddMessage( "Creating Pseudo Nodes Layer..." )
		pt = arcpy.Point()
		ptGeoms = []
		for p in pseudo_list:
			pt.X = p.X
			pt.Y = p.Y
			ptGeoms.append(arcpy.PointGeometry(pt, crs))
		arcpy.CopyFeatures_management(ptGeoms, out_pseudo_layer)
		arcpy.AddMessage( "Pseudo Nodes Layer Exported: " + out_pseudo_layer )

""" Find Missing Nodes """
if find_missing_nodes == "true":
	arcpy.AddMessage( "\nFinding Missing Nodes..." )
	feature_counter = 0
	missing_list = []

	cursor5 = arcpy.da.SearchCursor (in_line_layer, fields, None, crs, False, (None, None))
	for m in cursor5:

		if feature_counter % 50 == 0:
			arcpy.AddMessage( "Processing: " + str(feature_counter) )

		cursor6 = arcpy.da.SearchCursor (in_line_layer, fields, None, crs, False, (None, None))
		for n in cursor6:

			# Test if they have same attributes
			if road_test == "true":
				attr_test = m[0] != n[0] and m[1] == n[1] and m[2] == n[2] and m[3] == n[3] and m[4] == n[4] and m[5] == n[5]
			elif track_test == "true":
				attr_test = m[0] != n[0] and m[1] == n[1] and m[2] == n[2] and m[3] == n[3] and m[4] == n[4]
			elif other_test == "true":
				attr_test = m[0] != n[0]

			# Test if the node is contained (NOT connected) in the line
			if attr_test:
				if str(m[-1].firstPoint) != str(n[-1].firstPoint) and str(m[-1].firstPoint) != str(n[-1].lastPoint) and str(m[-1].lastPoint) != str(n[-1].firstPoint) and str(m[-1].lastPoint) != str(n[-1].lastPoint):
					if m[-1].contains(n[-1].firstPoint):
						pt = n[-1].firstPoint
						if pt not in missing_list:
							missing_list.append(pt)

					if m[-1].contains(n[-1].lastPoint):
						pt = n[-1].lastPoint
						if pt not in missing_list:
							missing_list.append(pt)
		feature_counter += 1

	# Create a Point shp for every point in missing_list
	if not missing_list:
		arcpy.AddMessage( "No Missing Nodes Found in Layer" )
	else:
		arcpy.AddMessage( "Creating Missing Nodes Layer..." )                 # An easier way:
		pt = arcpy.Point()                                                    # ptGeoms = []
		ptGeoms = []                                                          # for p in missing_list:
		for p in missing_list:                                                # ptGeoms.append(p)
			pt.X = p.X                                                        # arcpy.CopyFeatures_management(ptGeoms, out_missing_layer)
			pt.Y = p.Y
			ptGeoms.append(arcpy.PointGeometry(pt, crs))
		arcpy.CopyFeatures_management(ptGeoms, out_missing_layer)
		arcpy.AddMessage( "Missing Nodes Layer Exported: " + out_missing_layer )

# Add the shp to the map canvas
if add_to_map == "true":
	mxd = arcpy.mapping.MapDocument("CURRENT")
	dataFrame = arcpy.mapping.ListDataFrames(mxd, "*")[0]
	if find_pseudo_nodes == "true" and pseudo_list:
		addLayer = arcpy.mapping.Layer(out_pseudo_layer)
		arcpy.mapping.AddLayer(dataFrame, addLayer)
	if find_missing_nodes == "true" and missing_list:
		addLayer = arcpy.mapping.Layer(out_missing_layer)
		arcpy.mapping.AddLayer(dataFrame, addLayer)

arcpy.AddMessage( "\nProcess Finished" )
