from __future__ import annotations

from pathlib import Path
import pytest

import excel2sbol.validator as validator


HERE = Path(__file__).resolve().parent
WORKBOOK_DIR = HERE / "test_files" / "validator_workbooks"


# Phase 1 = checks that run BEFORE compiler.initialise and can trigger early return
PHASE1_ERROR_CODES = {
    "INIT_SHEET_MISSING",          # NEW
    "SHEET_NOT_IN_INIT",
    "LOOKUP_SHEET_MISSING",
    "SBOL_TERM_MISSING",
    "NAMESPACE_URL_INVALID",
    "TYPE_MISSING",
    "SPLIT_ON_INVALID",
    "COLUMN_DEFS_MALFORMED",
}

PHASE1_WARNING_CODES = {
    "WORKBOOK_SHEET_NOT_IN_INIT",  # NEW
    "MISSING_SHEET",
    "LOOKUP_SHEET_COLUMN_MISSING",
}

# Phase 2 = checks that run AFTER compiler.initialise (only if Phase 1 had no errors)
PHASE2_ERROR_CODES = {"COLUMN_DEF_MISSING_IN_SHEET"}
PHASE2_WARNING_CODES = {"UNDECLARED_COLUMN"}


def _wb(name: str) -> Path:
    p = WORKBOOK_DIR / name
    assert p.exists(), f"Missing workbook file: {p}"
    return p


def _run(path: Path) -> dict:
    return validator.run_sheet_validator(str(path), validate_only=True, echo=False)


def _codes(result: dict) -> tuple[set[str], set[str]]:
    err = {e["code"] for e in result.get("errors", [])}
    warn = {w["code"] for w in result.get("warnings", [])}
    return err, warn


def _debug_dump(result: dict) -> str:
    err, warn = _codes(result)
    return (
        f"ok={result.get('ok')}\n"
        f"errors({len(result.get('errors', []))}): {sorted(err)}\n"
        f"warnings({len(result.get('warnings', []))}): {sorted(warn)}\n"
    )


@pytest.mark.parametrize(
    "filename, expected_code, severity",
    [
        # ---- Phase 1 demos ----
        ("Resources_LOOKUP_SHEET_MISSING.xlsm", "LOOKUP_SHEET_MISSING", "error"),
        ("Resources_SPLIT_ON_INVALID.xlsm", "SPLIT_ON_INVALID", "error"),
        ("Resources_SBOL_TERM_MISSING.xlsm", "SBOL_TERM_MISSING", "error"),
        ("Resources_NAMESPACE_URL_INVALID.xlsm", "NAMESPACE_URL_INVALID", "error"),
        ("Resources_TYPE_MISSING.xlsm", "TYPE_MISSING", "error"),
        ("Resources_SHEET_NOT_IN_INIT.xlsm", "SHEET_NOT_IN_INIT", "error"),

        # NEW: Init ↔ workbook checks
        ("Resources_INIT_SHEET_MISSING.xlsm", "INIT_SHEET_MISSING", "error"),
        ("Resources_WORKBOOK_SHEET_NOT_IN_INIT.xlsm", "WORKBOOK_SHEET_NOT_IN_INIT", "warning"),

        # ---- Phase 2 demos ----
        ("Resources_COLUMN_DEF_MISSING_IN_SHEET.xlsm", "COLUMN_DEF_MISSING_IN_SHEET", "error"),
        ("Resources_UNDECLARED_COLUMN.xlsm", "UNDECLARED_COLUMN", "warning"),
    ],
)
def test_validator_expected_code_present(filename: str, expected_code: str, severity: str) -> None:
    """
    Each workbook should demonstrate the expected validation code.

    NOTE: validator returns early if Phase 1 has any errors.
    Therefore Phase 2 codes require Phase 1 to be clean.
    """
    path = _wb(filename)
    result = _run(path)
    err_codes, warn_codes = _codes(result)

    # If expecting a Phase 2 code, enforce Phase 1 has no errors so Phase 2 actually ran.
    if expected_code in PHASE2_ERROR_CODES or expected_code in PHASE2_WARNING_CODES:
        phase1_errs = err_codes.intersection(PHASE1_ERROR_CODES)
        assert not phase1_errs, (
            "Workbook has Phase 1 errors, so validator returns early and Phase 2 checks won't run.\n"
            f"Phase1 errors present: {sorted(phase1_errs)}\n"
            f"{_debug_dump(result)}"
        )

    if severity == "error":
        assert expected_code in err_codes, (
            f"Expected ERROR code '{expected_code}' not found.\n{_debug_dump(result)}"
        )
    else:
        assert expected_code in warn_codes, (
            f"Expected WARNING code '{expected_code}' not found.\n{_debug_dump(result)}"
        )


def test_undeclared_column_is_warning_only() -> None:
    """
    Strict expectation for the UNDECLARED_COLUMN demo workbook:
    - must include UNDECLARED_COLUMN warning
    - must have 0 errors (so ok=True)
    """
    path = _wb("Resources_UNDECLARED_COLUMN.xlsm")
    result = _run(path)
    err_codes, warn_codes = _codes(result)

    assert "UNDECLARED_COLUMN" in warn_codes, (
        f"Expected UNDECLARED_COLUMN warning.\n{_debug_dump(result)}"
    )
    assert len(result.get("errors", [])) == 0, (
        f"Expected no errors for the UNDECLARED_COLUMN workbook.\n{_debug_dump(result)}"
    )
    assert result.get("ok") is True, (
        f"Expected ok=True when there are no errors.\n{_debug_dump(result)}"
    )