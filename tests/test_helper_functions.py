# run by typing 'pytest' into the terminal
# for more detailed output use 'pytest -v -s'

import pytest
import excel2sbol.helpers as hf


class Test_check_name_blank_and_edge_cases:
    """Active tests covering blank-id and edge-case inputs for check_name().

    These cases were identified as untested validation gaps: blank strings
    pass through check_name() unchanged and can reach object creation with
    an empty display id, which is a confirmed bug in the pipeline.
    """

    @pytest.mark.parametrize(
        'nm_to_chck, expected', [
            ("", ""),                        # blank string passes through unchanged
            ("testname", "testname"),        # normal name is unchanged
            ("12test", "_12test"),           # leading digit gets prefix
            ("test%name", "test_u37_name"),  # percent sign encoded
            ("test name", "test_name"),      # space becomes underscore
            ("test-name", "test_name"),      # hyphen becomes underscore
            ("test.name", "test_name"),      # dot becomes underscore
        ]
    )
    def test_check_name_returns_expected(self, nm_to_chck, expected):
        assert hf.check_name(nm_to_chck) == expected

    def test_blank_string_returns_empty(self):
        """Blank display id normalizes to empty string - callers must reject it."""
        result = hf.check_name("")
        assert result == "", (
            "check_name('') must return '' so callers can detect and reject blank ids "
            "before object creation."
        )

    def test_non_string_raises_type_error(self):
        """Non-string inputs (e.g. bare integers) must raise TypeError."""
        with pytest.raises(TypeError):
            hf.check_name(576)


# uncomment when you want to update the converter tests
'''
import pytest
import excel2sbol.helpers as hf


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
'''