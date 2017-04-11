##orig_layer=vector
##iic_layer=vector
##output=output vector


from qgis.core import *
from PyQt4.QtCore import *

orig_lyr = processing.getObjectFromUri(orig_layer)
iic_lyr = processing.getObjectFromUri(iic_layer)

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

writer = QgsVectorFileWriter(output, None, fields,QGis.WKBLineString, orig_lyr.crs())



def identify_new_ids():
    out_feat = QgsFeature()
    """
	Assess the IIC suplied layer for t50_fid errors and returns layer of issues should they exist.

	Issues include
	1. No new t50_fid values (not including null or 0) Returned error - false added id
	
	"""
    # List of t50_fid for the original and iic layer
    original_id = [f["t50_fid"]for f in processing.features(orig_lyr)]
    iic_id = [f["t50_fid"]for f in processing.features(iic_lyr)]

    # icc_Id is a subset of original_Id
    iic_subs = list(set(iic_id) - (set(original_id)))
    iic_subset = [f for f in iic_subs if f != 0 if f is not None]

    # write any returned values to the output file.
    for false_added in iic_subset:
        request = QgsFeatureRequest().setFilterExpression('t50_fid = {}'.format(false_added))
        for feature in iic_lyr.getFeatures(request):
            geom = feature.geometry()
            attrs = feature.attributes()
            attrs.extend([false_added, "false added id", ""])
            out_feat.setGeometry(geom)
            out_feat.setAttributes(attrs)
            writer.addFeature(out_feat)

identify_new_ids()
del writer


