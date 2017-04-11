import unittest

from qgis.utils import plugins
from qgis.utils import QGis
from qgis.core import QgsVectorLayer, QgsFeatureRequest
from PyQt4.QtCore import QSettings, QFileInfo




class TestFoo(unittest.TestCase):
    
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')
        

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestFoo, 'test'))
    return suite

def run_tests():
    unittest.TextTestRunner(verbosity=3, stream=sys.stdout).run(suite())

