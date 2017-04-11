"""
Test based on the example script scrpt_framework.py
copy this file, edit it to test your script and name
it test_{NAME_OF_YOUR_SCRIPT}.py

When running this test script locally within QGIS
The variables test_dir and file_path need
to be changed.

"""

import sys
import os
import unittest
from qgis.utils import plugins
from qgis.utils import QGis
from qgis.core import QgsVectorLayer
from processing import runalg, alglist
from processing.core.Processing import Processing
from processing.script.ScriptAlgorithm import ScriptAlgorithm
from processing.script.WrongScriptException import WrongScriptException
from processing.script.ScriptUtils import ScriptUtils
from PyQt4.QtCore import QSettings, QFileInfo

# set global variables
test_dir = '/tests_directory/iic/tests/testdata'
file_path = '/tests_directory/iic/script_framework.py'

# Set up test layers
input_layer = QgsVectorLayer(
    r"{}/script_framework_original.shp".format(test_dir),
    'original_BK39',
    'ogr')
if not input_layer.isValid():
    raise ImportError('Input Layer failed to load!')

updated_layer = QgsVectorLayer(
    r"{}/script_framework_updated.shp".format(test_dir),
    'updated_BK39',
    'ogr')
if not updated_layer.isValid():
    raise ImportError('Updated Layer failed to load!')


class TestScriptFramework(unittest.TestCase):

    def setUp(self):
        """
        Setting up TestScriptFramework and adding algorithm
        to Processing Toolbox.
        Do not remove this function!
        """
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

    def test_run_script_framework(self):
        """This is where you put your customized code to run your script"""
        print alglist('script framework')
        result = runalg(
            "script:scriptframework",
            input_layer,
            updated_layer,
            50,
            None
        )
        output_layer = QgsVectorLayer(
            result['output'], 'output_layer', 'ogr')

        # Count should be 0, because nothing was selected
        self.assertEqual(output_layer.featureCount(), 0)


def suite():
    """
    A test suite is a collection of test cases, test suites, or both.
    It is used to aggregate tests that should be executed together.
    """
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestScriptFramework, 'test'))
    return suite


def run_tests():
    """
    Implements a TextTestRunner, which is a basic test runner implementation
    that prints results on standard error.
    """
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())
