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

""" Finds out the spatial differences between KiwiRail and Topo50 Railway

Args:
    Argument 1 (feature layer): Topo50 dataset
    Argument 2 (feature layer): KiwiRail dataset, must not contain multi part
        geometries
    Argument 3 (SQL): User can select which lines to deal with. Default is
        "Type" = 'Main Centre' OR "Type" = 'Main Left' OR "Type" = 'Main Right'
    Argument 4 (double): buffer width, 2 lines seperated apart more than this
        distance is regarded as mismatch. Default is 2(m),
    Argument 5 (double): length tolerance, resulting lines shorter than this
        distance are ignored. Default is 20(m)
    Argument 6 (boolean): True if user wants to include merge feature function,
        It generates single-line road features in place of matched pairs of
        divided road lanes.
    Argument 7 (field): only enabled when arguemnt 6 is true, The field that
        contains road classification information. Only parallel, proximate roads
        of equal classification will be merged. Default is Type
    Argument 8 (field value): only enabled when argument 6 is true, selected
        values will be assisned as equal classification and merged. Default is
        Main Left, Main Right
    Argument 9 (double): only enabled when argument 6 is true, The minimum
        distance apart, in the specified units, for equal-class, relatively
        parallel road features to be merged. Default is 10
    Argument 10 (folder): output location

Returns:
    A line shapefile of railway mismatches.

Todo:

"""

import arcpy

line_1 = arcpy.GetParameterAsText(0)
line_2 = arcpy.GetParameterAsText(1)
line_to_deal_with = arcpy.GetParameterAsText(2)
buffer_width = arcpy.GetParameterAsText(3)
length_tolerance = arcpy.GetParameterAsText(4)
merge_function = arcpy.GetParameterAsText(5)
merge_field = arcpy.GetParameterAsText(6)
merge_feature = arcpy.GetParameterAsText(7)
merge_distance = arcpy.GetParameterAsText(8)
output_folder = arcpy.GetParameterAsText(9) + "\\"

# If user chose to ignore some features...
if line_to_deal_with:
    arcpy.Select_analysis(line_2, output_folder + "line_to_deal_with.shp", line_to_deal_with)
    line_2 = output_folder + "line_to_deal_with.shp"
    arcpy.AddMessage("Lines Selected")

# If user chose to generalise line features...
if merge_function == "true":
    arcpy.AddField_management(line_2, "merge_line", "SHORT")
    merge_feature_list = merge_feature.split(';')

    for i in range(len(merge_feature_list)):
        merge_feature_list[i] = str(merge_feature_list[i].strip("'"))

        merge_expression = "%s ='%s'" % (merge_field, merge_feature_list[i])
        with arcpy.da.UpdateCursor(line_2, "merge_line", merge_expression) as cursor:
            for row in cursor:
                row[0] = 1
                cursor.updateRow(row)

    arcpy.MergeDividedRoads_cartography(line_2, "merge_line", merge_distance, output_folder + "merged.shp")
    line_2 = output_folder + "merged.shp"
    arcpy.AddMessage("Features Merged")

# Create Buffer
arcpy.Buffer_analysis(line_1, output_folder + "buffer.shp", buffer_width + " Meter")
arcpy.AddMessage("Buffer Zone Created")

# Identity Analysis
arcpy.Identity_analysis (line_2, output_folder + "buffer.shp", output_folder + "identity.shp", "ONLY_FID")
arcpy.AddMessage("Identity Analysis Finished")

# Calculate Length of Lines
# shp does not store length attribute automatically so this tool is needed
arcpy.AddGeometryAttributes_management(output_folder + "identity.shp", "LENGTH_GEODESIC")
arcpy.AddMessage("Length Calculation Finished")

# Export the Resulting Line
arcpy.Select_analysis(output_folder + "identity.shp", output_folder + "difference.shp",
                      ' "FID_buffer"  = -1 AND "LENGTH_GEO" > ' + length_tolerance)
arcpy.AddMessage("All Done")
