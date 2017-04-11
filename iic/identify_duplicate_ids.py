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



def identify_duplicate_ids():
    out_feat = QgsFeature()
    """
	Assess the IIC suplied layer for t50_fid errors and returns layer of issues should they exist.

	Issues include
	1. No duplicate t50_fid values (not including null or 0) Returned error - duplicate
	
	"""
    # List of t50_fid for the original and iic layer
    original_id = [f["t50_fid"]for f in processing.features(orig_lyr)]
    iic_id = [f["t50_fid"]for f in processing.features(iic_lyr)]

    # Duplicate iic ids
    dup_iic_id = set([f for f in iic_id if iic_id.count(f) > 1])
    duplicate_id = [f for f in dup_iic_id if f != 0 if f is not None]

    # write any returned values to the output file.
    for duplicate in duplicate_id:
        request = QgsFeatureRequest().setFilterExpression('t50_fid = {}'.format(duplicate))
        for feature in iic_lyr.getFeatures(request):
            geom = feature.geometry()
            attrs = feature.attributes()
            attrs.extend([duplicate, "duplicate", ""])
            out_feat.setGeometry(geom)
            out_feat.setAttributes(attrs)
            writer.addFeature(out_feat)

identify_duplicate_ids()
del writer


