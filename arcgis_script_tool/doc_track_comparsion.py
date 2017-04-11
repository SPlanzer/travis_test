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

""" Compare 2 DOC track dataset

This script finds out the attribute mismatches and spatial mismatches between
2 DOC track datasets. If the track has the same "URL" but different "DESCRIPTIO"
they are considered as attribute mismatches. User can set their own parameter to
define spatial mismatch.

Args:
    Argument 1 (feature layer): older track dataset
    Argument 2 (SQL): User can select which lines to deal with in the older
        track dataset
    Argument 3 (feature layer): newer track dataset
    Argument 4 (SQL): User can select which lines to deal with in the newer
        track dataset
    Argument 5 (double): buffer width, 2 lines seperated apart more than this
        distance is regarded as mismatch. Default is 1(m)
    Argument 6 (double): length tolerance, resulting lines shorter than this
        distance are ignored, default is 10(m)
    Argument 7 (folder): output location
    Argument 8 (boolean): true if the user wants the resulting shapefiles to
        be added to map canvas

Returns:
    1 line shapefile of attribute mismatches. 2 line shapefiles of spatial
    mismatches

Todo:

"""

import arcpy

old_track = arcpy.GetParameterAsText(0)
old_track_sel = arcpy.GetParameterAsText(1)
new_track = arcpy.GetParameterAsText(2)
new_track_sel = arcpy.GetParameterAsText(3)
buffer_width = arcpy.GetParameterAsText(4)
length_tolerance = arcpy.GetParameterAsText(5)
output_folder = arcpy.GetParameterAsText(6) + "\\"
add_to_map = arcpy.GetParameterAsText(7)

old_crs = arcpy.Describe(old_track).spatialReference
new_crs = arcpy.Describe(new_track).spatialReference

if old_crs.name != new_crs.name:
    arcpy.AddMessage( "\nError: Both dataset must have the same spatial reference" )
else:

    # If the user chooses to ignore some features...
    if old_track_sel or new_track_sel:
        arcpy.AddMessage("\nSelecting features to deal with...")

    if old_track_sel:
        arcpy.Select_analysis(old_track, output_folder + "old_track_sel.shp", old_track_sel)
        old_track = output_folder + "old_track_sel.shp"
        arcpy.AddMessage("Lines of Input 1 Selected")

    if new_track_sel:
        arcpy.Select_analysis(new_track, output_folder + "new_track_sel.shp", new_track_sel)
        new_track = output_folder + "new_track_sel.shp"
        arcpy.AddMessage("Lines of Input 2 Selected")

    """ Find Attribute Differences """
    arcpy.AddMessage("\nFinding Attribute Differences...")
    feat_counter = -1
    pln_list = []
    cursor1 = arcpy.da.SearchCursor (old_track, ["FID", "DESCRIPTIO", "URL"], None, old_crs, False, (None, None))
    for i in cursor1:

        if (feat_counter + 1) % 100 == 0:
            arcpy.AddMessage( "Processing: " + str(feat_counter + 1) )

        cursor2 = arcpy.da.SearchCursor (new_track, ["FID", "DESCRIPTIO", "URL"], "FID > %s" % feat_counter, old_crs, False, (None, None))
        for j in cursor2:

            if int(i[2]) == int(j[2]) and i[1] != j[1]:

                    cursor3 = arcpy.da.SearchCursor (old_track, ["SHAPE@"], "FID = %s" % i[0], old_crs, False, (None, None))
                    for k in cursor3:
                        pln_list.append(k[0])

                    cursor4 = arcpy.da.SearchCursor (new_track, ["SHAPE@"], "FID = %s" % j[0], old_crs, False, (None, None))
                    for l in cursor4:
                        pln_list.append(l[0])

                    break
        feat_counter += 1

    if not pln_list:
        arcpy.AddMessage( "Attribute Differences: Not Found" )
    else:
        plnGeoms = []
        for pln in pln_list:
            plnGeoms.append(pln)
        arcpy.CopyFeatures_management(plnGeoms, output_folder + "attr_diff")
        arcpy.AddMessage( "Finished Finding Attribute Differences" )


    """ Find Spatial Differences """
    arcpy.AddMessage("\nFinding Spatial Differences...")

    # Create Buffer
    arcpy.AddMessage("Creating Buffer Zones...")
    arcpy.Buffer_analysis(old_track, output_folder + "old_buf.shp", buffer_width + " Meter")
    arcpy.Buffer_analysis(new_track, output_folder + "new_buf.shp", buffer_width + " Meter")
    arcpy.AddMessage("Buffer Zones Created...")

    # Identity Analysis
    arcpy.AddMessage("Carrying Out Identity Analysis...")
    arcpy.Identity_analysis (old_track, output_folder + "new_buf.shp", output_folder + "identity1.shp", "ONLY_FID")
    arcpy.Identity_analysis (new_track, output_folder + "old_buf.shp", output_folder + "identity2.shp", "ONLY_FID")
    arcpy.AddMessage("Identity Analysis Completed")

    # Calculate Length of Lines (shp does not store length attribute automatically so this tool is needed)
    arcpy.AddMessage("Calculating Length")
    arcpy.AddGeometryAttributes_management(output_folder + "identity1.shp", "LENGTH_GEODESIC")
    arcpy.AddGeometryAttributes_management(output_folder + "identity2.shp", "LENGTH_GEODESIC")
    arcpy.AddMessage("Length Calculation Finished")

    # Export the Resulted Line
    arcpy.AddMessage("Exporting Spatial Differences...")
    arcpy.Select_analysis(output_folder + "identity1.shp", output_folder + "spat_diff_1.shp",
                          ' "FID_new_bu"  = -1 AND "LENGTH_GEO" > ' + length_tolerance)
    arcpy.Select_analysis(output_folder + "identity2.shp", output_folder + "spat_diff_2.shp",
                          ' "FID_old_bu"  = -1 AND "LENGTH_GEO" > ' + length_tolerance)

    if old_track_sel:
        arcpy.Delete_management (output_folder + "old_track_sel.shp")
    if new_track_sel:
        arcpy.Delete_management (output_folder + "new_track_sel.shp")
    arcpy.Delete_management (output_folder + "old_buf.shp")
    arcpy.Delete_management (output_folder + "new_buf.shp")
    arcpy.Delete_management (output_folder + "identity1.shp")
    arcpy.Delete_management (output_folder + "identity2.shp")

    if add_to_map == "true":
        mxd = arcpy.mapping.MapDocument("CURRENT")
        dataFrame = arcpy.mapping.ListDataFrames(mxd, "*")[0]
        if pln_list:
            addLayer = arcpy.mapping.Layer(output_folder + "attr_diff.shp")
            arcpy.mapping.AddLayer(dataFrame, addLayer)
        addLayer = arcpy.mapping.Layer(output_folder + "spat_diff_1.shp")
        arcpy.mapping.AddLayer(dataFrame, addLayer)
        addLayer = arcpy.mapping.Layer(output_folder + "spat_diff_2.shp")
        arcpy.mapping.AddLayer(dataFrame, addLayer)

    arcpy.AddMessage( "Process Finished\n" )
