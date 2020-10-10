import os
import unittest

class GoldenFileTest(unittest.TestCase):

    def setup(self):
        curr_path = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(curr_path, 'data')

    def tearDown(self):
        pass

    def test_library_file(self):
        pass