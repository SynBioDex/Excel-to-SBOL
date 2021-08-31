import pytest
import excel2sbol.initialise_functions as initf
import excel2sbol.column_functions as cf
import json
import os


file_dir = os.path.dirname(__file__)
test_files_path = os.path.join(file_dir, 'test_files')


@pytest.mark.parametrize(
    'column_read_dict, raising_err, expected', [
        (
            {"Col1": {"test1": 1, "test2": 2},
             "Col2": {"test1": 3, "test2": 4}},
            False, {"Col1": "class_object_substitute",
                    "Col2": "class_object_substitute"}
        ),
        (
            {"Col1": {"test1": 1, "test2": 2}},
            False, {"Col1": "class_object_substitute"}
        ),
        (
            "random string",
            True, TypeError
        )
    ]
)
def test_table(column_read_dict, raising_err, expected, monkeypatch):
    def fake_column(file_path_in, column_dict_entry):
        return "class_object_substitute"
    monkeypatch.setattr(cf, 'column', fake_column)

    if raising_err:
        with pytest.raises(expected):
            initf.table('table_doc_path', column_read_dict)
    else:
        tbl_out_put = initf.table('table_doc_path', column_read_dict)
        assert tbl_out_put.column_list == expected


@pytest.mark.parametrize(
    'templt_name, template_dict, file_path_in, raising_err, expected1, expected2, expected3, expected4', [
        (
            'test_temp.xlsx',
            {"test_temp.xlsx": {"library_start_row": 18,
                                "sheet_name": "Test1",
                                "number_of_collection_rows": 8,
                                "collection_columns": [0, 1],
                                "description_start_row": 10,
                                "description_columns": [0]
                                }
             },
            os.path.join(test_files_path, 'read_in_test.xlsx'),
            False,
            {
                0: {'A19': 'A20', 'B19': 'B20', 'C19': 'C20', 'D19': 'D20', 'E19': 'E20', 'F19': 'F20'},
                1: {'A19': 'A21', 'B19': 'B21', 'C19': 'C21', 'D19': 'D21', 'E19': 'E21', 'F19': 'F21'},
                2: {'A19': 'A22', 'B19': 'B22', 'C19': 'C22', 'D19': 'D22', 'E19': 'E22', 'F19': 'F22'},
                3: {'A19': 'A23', 'B19': 'B23', 'C19': 'C23', 'D19': 'D23', 'E19': 'E23', 'F19': 'F23'},
                4: {'A19': 'A24', 'B19': 'B24', 'C19': 'C24', 'D19': 'D24', 'E19': 'E24', 'F19': 'F24'},
                5: {'A19': 'A25', 'B19': 'B25', 'C19': 'C25', 'D19': 'D25', 'E19': 'E25', 'F19': 'F25'},
                6: {'A19': 'A26', 'B19': 'B26', 'C19': 'C26', 'D19': 'D26', 'E19': 'E26', 'F19': 'F26'},
                7: {'A19': 'A27', 'B19': 'B27', 'C19': 'C27', 'D19': 'D27', 'E19': 'E27', 'F19': 'F27'},
                8: {'A19': 'A28', 'B19': 'B28', 'C19': 'C28', 'D19': 'D28', 'E19': 'E28', 'F19': 'F28'},
                9: {'A19': 'A29', 'B19': 'B29', 'C19': 'C29', 'D19': 'D29', 'E19': 'E29', 'F19': 'F29'},
                10: {'A19': 'A30', 'B19': 'B30', 'C19': 'C30', 'D19': 'D30', 'E19': 'E30', 'F19': 'F30'},
                11: {'A19': 'A31', 'B19': 'B31', 'C19': 'C31', 'D19': 'D31', 'E19': 'E31', 'F19': 'F31'},
                12: {'A19': 'A32', 'B19': 'B32', 'C19': 'C32', 'D19': 'D32', 'E19': 'E32', 'F19': 'F32'},
                13: {'A19': 'A33', 'B19': 'B33', 'C19': 'C33', 'D19': 'D33', 'E19': 'E33', 'F19': 'F33'},
            }, 'A11',
            {
                'A1': {1: 'B1'}, 'A2': {1: 'B2'}, 'A3': {1: 'B3'},
                'A4': {1: 'B4'}, 'A5': {1: 'B5'}, 'A6': {1: 'B6'},
                'A7': {1: 'B7'}, 'A8': {1: 'B8'}
            },
            {
                'Col_def A2': {'Col_def B1': 'Col_def B2',
                               'Col_def C1': 'Col_def C2',
                               'Col_def D1': 'Col_def D2',
                               'Col_def E1': 'Col_def E2',
                               'Col_def F1': 'Col_def F2'},
                'Col_def A3': {'Col_def B1': 'Col_def B3',
                               'Col_def C1': 'Col_def C3',
                               'Col_def D1': 'Col_def D3',
                               'Col_def E1': 'Col_def E3',
                               'Col_def F1': 'Col_def F3'},
                'Col_def A4': {'Col_def B1': 'Col_def B4',
                               'Col_def C1': 'Col_def C4',
                               'Col_def D1': 'Col_def D4',
                               'Col_def E1': 'Col_def E4',
                               'Col_def F1': 'Col_def F4'},
                'Col_def A5': {'Col_def B1': 'Col_def B5',
                               'Col_def C1': 'Col_def C5',
                               'Col_def D1': 'Col_def D5',
                               'Col_def E1': 'Col_def E5',
                               'Col_def F1': 'Col_def F5'},
                'Col_def A6': {'Col_def B1': 'Col_def B6',
                               'Col_def C1': 'Col_def C6',
                               'Col_def D1': 'Col_def D6',
                               'Col_def E1': 'Col_def E6',
                               'Col_def F1': 'Col_def F6'},
                'Col_def A7': {'Col_def B1': 'Col_def B7',
                               'Col_def C1': 'Col_def C7',
                               'Col_def D1': 'Col_def D7',
                               'Col_def E1': 'Col_def E7',
                               'Col_def F1': 'Col_def F7'},
                'Col_def A8': {'Col_def B1': 'Col_def B8',
                               'Col_def C1': 'Col_def C8',
                               'Col_def D1': 'Col_def D8',
                               'Col_def E1': 'Col_def E8',
                               'Col_def F1': 'Col_def F8'},
                'Col_def A9': {'Col_def B1': 'Col_def B9',
                               'Col_def C1': 'Col_def C9',
                               'Col_def D1': 'Col_def D9',
                               'Col_def E1': 'Col_def E9',
                               'Col_def F1': 'Col_def F9'},
                'Col_def A10': {'Col_def B1': 'Col_def B10',
                                'Col_def C1': 'Col_def C10',
                                'Col_def D1': 'Col_def D10',
                                'Col_def E1': 'Col_def E10',
                                'Col_def F1': 'Col_def F10'},
            }
        ),
        (
            'test_temp.xlsx',
            {"test_temp.xlsx": {"library_start_row": 18,
                                "sheet_name": "Test 2",
                                "number_of_collection_rows": 8,
                                "collection_columns": [0, 1],
                                "description_start_row": 10,
                                "description_columns": [0]
                                }
             },
            os.path.join(test_files_path, 'read_in_test.xlsx'),
            False,
            {
                0: {'A19': 'A20', 'B19': 'B20', 'C19': 'C20', 'D19': 'D20', 'E19': 'E20', 'F19': 'F20'},
                1: {'A19': 'A21', 'B19': 'B21', 'C19': 'C21', 'D19': 'D21', 'E19': 'E21', 'F19': 'F21'},
                2: {'A19': 'A22', 'B19': 'B22', 'C19': 'C22', 'D19': 'D22', 'E19': 'E22', 'F19': 'F22'},
                3: {'A19': 'A23', 'B19': 'B23', 'C19': 'C23', 'D19': 'D23', 'E19': 'E23', 'F19': 'F23'},
                4: {'A19': 'A24', 'B19': 'B24', 'C19': 'C24', 'D19': 'D24', 'E19': 'E24', 'F19': 'F24'},
                5: {'A19': 'A25', 'B19': 'B25', 'C19': 'C25', 'D19': 'D25', 'E19': 'E25', 'F19': 'F25'},
                6: {'A19': 'A26', 'B19': 'B26', 'C19': 'C26', 'D19': 'D26', 'E19': 'E26', 'F19': 'F26'},
                7: {'A19': 'A27', 'B19': 'B27', 'C19': 'C27', 'D19': 'D27', 'E19': 'E27', 'F19': 'F27'},
                8: {'A19': 'A28', 'B19': 'B28', 'C19': 'C28', 'D19': 'D28', 'E19': 'E28', 'F19': 'F28'},
                9: {'A19': 'A29', 'B19': 'B29', 'C19': 'C29', 'D19': 'D29', 'E19': 'E29', 'F19': 'F29'},
                10: {'A19': 'A30', 'B19': 'B30', 'C19': 'C30', 'D19': 'D30', 'E19': 'E30', 'F19': 'F30'},
                11: {'A19': 'A31', 'B19': 'B31', 'C19': 'C31', 'D19': 'D31', 'E19': 'E31', 'F19': 'F31'},
                12: {'A19': 'A32', 'B19': 'B32', 'C19': 'C32', 'D19': 'D32', 'E19': 'E32', 'F19': 'F32'},
                13: {'A19': 'A33', 'B19': 'B33', 'C19': 'C33', 'D19': 'D33', 'E19': 'E33', 'F19': 'F33'},
            }, 'Merged A11 to F11',
            {
                'A1': {1: 'B1'}, 'A2': {1: 'B2'}, 'A3': {1: 'B3'},
                'A4': {1: 'B4'}, 'A5': {1: 'B5'}, 'A6': {1: 'B6'},
                'A7': {1: 'B7'}, 'A8': {1: 'B8'}
            },
            {
                'Col_def A2': {'Col_def B1': 'Col_def B2',
                               'Col_def C1': 'Col_def C2',
                               'Col_def D1': 'Col_def D2',
                               'Col_def E1': 'Col_def E2',
                               'Col_def F1': 'Col_def F2'},
                'Col_def A3': {'Col_def B1': 'Col_def B3',
                               'Col_def C1': 'Col_def C3',
                               'Col_def D1': 'Col_def D3',
                               'Col_def E1': 'Col_def E3',
                               'Col_def F1': 'Col_def F3'},
                'Col_def A4': {'Col_def B1': 'Col_def B4',
                               'Col_def C1': 'Col_def C4',
                               'Col_def D1': 'Col_def D4',
                               'Col_def E1': 'Col_def E4',
                               'Col_def F1': 'Col_def F4'},
                'Col_def A5': {'Col_def B1': 'Col_def B5',
                               'Col_def C1': 'Col_def C5',
                               'Col_def D1': 'Col_def D5',
                               'Col_def E1': 'Col_def E5',
                               'Col_def F1': 'Col_def F5'},
                'Col_def A6': {'Col_def B1': 'Col_def B6',
                               'Col_def C1': 'Col_def C6',
                               'Col_def D1': 'Col_def D6',
                               'Col_def E1': 'Col_def E6',
                               'Col_def F1': 'Col_def F6'},
                'Col_def A7': {'Col_def B1': 'Col_def B7',
                               'Col_def C1': 'Col_def C7',
                               'Col_def D1': 'Col_def D7',
                               'Col_def E1': 'Col_def E7',
                               'Col_def F1': 'Col_def F7'},
                'Col_def A8': {'Col_def B1': 'Col_def B8',
                               'Col_def C1': 'Col_def C8',
                               'Col_def D1': 'Col_def D8',
                               'Col_def E1': 'Col_def E8',
                               'Col_def F1': 'Col_def F8'},
                'Col_def A9': {'Col_def B1': 'Col_def B9',
                               'Col_def C1': 'Col_def C9',
                               'Col_def D1': 'Col_def D9',
                               'Col_def E1': 'Col_def E9',
                               'Col_def F1': 'Col_def F9'},
                'Col_def A10': {'Col_def B1': 'Col_def B10',
                                'Col_def C1': 'Col_def C10',
                                'Col_def D1': 'Col_def D10',
                                'Col_def E1': 'Col_def E10',
                                'Col_def F1': 'Col_def F10'},
            }
        ),
        (
            'test_temp.xlsx',
            {"test_temp.xlsx": {"library_start_row": 29,
                                "sheet_name": "Test3",
                                "number_of_collection_rows": 3,
                                "collection_columns": [3, 4],
                                "description_start_row": 0,
                                "description_columns": [1]
                                }
             },
            os.path.join(test_files_path, 'read_in_test.xlsx'),
            False,
            {
                0: {'A30': 'A31', 'B30': 'B31', 'C30': 'C31', 'D30': 'D31', 'E30': 'E31', 'F30': 'F31'},
                1: {'A30': 'A32', 'B30': 'B32', 'C30': 'C32', 'D30': 'D32', 'E30': 'E32', 'F30': 'F32'},
                2: {'A30': 'A33', 'B30': 'B33', 'C30': 'C33', 'D30': 'D33', 'E30': 'E33', 'F30': 'F33'},
            }, 'B1',
            {
                'D1': {4: 'E1'}, 'D2': {4: 'E2'}, 'D3': {4: 'E3'}
            },
            {
                'Col_def A2': {'Col_def B1': 'Col_def B2',
                               'Col_def C1': 'Col_def C2',
                               'Col_def D1': 'Col_def D2',
                               'Col_def E1': 'Col_def E2',
                               'Col_def F1': 'Col_def F2'},
                'Col_def A3': {'Col_def B1': 'Col_def B3',
                               'Col_def C1': 'Col_def C3',
                               'Col_def D1': 'Col_def D3',
                               'Col_def E1': 'Col_def E3',
                               'Col_def F1': 'Col_def F3'},
                'Col_def A4': {'Col_def B1': 'Col_def B4',
                               'Col_def C1': 'Col_def C4',
                               'Col_def D1': 'Col_def D4',
                               'Col_def E1': 'Col_def E4',
                               'Col_def F1': 'Col_def F4'},
                'Col_def A5': {'Col_def B1': 'Col_def B5',
                               'Col_def C1': 'Col_def C5',
                               'Col_def D1': 'Col_def D5',
                               'Col_def E1': 'Col_def E5',
                               'Col_def F1': 'Col_def F5'},
                'Col_def A6': {'Col_def B1': 'Col_def B6',
                               'Col_def C1': 'Col_def C6',
                               'Col_def D1': 'Col_def D6',
                               'Col_def E1': 'Col_def E6',
                               'Col_def F1': 'Col_def F6'},
                'Col_def A7': {'Col_def B1': 'Col_def B7',
                               'Col_def C1': 'Col_def C7',
                               'Col_def D1': 'Col_def D7',
                               'Col_def E1': 'Col_def E7',
                               'Col_def F1': 'Col_def F7'},
                'Col_def A8': {'Col_def B1': 'Col_def B8',
                               'Col_def C1': 'Col_def C8',
                               'Col_def D1': 'Col_def D8',
                               'Col_def E1': 'Col_def E8',
                               'Col_def F1': 'Col_def F8'},
                'Col_def A9': {'Col_def B1': 'Col_def B9',
                               'Col_def C1': 'Col_def C9',
                               'Col_def D1': 'Col_def D9',
                               'Col_def E1': 'Col_def E9',
                               'Col_def F1': 'Col_def F9'},
                'Col_def A10': {'Col_def B1': 'Col_def B10',
                                'Col_def C1': 'Col_def C10',
                                'Col_def D1': 'Col_def D10',
                                'Col_def E1': 'Col_def E10',
                                'Col_def F1': 'Col_def F10'},
            }
        ),
    ]
)
def test_read_in_sheet(templt_name, template_dict, file_path_in, raising_err,
                       expected1, expected2, expected3, expected4, monkeypatch):
    def fake_loads(return_object):
        return template_dict
    monkeypatch.setattr(json, 'loads', fake_loads)

    if raising_err:
        with pytest.raises(expected1):
            initf.read_in_sheet(templt_name, file_path_in)
    else:
        column_read_dict, sheet_dict, description_info, collection_info = initf.read_in_sheet(templt_name, file_path_in)
        assert sheet_dict == expected1
        assert description_info == expected2
        assert collection_info == expected3
        assert column_read_dict == expected4
