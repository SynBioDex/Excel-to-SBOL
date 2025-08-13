# uncomment to update converter tests


from unittest import TestCase
import pytest
import excel2sbol.converter as confun
import excel2sbol.compiler as e2s
import os
import tempfile
import rdflib
import rdflib.compare
import openpyxl
import sbol3
import requests

TESTFILE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_files')

def test_conversion_file1():
    sbol3.set_namespace('http://examples.org')
    excel_path = os.path.join(TESTFILE_DIR, 'ACS_SBOL2_simple_and_composite_parts_template.xlsx')
    output_path = './test.xml'
    reference_path = os.path.join(TESTFILE_DIR, 'ACS_sbol_parts.xml')

    try:
        # Run the conversion
        confun(file_path_in=excel_path, file_path_out=output_path)  # homespace=homespace

        print('working tests')

        file = open(reference_path).read()
        comp_file = open(output_path).read()
        request = {
            'options': {
                'language': 'SBOL2',
                'test_equality': True,
                'check_uri_compliance': False,
                'check_completeness': False,
                'check_best_practices': False,
                'fail_on_first_error': False,
                'provide_detailed_stack_trace': False,
                'subset_uri': '',
                'uri_prefix': '',
                'version': '',
                'insert_type': False,
                'main_file_name': 'main file',
                'diff_file_name': 'comparison file',
            },
            'return_file': True,
            'main_file': file,
            'diff_file': comp_file
        }
        resp = requests.post("https://validator.sbolstandard.org/validate/", json=request)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("check_equality") is True, f"Files are not equal: {data}"

    finally:
        # Always remove the created file after the test
        if os.path.exists(output_path):
            os.remove(output_path)

def test_conversion_file2():
    sbol3.set_namespace('http://examples.org')
    excel_path = os.path.join(TESTFILE_DIR, 'Excel2SBOL_Murray_Parts.xlsm')
    output_path = './murray_test.xml'
    reference_path = os.path.join(TESTFILE_DIR, 'Excel2SBOL_Murray_Parts.xml')

    try:
        # Run the conversion
        confun(file_path_in=excel_path, file_path_out=output_path)  # homespace=homespace

        print('working tests')

        file = open(reference_path).read()
        comp_file = open(output_path).read()
        request = {
            'options': {
                'language': 'SBOL2',
                'test_equality': True,
                'check_uri_compliance': False,
                'check_completeness': False,
                'check_best_practices': False,
                'fail_on_first_error': False,
                'provide_detailed_stack_trace': False,
                'subset_uri': '',
                'uri_prefix': '',
                'version': '',
                'insert_type': False,
                'main_file_name': 'main file',
                'diff_file_name': 'comparison file',
            },
            'return_file': True,
            'main_file': file,
            'diff_file': comp_file
        }
        resp = requests.post("https://validator.sbolstandard.org/validate/", json=request)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("check_equality") is True, f"Files are not equal: {data}"

    finally:
        # Always remove the created file after the test
        if os.path.exists(output_path):
            os.remove(output_path)

def test_conversion_file3():
    sbol3.set_namespace('http://examples.org')
    excel_path = os.path.join(TESTFILE_DIR, 'personalpaper.xlsx')
    output_path = './personalpaper_test.xml'
    reference_path = os.path.join(TESTFILE_DIR, 'personalpaper.xml')

    try:
        # Run the conversion
        confun(file_path_in=excel_path, file_path_out=output_path)  # homespace=homespace

        print('working tests')

        file = open(reference_path).read()
        comp_file = open(output_path).read()
        request = {
            'options': {
                'language': 'SBOL2',
                'test_equality': True,
                'check_uri_compliance': False,
                'check_completeness': False,
                'check_best_practices': False,
                'fail_on_first_error': False,
                'provide_detailed_stack_trace': False,
                'subset_uri': '',
                'uri_prefix': '',
                'version': '',
                'insert_type': False,
                'main_file_name': 'main file',
                'diff_file_name': 'comparison file',
            },
            'return_file': True,
            'main_file': file,
            'diff_file': comp_file
        }
        resp = requests.post("https://validator.sbolstandard.org/validate/", json=request)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("check_equality") is True, f"Files are not equal: {data}"

    finally:
        # Always remove the created file after the test
        if os.path.exists(output_path):
            os.remove(output_path)
            
def test_conversion_file4():
    sbol3.set_namespace('http://examples.org')
    excel_path = os.path.join(TESTFILE_DIR, 'sb2c00521_si_001.xlsx')
    output_path = './paper_test.xml'
    reference_path = os.path.join(TESTFILE_DIR, 'sb2c00521_si_001.xml')

    try:
        # Run the conversion
        confun(file_path_in=excel_path, file_path_out=output_path)  # homespace=homespace

        print('working tests')

        file = open(reference_path).read()
        comp_file = open(output_path).read()
        request = {
            'options': {
                'language': 'SBOL2',
                'test_equality': True,
                'check_uri_compliance': False,
                'check_completeness': False,
                'check_best_practices': False,
                'fail_on_first_error': False,
                'provide_detailed_stack_trace': False,
                'subset_uri': '',
                'uri_prefix': '',
                'version': '',
                'insert_type': False,
                'main_file_name': 'main file',
                'diff_file_name': 'comparison file',
            },
            'return_file': True,
            'main_file': file,
            'diff_file': comp_file
        }
        resp = requests.post("https://validator.sbolstandard.org/validate/", json=request)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("check_equality") is True, f"Files are not equal: {data}"

    finally:
        # Always remove the created file after the test
        if os.path.exists(output_path):
            os.remove(output_path)
def test_conversion_file5():
    sbol3.set_namespace('http://examples.org')
    excel_path = os.path.join(TESTFILE_DIR, 'SBOL2_parts_project.xlsx')
    output_path = './parts_test.xml'
    reference_path = os.path.join(TESTFILE_DIR, 'SBOL2_parts_project.xml')

    try:
        # Run the conversion
        confun(file_path_in=excel_path, file_path_out=output_path)  # homespace=homespace

        print('working tests')

        file = open(reference_path).read()
        comp_file = open(output_path).read()
        request = {
            'options': {
                'language': 'SBOL2',
                'test_equality': True,
                'check_uri_compliance': False,
                'check_completeness': False,
                'check_best_practices': False,
                'fail_on_first_error': False,
                'provide_detailed_stack_trace': False,
                'subset_uri': '',
                'uri_prefix': '',
                'version': '',
                'insert_type': False,
                'main_file_name': 'main file',
                'diff_file_name': 'comparison file',
            },
            'return_file': True,
            'main_file': file,
            'diff_file': comp_file
        }
        resp = requests.post("https://validator.sbolstandard.org/validate/", json=request)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("check_equality") is True, f"Files are not equal: {data}"

    finally:
        # Always remove the created file after the test
        if os.path.exists(output_path):
            os.remove(output_path)

def test_conversion_file6():
    sbol3.set_namespace('http://examples.org')
    excel_path = os.path.join(TESTFILE_DIR, 'SBOL2_simple_library4.xlsx')
    output_path = './lib4_test.xml'
    reference_path = os.path.join(TESTFILE_DIR, 'sbol_lib4.xml')

    try:
        # Run the conversion
        confun(file_path_in=excel_path, file_path_out=output_path)  # homespace=homespace

        print('working tests')

        file = open(reference_path).read()
        comp_file = open(output_path).read()
        request = {
            'options': {
                'language': 'SBOL2',
                'test_equality': True,
                'check_uri_compliance': False,
                'check_completeness': False,
                'check_best_practices': False,
                'fail_on_first_error': False,
                'provide_detailed_stack_trace': False,
                'subset_uri': '',
                'uri_prefix': '',
                'version': '',
                'insert_type': False,
                'main_file_name': 'main file',
                'diff_file_name': 'comparison file',
            },
            'return_file': True,
            'main_file': file,
            'diff_file': comp_file
        }
        resp = requests.post("https://validator.sbolstandard.org/validate/", json=request)
        resp.raise_for_status()
        data = resp.json()

        assert data.get("check_equality") is True, f"Files are not equal: {data}"

    finally:
        # Always remove the created file after the test
        if os.path.exists(output_path):
            os.remove(output_path)

