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
""" Extract the Road DB roads

The Topo team currently runs a process (Pearl script created by Chris Crook)
to extract Landonline roads to check Topo50 roads against.
This process is run regularly by the Topo team, eg. a few times a week.
A similar process is required to extract the Road DB roads for the Topo team.
This script tool:
(1) Extracts roads based on area (map sheet)
(2) Converts full_road_ values to ALL CAPS
(3) Merges geometries on road_id, full_road_, and when two roads are connected
(4) Projects the resulting shapefile as NZTM2000 (ESPG 2193)

Args:
    Argument 1 (feature layer): Linz map sheet
    Argument 2 (field value): Map sheet number
    Argument 3 (feature layer): Road dataset
    Argument 4 (folder): output location
    Argument 5 (string): output file name
    Argument 6 (boolean): true if the user wants the resulting shapefile to
        be added to map canvas

Returns:
    A line shapefile of extracted road dataset.

Todo:

"""

import arcpy

map_sheet = arcpy.GetParameterAsText(0)
target_sheet_code = arcpy.GetParameterAsText(1)
in_road = arcpy.GetParameterAsText(2)
out_fol = arcpy.GetParameterAsText(3) + "\\"
out_file = arcpy.GetParameterAsText(4)
add_to_map = arcpy.GetParameterAsText(5)

arcpy.AddMessage( "\nSelecting Map Sheet..." )
arcpy.Select_analysis (map_sheet, out_fol+ "target_sheet", "sheet_code = '%s'" % target_sheet_code)

arcpy.AddMessage( "Clipping Road Dataset..." )
arcpy.Clip_analysis (in_road, out_fol+ "target_sheet.shp", out_fol+ "road_clipped.shp")

arcpy.AddMessage( "Converting values in 'full_road_' to upper case..." )
crs = arcpy.Describe(in_road).spatialReference
cursor = arcpy.da.UpdateCursor (out_fol + "road_clipped.shp", ["full_road_"], None, crs, False, (None, None))
for row in cursor:
    row[0] = row[0].upper()
    cursor.updateRow(row)

arcpy.AddMessage( "Disolving Roads..." )
arcpy.Dissolve_management (out_fol + "road_clipped.shp", out_fol + "road_dissolved", ["road_id", "full_road_"], "", "MULTI_PART", "UNSPLIT_LINES")

arcpy.AddMessage( "Reprojecting Road Dataset ..." )
sr = arcpy.SpatialReference(2193)
arcpy.Project_management (out_fol + "road_dissolved.shp", out_fol + out_file, sr)

if add_to_map == "true":
    mxd = arcpy.mapping.MapDocument("CURRENT")
    dataFrame = arcpy.mapping.ListDataFrames(mxd, "*")[0]
    addLayer = arcpy.mapping.Layer(out_fol + out_file)
    arcpy.mapping.AddLayer(dataFrame, addLayer)

arcpy.Delete_management(out_fol+ "target_sheet.shp")
arcpy.Delete_management(out_fol + "road_clipped.shp")
arcpy.Delete_management(out_fol + "road_dissolved.shp")

arcpy.AddMessage( "Process Finished\n" )