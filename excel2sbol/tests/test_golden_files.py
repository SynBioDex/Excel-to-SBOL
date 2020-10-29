import excel2sbol.main as tool
import os
import unittest

class GoldenFileTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    def setUp(self):
        curr_path = os.path.dirname(os.path.realpath(__file__))
        self.data_dir = os.path.join(curr_path, 'data')

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_convert_part_library(self):
        file = 'darpa_template.xlsx'
        input_file_path = os.path.join(self.data_dir, file)
        template_file = os.path.join(self.data_dir, 'darpa_template_blank.xlsx')
        output_doc = tool.convert_part_library(template_file=template_file, input_excel=input_file_path)
        self.assertTrue(output_doc)

        dna_parts = output_doc.componentDefinitions
        self.assertEqual(5, len(dna_parts))

    def test_convert_composition_reading(self):
        file = 'darpa_template.xlsx'
        input_file_path = os.path.join(self.data_dir, file)
        template_file = os.path.join(self.data_dir, 'darpa_template_blank.xlsx')
        output_doc = tool.convert_composition_reading(template_file=template_file, input_excel=input_file_path)
        self.assertTrue(output_doc)
