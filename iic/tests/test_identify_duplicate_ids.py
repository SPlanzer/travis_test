"""
Test based on the example script scrpt_framework.py
Test compatable with both 2.18 and 2.14
Test original_id_check qgis user proccessing script
Assess the IIC suplied layer for t50_fid errors and returns layer of issues should they exist.

Issues include
1. No duplicate t50_fid values (not including null or 0) Returned error - duplicate

Tests
1. Is output created and does it return the expected number of rows
2. Are duplicate results returned and correctly annotated

"""

import sys
import os
import unittest

from qgis.utils import plugins
from qgis.utils import QGis
from qgis.core import QgsVectorLayer, QgsFeatureRequest
from PyQt4.QtCore import QSettings, QFileInfo

import processing
from processing import runalg, alglist
from processing.core.Processing import Processing
from processing.script.ScriptAlgorithm import ScriptAlgorithm
from processing.script.WrongScriptException import WrongScriptException
from processing.script.ScriptUtils import ScriptUtils

# set global variables
test_dir = '/tests_directory/iic/tests/testdata'
file_path = '/tests_directory/iic/identify_duplicate_ids.py'

# Set up test layers
input_layer = QgsVectorLayer(
    r"{}/identify_id_original.shp".format(test_dir),
    'original_BK39',
    'ogr')
if not input_layer.isValid():
    raise ImportError('Input Layer failed to load!')

updated_layer = QgsVectorLayer(
    r"{}/identify_id_updated.shp".format(test_dir),
    'updated_BK39',
    'ogr')
if not updated_layer.isValid():
    raise ImportError('Updated Layer failed to load!')

settings = QSettings()
try:
    settings.setValue(
        'Processing/lastScriptsDir',
        QFileInfo(file_path).absoluteDir().absolutePath())
    script = ScriptAlgorithm(file_path)
except WrongScriptException:
    raise WrongScriptException(
        'Could not load script: {0}'.format(file_path)
    )

# QGIS 2.14 has ScriptUtils.scriptsFolder()
if QGis.QGIS_VERSION_INT < 21800:
    dest_file_name = os.path.join(
        ScriptUtils.scriptsFolder(), os.path.basename(file_path))
# QGIS 2.18 has ScriptUtils.scriptsFolders()
elif QGis.QGIS_VERSION_INT >= 21800:
    dest_file_name = os.path.join(
        ScriptUtils.scriptsFolders()[0], os.path.basename(file_path))

with open(dest_file_name, 'w') as f:
    f.write(script.script)

# Refresh Processing Toolbox plugin
plugins['processing'].toolbox.updateProvider('script')
Processing.initialize()

# QGIS 2.14 has Processing.updateAlgsList()
if QGis.QGIS_VERSION_INT < 21800:
    Processing.updateAlgsList()
# QGIS 2.18 has algList.reloadProvider(('script')
elif QGis.QGIS_VERSION_INT >= 21800:
    from processing.core.alglist import algList
    algList.reloadProvider('script')

print alglist('identify duplicate ids')
result = runalg(
    "script:identifyduplicateids",
    input_layer,
    updated_layer,
    None
)

output_layer = processing.getObject(result['output'])


class TestOriginalIDCheck(unittest.TestCase):

    def test_valid_output(self):
        # Test for valid output
        self.assertEqual(output_layer.featureCount(), 2)

    def test_duplicate(self):
        # Test for duplicates
        found = False
        request = QgsFeatureRequest().setFilterExpression('t50_fid = 3205018')
        for feature in output_layer.getFeatures(request):
            self.assertEqual(feature['t50_origid'], 3205018)
            self.assertEqual(feature['error_type'], 'duplicate')
            found = True
        self.assertEqual(found, True)


def suite():
    """
    A test suite is a collection of test cases, test suites, or both.
    It is used to aggregate tests that should be executed together.
    """
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestOriginalIDCheck, 'test'))
    return suite


def run_tests():
    """
    Implements a TextTestRunner, which is a basic test runner implementation
    that prints results on standard error.
    """
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())
