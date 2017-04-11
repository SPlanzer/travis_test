##original_layer=vector
##IIC_layer=vector
##input_variable=number 50
##output=output vector

from qgis.core import *
from PyQt4.QtCore import *

# Assign variables to the original topo50 layer, IIC layer
# and any input variables so they cna be reused.

orig_lyr = processing.getObjectFromUri(original_layer)
iic_lyr = processing.getObjectFromUri(IIC_layer)
your_variable = input_variable

# Create the fields for the output layer
fields = QgsFields()

fields_list = [
    QgsField("t50_fid", QVariant.Int),
    QgsField("name_ascii", QVariant.String),
    QgsField("macronated", QVariant.String),
    QgsField("name", QVariant.String),
    QgsField("hway_num", QVariant.String),
    QgsField("rna_sufi", QVariant.Int),
    QgsField("lane_count", QVariant.Int),
    QgsField("way_count", QVariant.String),
    QgsField("status", QVariant.String),
    QgsField("surface", QVariant.String),
    QgsField("new_lane_c", QVariant.Int),
    QgsField("new_surfac", QVariant.String),
    QgsField("width", QVariant.String),
    QgsField("access", QVariant.String),
    QgsField("t50_origid", QVariant.Int),
    QgsField("error_type", QVariant.String),
    QgsField("error_comm", QVariant.String)
]

for field in fields_list:
    fields.append(field)

# Create a shapefile in the location specified by the user under output
writer = QgsVectorFileWriter(output, None, fields,
                             QGis.WKBLineString, orig_lyr.crs())


def your_function():
    """An example of using a QgsFeature to update the output layer"""
    out_feat = QgsFeature()
    for feature in iic_lyr.selectedFeatures():
        geom = feature.geometry()
        attrs = feature.attributes()
        attrs.extend([666, "bad", "no comment"])
        out_feat.setGeometry(geom)
        out_feat.setAttributes(attrs)
        writer.addFeature(out_feat)


your_function()


del writer
