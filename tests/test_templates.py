from pathlib import Path

import pytest

from excel2sbol.compiler import initialise, initialise_welcome


TEMPLATES_DIR = Path(__file__).parents[1] / "resources" / "templates"

TEMPLATE_SHEETS = {
    "Base.xlsm": {"welcome", "ontology_terms", "organism_terms"},
    "Resources.xlsm": {"Init", "column_definitions", "chassis", "cds"},
    "SampleDesign.xlsm": {"Init", "column_definitions", "sample design", "supplement"},
    "Strains.xlsm": {"Init", "column_definitions", "strain"},
    "Study.xlsm": {"Init", "column_definitions", "study", "assay", "sample"},
}


@pytest.mark.parametrize("template_name", TEMPLATE_SHEETS)
def test_template_contains_required_sheets(template_name):
    """Ensure every distributed template remains a valid Excel workbook."""
    import openpyxl

    workbook = openpyxl.load_workbook(TEMPLATES_DIR / template_name, read_only=True)

    assert TEMPLATE_SHEETS[template_name].issubset(workbook.sheetnames)


@pytest.mark.parametrize("template_name", sorted(set(TEMPLATE_SHEETS) - {"Base.xlsm"}))
def test_converter_can_read_template_configuration(template_name):
    """Ensure templates can be read by the installed converter package."""
    col_definitions, sheets_to_convert, compiled_sheets, version, _, init_info = initialise(
        TEMPLATES_DIR / template_name
    )

    assert version == 2
    assert sheets_to_convert
    assert set(sheets_to_convert).issubset(compiled_sheets)
    assert not col_definitions.empty
    assert initialise_welcome(init_info, TEMPLATES_DIR / template_name) is not None
