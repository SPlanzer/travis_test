
## Testing Topo Utility Scripts

[Unittest docs](https://docs.python.org/2/library/unittest.html)

### Steps to adding test script

1. Make sure your branch is up-to-date with remote master

2. Copy the test_script_framework.py into your iic/tests folder. Rename the script
**test_<name_of_your_script>.py**

3. Place your test shapefiles into iic/tests/testdata and rename them **<name_of_your_script>_original**
and **<name_of_your_script>_updated**.

4. In the test script itself, the two global variables test_dir and file_path need to be changed to your local paths
	```python
	# set global variables
	test_dir = 'your/path/to/iic/tests/testdata'
	file_path = 'your/path/to/iic/<name_of_your_script>.py'
	```

5. Also in the test script: where the words **script framework** appear, change these to the name of your script
	- input_layer = QgsVectorLayer(  
	    r"{}/**script_framework**_original.shp".format(test_dir),  
	    'original_BK39',  
	    'ogr')  
	  updated_layer = QgsVectorLayer(  
	    r"{}/**script_framework**_updated.shp".format(test_dir),  
	    'updated_BK39',  
	    'ogr')  
	- class **TestScriptFramework**(unittest.TestCase):
	- 
	    def test_run_**script_framework**(self)
	    Within this function make sure alglist() and runalg() is referencing your script,
	    with the correct number of parameters.
	    Some [documentation](https://docs.qgis.org/2.14/en/docs/user_manual/processing/scripts.html#writing-new-processing-algorithms-as-python-scripts) on runalg, etc.
	- suite.addTests(unittest.makeSuite(**TestScriptFramework**, 'test'))
	- :exclamation:  Note: You do not have to change anything in the setUp() function.

6. Write your own tests within the test case. The [unittest documentation](https://docs.python.org/2/library/unittest.html) has good examples of how to write them.

### Running Tests

Test script to be run from your QGIS Python Consule.


### Travis CI setup before your Pull Request

The steps below will make sure that travis runs properly and recognizes your tests. 
This is a temporary solution, trying to come up with something better...

1. Change file paths back to original (shown below). file_path is the path to your script, not your test script.
	```python
	# set global variables
	test_dir = '/tests_directory/iic/tests/testdata'
	file_path = '/tests_directory/iic/<name_of_your_script>.py'
	```
2. Add a line to the list of scripts in .travis.yml file (under the script header).
	```yml
	script:
      - docker exec -it qgis-testing-environment sh -c "qgis_testrunner.sh ${SCRIPT_DIR}.tests.test_script_framework.run_tests; "
	  - docker exec -it qgis-testing-environment sh -c "qgis_testrunner.sh ${SCRIPT_DIR}.tests.test_<name_of_your_script>.run_tests; "
	```
