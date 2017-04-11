##linz_test_layer=output vector
##iic_test_layer=output vector
##input_crs=number 2193

from qgis.core import *
from PyQt4.QtCore import *

crs_parameter = input_crs
if crs_parameter == 2193:
	crs = QgsCoordinateReferenceSystem("EPSG:2193")
elif crs_parameter == 4167:
	crs = QgsCoordinateReferenceSystem("EPSG:4167")

linz_fields = QgsFields()

linz_fields_list = [QgsField("t50_fid", QVariant.Int),
               QgsField("name_ascii", QVariant.String),
               QgsField("macronated", QVariant.String),
               QgsField("name", QVariant.String),
               QgsField("hway_num", QVariant.String),
               QgsField("rna_sufi", QVariant.Int),
               QgsField("lane_count", QVariant.Int),
               QgsField("way_count", QVariant.String),
               QgsField("status", QVariant.String),
               QgsField("surface", QVariant.String),
               QgsField("test_case", QVariant.String)]

for field in linz_fields_list:
    linz_fields.append(field)

iic_fields = QgsFields()

iic_fields_list = [QgsField("t50_fid", QVariant.Int),
               QgsField("name_ascii", QVariant.String),
               QgsField("macronated", QVariant.String),
               QgsField("name", QVariant.String),
               QgsField("hway_num", QVariant.String),
               QgsField("rna_sufi", QVariant.Int),
               QgsField("lane_count", QVariant.Int),
               QgsField("way_count", QVariant.String),
               QgsField("status", QVariant.String),
               QgsField("surface", QVariant.String),
               QgsField("new_lane_count", QVariant.Int),
               QgsField("new_surface", QVariant.String),
               QgsField("width", QVariant.String),
               QgsField("width", QVariant.String),
               QgsField("test_case", QVariant.String)]

for field in iic_fields_list:
    iic_fields.append(field)

writer = QgsVectorFileWriter(linz_test_layer, None, linz_fields,
                             QGis.WKBLineString, crs)

writer = QgsVectorFileWriter(iic_test_layer, None, iic_fields,
                             QGis.WKBLineString, crs)