from unittest import TestCase
import pytest
import excel2sbol.converter as confun
import excel2sbol.compiler_test as e2s
import os
import tempfile
import rdflib
import rdflib.compare
import openpyxl
import sbol3

TESTFILE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_files')

def test_conversion():
    sbol3.set_namespace('http://examples.org')

    # Convert the document into a temporary file
    # From that file have a document read the file
    # Use that document to test

    file_path_in = os.path.join(TESTFILE_DIR, 'simple_library2.xlsx')

    with tempfile.TemporaryDirectory() as dirpath:
        file_path_out = os.path.join(dirpath, 'sample_out.xml')
        confun.converter(file_path_in, file_path_out, 3)

        doc = sbol3.Document()
        doc.read(file_path_out)

        # assert not doc.validate().errors
        assert len(doc.find('Composite_u32_Parts').members) == 6
        assert len(doc.find('Basic_u32_Parts').members) == 26
        # assert len(doc.find('LinearDNAProducts').members) == 37
        # assert len(doc.find('FinalProducts').members) == 24

        # Holistic test here
        expected = os.path.join(TESTFILE_DIR,
                                    'sample_out.xml')
        expected_graph = rdflib.Graph()
        expected_graph.parse(expected)
        expected_iso = rdflib.compare.to_isomorphic(expected_graph)
        output_graph = rdflib.Graph()
        output_graph.parse(file_path_out)
        output_iso = rdflib.compare.to_isomorphic(output_graph)

        assert output_iso.__eq__(expected_iso)

