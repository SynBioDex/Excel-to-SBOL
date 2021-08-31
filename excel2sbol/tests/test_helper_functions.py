# run by typing 'pytest' into the terminal
# for more detailed output use 'pytest -v -s'
import pytest
import excel2sbol.helper_functions as hf


class Test_col_to_num:

    @pytest.mark.parametrize(
        'col_name, raising_err, expected', [
            ("A", False, 0),
            ("a", False, 0),
            ("aa", False, 26),
            ("AA", False, 26),
            ("B", False, 1),
            ("Not a column", True, ValueError),
            ("LONG", True, ValueError),
            (3, True, TypeError)
        ]
    )
    def test_col_to_num(self, col_name, raising_err, expected):
        if raising_err:
            with pytest.raises(expected):
                hf.col_to_num(col_name)
        else:
            assert hf.col_to_num(col_name) == expected


class Test_check_name:

    @pytest.mark.parametrize(
        'nm_to_chck, raising_err, expected', [
            ("testname", False, "testname"),
            ("test_name", False, "test_name"),
            ("_test_name", False, "_test_name"),
            ("test_name12", False, "test_name12"),
            ("12test_name", False, "_12test_name"),
            ("test_name%", False, "test_name_u37_"),
            ("test_näme", False, "test_n_u228_me"),
            ("tεst_name", False, "t_u949_st_name"),
            (576, True, TypeError)
        ]
    )
    def test_check_name(self, nm_to_chck, raising_err, expected):
        if raising_err:
            with pytest.raises(expected):
                hf.check_name(nm_to_chck)
        else:
            assert hf.check_name(nm_to_chck) == expected


class Test_truthy_strings:
    @pytest.mark.parametrize(
        'to_chck, raising_err, expected', [
            ("True", False, True),
            ("TRUE", False, True),
            ("true", False, True),
            ("tRue", False, True),
            (True, False, True),
            ("False", False, False),
            ("FALSE", False, False),
            ("false", False, False),
            ("fAlse", False, False),
            (False, False, False),
            (576, True, TypeError),
            ("something", True, TypeError),
            ("1RUE", True, TypeError)
        ]
    )
    def test_check_name(self, to_chck, raising_err, expected):
        if raising_err:
            with pytest.raises(expected):
                hf.truthy_strings(to_chck)
        else:
            assert hf.truthy_strings(to_chck) == expected
