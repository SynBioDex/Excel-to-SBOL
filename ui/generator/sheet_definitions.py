"""
sheet_definitions.py: single source of truth for all sheet types.

Every ColumnDef and SheetDef instance here drives:
  - column headers written to generated workbooks
  - column_definitions rows consumed by the converter
  - Init rows consumed by the converter
  - _DropdownMap rows written for VBA HeaderDropdowns
  - tooltip comments placed on header cells
"""

from dataclasses import dataclass, field
from typing import Optional

# ── Namespace constants ───────────────────────────────────────────────────────

NS_SBOLS = "http://sbols.org/v2#"
NS_DC    = "http://purl.org/dc/terms/#"
NS_OBO   = "http://purl.obolibrary.org/obo/"
NS_SBH   = "https://wiki.synbiohub.org/wiki/Terms/synbiohub#"
NS_FJ    = "https://wiki.synbiohub.org/wiki/Terms/Flapjack#"
NS_ISA   = "http://isa-tools.org/ns/"
NS_EDAM  = "http://edamontology.org/"
NS_NA    = "Not_applicable"


# ── Dataclasses ───────────────────────────────────────────────────────────────

@dataclass
class ColumnDef:
    name: str
    tooltip: str
    sbol_term: str
    namespace: str
    col_type: str                     # "String", "URI", or "Not_applicable"
    split_on: str = '""'
    pattern: Optional[str] = None
    tyto_lookup: bool = False
    sheet_lookup: bool = False
    replacement_lookup: bool = False
    object_id_lookup: bool = False
    parent_lookup: bool = False
    lookup_sheet: Optional[str] = None  # MUST be a snake_case tab name in the workbook
    from_col: Optional[str] = None
    to_col: Optional[str] = None
    ontology_name: Optional[str] = None
    comma_append: bool = False        # VBA only: append with ", " instead of replace
    translate_target: Optional[str] = None  # VBA only: destination sheet for translator


@dataclass
class SheetDef:
    name: str                         # tab name, lowercase
    display_name: str                 # column header prefix (e.g. "CDS", "ncRNA")
    sbol_object_type: str             # e.g. "ComponentDefinition" or "" for Flapjack-only
    molecule_type: str                # e.g. "DNARegion" or ""
    role: str                         # e.g. "promoter" or ""
    flapjack_object: Optional[str]    # Flapjack API type, None if not Flapjack-targeted
    sbh_collections: list             # scaffold sheet names to create
    columns: list                     # list[ColumnDef]
    name_column: Optional[str] = None # header of primary name col; None for Flapjack-only
    ui_group: str = ""                # checkbox group label in the Spreadsheet Creator UI
    ui_hint: str = ""                 # short description shown under the checkbox label
    ui_default_checked: bool = False  # whether the checkbox is pre-checked by default
    ui_selectable: bool = True        # whether to offer this sheet in the custom catalog


# ── Column factories ──────────────────────────────────────────────────────────

def _name_col(display_name: str) -> ColumnDef:
    return ColumnDef(
        name=f"{display_name} Name",
        tooltip=f"The human-readable name for this {display_name.lower()} entry.",
        sbol_term="sbol_name",
        namespace=NS_SBOLS,
        col_type="String",
    )


def _id_col(display_name: str) -> ColumnDef:
    return ColumnDef(
        name=f"{display_name} ID",
        tooltip=(
            f"Unique identifier for this {display_name.lower()} entry. "
            f"This ID is used to reference the {display_name} entries in other sheets "
            f"and must be unique across all sheets in this workbook."
        ),
        sbol_term="sbol_displayId",
        namespace=NS_SBOLS,
        col_type="String",
    )


def _desc_col(display_name: str) -> ColumnDef:
    return ColumnDef(
        name=f"{display_name} Description",
        tooltip=f"A free-text description of this {display_name.lower()} entry.",
        sbol_term="sbol_description",
        namespace=NS_DC,
        col_type="String",
    )


def _prev_version_col() -> ColumnDef:
    return ColumnDef(
        name="Previous Version (URI)",
        tooltip=(
            "URI of the previous version of this part, used to track provenance and "
            "version history. Copy the URI from the part's SynBioHub page."
        ),
        sbol_term="sbol_wasDerivedFrom",
        namespace=NS_SBOLS,
        col_type="URI",
    )


def _data_source_col() -> ColumnDef:
    return ColumnDef(
        name="Data Source",
        tooltip=(
            "URL of the external database or publication where this part's sequence "
            "was originally obtained (e.g. iGEM Registry, NCBI, literature)."
        ),
        sbol_term="sbol_wasDerivedFrom",
        namespace=NS_SBOLS,
        col_type="URI",
    )


def _pubmed_col() -> ColumnDef:
    return ColumnDef(
        name="PubMed ID",
        tooltip=(
            "PubMed identifier of the publication describing this part. "
            "Enter only the numeric ID (e.g. 12345678)."
        ),
        sbol_term="obo_OBI_0001617",
        namespace=NS_OBO,
        col_type="String",
    )


def _doi_col() -> ColumnDef:
    return ColumnDef(
        name="DOI",
        tooltip=(
            "Digital Object Identifier of the publication describing this part "
            "(e.g. https://doi.org/10.1000/xyz123)."
        ),
        sbol_term="sbol_wasDerivedFrom",
        namespace=NS_SBOLS,
        col_type="URI",
    )


def _degrades_col() -> ColumnDef:
    return ColumnDef(
        name="Degrades",
        tooltip=(
            "Whether this entity is subject to degradation. Select TRUE or FALSE "
            "from the dropdown."
        ),
        sbol_term="sbol_degrades",
        namespace=NS_SBOLS,
        col_type="String",
    )


def _source_organism_col() -> ColumnDef:
    return ColumnDef(
        name="Source Organism",
        tooltip=(
            "The organism from which this part was derived. Select from the dropdown "
            "(populated from the organism_terms sheet) or enter an NCBI Taxonomy URI."
        ),
        sbol_term="sbh_sourceOrganism",
        namespace=NS_SBH,
        col_type="URI",
        sheet_lookup=True,
        lookup_sheet="organism_terms",
        from_col="A",
        to_col="B",
        ontology_name="NCBITaxon",
    )


def _dna_sequence_col() -> ColumnDef:
    return ColumnDef(
        name="Sequence",
        tooltip=(
            "The DNA sequence of this part in IUPAC notation (A, T, C, G). "
            "Only include the coding strand."
        ),
        sbol_term="sbol_sequence",
        namespace=NS_SBOLS,
        col_type="String",
    )


def _rna_sequence_col() -> ColumnDef:
    return ColumnDef(
        name="Sequence",
        tooltip=(
            "The RNA sequence (A, U, C, G). "
            "Enter using DNA notation (T instead of U); T→U conversion is applied automatically."
        ),
        sbol_term="sbol_sequence",
        namespace=NS_SBOLS,
        col_type="String",
    )


def _protein_sequence_col() -> ColumnDef:
    return ColumnDef(
        name="Sequence",
        tooltip="The amino acid sequence of this protein in single-letter IUPAC notation.",
        sbol_term="sbol_proteinSequence",
        namespace=NS_SBOLS,
        col_type="String",
    )


def _length_col(unit: str) -> ColumnDef:
    return ColumnDef(
        name=f"Length ({unit})",
        tooltip=f"Length of the sequence in {unit}. Calculated automatically from the Sequence column.",
        sbol_term=NS_NA,
        namespace=NS_NA,
        col_type="Not_applicable",
    )


def _uri_col() -> ColumnDef:
    return ColumnDef(
        name="URI",
        tooltip="This field is contains the URI for this object on an instance of SynBioHub.",
        sbol_term=NS_NA,
        namespace=NS_NA,
        col_type="Not_applicable",
    )


def _update_col() -> ColumnDef:
    return ColumnDef(
        name="Update",
        tooltip="Select True, if you wish this entry to be processed.  Select False, if this entry is already uploaded to an instance of SynBioHub, and the entry has not been changed.",
        sbol_term=NS_NA,
        namespace=NS_NA,
        col_type="Not_applicable",
    )


def _role_col() -> ColumnDef:
    return ColumnDef(
        name="Role",
        tooltip=(
            "Sequence Ontology (SO) role for this part. Select from the dropdown "
            "(populated from the ontology_terms sheet)."
        ),
        sbol_term="sbol_roles",
        namespace=NS_SBOLS,
        col_type="URI",
        sheet_lookup=True,
        lookup_sheet="ontology_terms",
        from_col="A",
        to_col="B",
        ontology_name="SO",
    )


def _activators_col() -> ColumnDef:
    return ColumnDef(
        name="Activators",
        tooltip=(
            "The ID(s) of the components activated by this promoter. "
            "Double-click the cell to open the selector and choose one or more values."
        ),
        sbol_term="sbol_activator",
        namespace=NS_SBH,
        col_type="URI",
        # Resolve entered component IDs to their local object URIs and split on
        # commas for multiple values. comma_append is the VBA input-append flag.
        object_id_lookup=True,
        split_on='","',
        comma_append=True,
    )


def _repressors_col() -> ColumnDef:
    return ColumnDef(
        name="Repressors",
        tooltip=(
            "The ID(s) of the components repressed by this promoter. "
            "Double-click the cell to open the selector and choose one or more values."
        ),
        sbol_term="sbol_repressor",
        namespace=NS_SBH,
        col_type="URI",
        # Resolve entered component IDs to their local object URIs and split on
        # commas for multiple values. comma_append is the VBA input-append flag.
        object_id_lookup=True,
        split_on='","',
        comma_append=True,
    )


def _encodes_for_cds_col() -> ColumnDef:
    return ColumnDef(
        name="Encodes for",
        tooltip=(
            "The protein encoded by this CDS. Enter the Protein ID of the corresponding "
            "protein entry, or use the 'Translate to Protein' button to populate automatically."
        ),
        sbol_term="sbol_encodesFor",
        namespace=NS_SBH,
        col_type="URI",
        # Resolve the entered Protein ID to its local object URI so the
        # encodesFor genetic-production interaction links the real protein.
        object_id_lookup=True,
    )


def _encodes_for_ncrna_col() -> ColumnDef:
    return ColumnDef(
        name="Encodes for",
        tooltip=(
            "The RNA transcribed from this ncRNA. Enter the RNA ID of the corresponding "
            "RNA entry, or use the 'Translate to RNA' button to populate automatically."
        ),
        sbol_term="sbol_encodesFor",
        namespace=NS_SBH,
        col_type="URI",
        # Resolve the entered RNA ID to its local object URI so the
        # encodesFor interaction links the real RNA object.
        object_id_lookup=True,
    )


def _translate_to_protein_col() -> ColumnDef:
    return ColumnDef(
        name="Translate to Protein",
        tooltip=(
            "Check this box to automatically translate this CDS DNA sequence to a protein "
            "sequence using the longest open reading frame (forward strand) and add the "
            "result to the Protein sheet."
        ),
        sbol_term=NS_NA,
        namespace=NS_NA,
        col_type="Not_applicable",
        translate_target="protein",
    )


def _translate_to_rna_col() -> ColumnDef:
    return ColumnDef(
        name="Translate to RNA",
        tooltip=(
            "Check this box to automatically convert this ncRNA DNA sequence to an RNA "
            "sequence (T→U substitution) and add the result to the RNA sheet."
        ),
        sbol_term=NS_NA,
        namespace=NS_NA,
        col_type="Not_applicable",
        translate_target="rna",
    )


def _signal_color_col() -> ColumnDef:
    return ColumnDef(
        name="Signal Color",
        tooltip=(
            "Hex color code used to represent this signal in Flapjack visualizations "
            "(e.g. #FF0000 for red). Must be a valid 6-digit hex color prefixed with #."
        ),
        sbol_term="fj_color",
        namespace=NS_FJ,
        col_type="String",
    )


def _components_ids_col() -> ColumnDef:
    return ColumnDef(
        name="Components IDs",
        tooltip=(
            "The ID(s) of the sub-components that make up this complex. "
            "Double-click the cell to open the selector and choose one or more values."
        ),
        sbol_term="sbol_complexComponent",
        namespace=NS_SBOLS,
        col_type="URI",
        # Resolve entered sub-component IDs to their local object URIs and split
        # on commas for multiple values. comma_append is the VBA input-append flag.
        object_id_lookup=True,
        split_on='","',
        comma_append=True,
    )


# ── Standard column block helpers ────────────────────────────────────────────

def _bio_tail_cols() -> list:
    """Hook for trailing columns shared by every part sheet; currently none."""
    return []


def _bio_base_cols(dn: str) -> list:
    """Name, ID, Previous Version (URI), Description."""
    return [_name_col(dn), _id_col(dn), _prev_version_col(), _desc_col(dn)]


def _provenance_cols() -> list:
    """Data Source, PubMed ID, DOI."""
    return [_data_source_col(), _pubmed_col(), _doi_col()]


# ── Sheet instances ───────────────────────────────────────────────────────────

PROMOTER = SheetDef(
    name="promoter",
    display_name="Promoter",
    sbol_object_type="ComponentDefinition",
    molecule_type="DNARegion",
    role="promoter",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Promoter Name",
    ui_group="DNA Parts",
    ui_hint="",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("Promoter")
        + _provenance_cols()
        + [_source_organism_col(), _activators_col(), _repressors_col(), _length_col("bp"), _dna_sequence_col()]
        + _bio_tail_cols()
    ),
)

RBS = SheetDef(
    name="rbs",
    display_name="RBS",
    sbol_object_type="ComponentDefinition",
    molecule_type="DNARegion",
    role="ribosome_entry_site",
    flapjack_object=None,
    sbh_collections=[],
    name_column="RBS Name",
    ui_group="DNA Parts",
    ui_hint="Ribosome Binding Site",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("RBS")
        + _provenance_cols()
        + [_source_organism_col(), _length_col("bp"), _dna_sequence_col()]
        + _bio_tail_cols()
    ),
)

CDS = SheetDef(
    name="cds",
    display_name="CDS",
    sbol_object_type="ComponentDefinition",
    molecule_type="DNARegion",
    role="CDS",
    flapjack_object=None,
    sbh_collections=[],
    name_column="CDS Name",
    ui_group="DNA Parts",
    ui_hint="Coding Sequence",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("CDS")
        + _provenance_cols()
        + [_source_organism_col(), _encodes_for_cds_col(), _length_col("bp"), _dna_sequence_col(), _translate_to_protein_col()]
        + _bio_tail_cols()
    ),
)

TERMINATOR = SheetDef(
    name="terminator",
    display_name="Terminator",
    sbol_object_type="ComponentDefinition",
    molecule_type="DNARegion",
    role="terminator",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Terminator Name",
    ui_group="DNA Parts",
    ui_hint="",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("Terminator")
        + _provenance_cols()
        + [_source_organism_col(), _length_col("bp"), _dna_sequence_col()]
        + _bio_tail_cols()
    ),
)

OTHER = SheetDef(
    name="other",
    display_name="Part",
    sbol_object_type="ComponentDefinition",
    molecule_type="DNARegion",
    role="",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Part Name",
    ui_group="DNA Parts",
    ui_hint="Catch-all for undefined part types",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("Part")
        + [_role_col()]
        + _provenance_cols()
        + [_source_organism_col(), _length_col("bp"), _dna_sequence_col()]
        + _bio_tail_cols()
    ),
)

NCRNA = SheetDef(
    name="ncrna",
    display_name="ncRNA",
    sbol_object_type="ComponentDefinition",
    molecule_type="RNA",
    role="RNA",
    flapjack_object=None,
    sbh_collections=[],
    name_column="ncRNA Name",
    ui_group="RNA & Protein",
    ui_hint="Non-coding RNA",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("ncRNA")
        + _provenance_cols()
        + [_source_organism_col(), _encodes_for_ncrna_col(), _length_col("nt"), _rna_sequence_col(), _translate_to_rna_col()]
        + _bio_tail_cols()
    ),
)

RNA = SheetDef(
    name="rna",
    display_name="RNA",
    sbol_object_type="ComponentDefinition",
    molecule_type="RNA",
    role="",
    flapjack_object=None,
    sbh_collections=[],
    name_column="RNA Name",
    ui_group="RNA & Protein",
    ui_hint="Any RNA transcript",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("RNA")
        + _provenance_cols()
        + [_degrades_col(), _length_col("nt"), _rna_sequence_col()]
        + _bio_tail_cols()
    ),
)

PROTEIN = SheetDef(
    name="protein",
    display_name="Protein",
    sbol_object_type="ComponentDefinition",
    molecule_type="Protein",
    role="",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Protein Name",
    ui_group="RNA & Protein",
    ui_hint="",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("Protein")
        + _provenance_cols()
        + [_degrades_col(), _length_col("aa"), _protein_sequence_col()]
        + _bio_tail_cols()
    ),
)

COMPLEX = SheetDef(
    name="complex",
    display_name="Complex",
    sbol_object_type="ComponentDefinition",
    molecule_type="Complex",
    role="",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Complex Name",
    ui_group="RNA & Protein",
    ui_hint="Protein complex",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("Complex")
        + _provenance_cols()
        + [_components_ids_col(), _degrades_col()]
        + _bio_tail_cols()
    ),
)

SIGNAL = SheetDef(
    name="signal",
    display_name="Signal",
    sbol_object_type="ComponentDefinition",
    molecule_type="",
    role="signal",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Signal Name",
    ui_group="Study",
    ui_hint="Fluorescent / reporter signal",
    ui_default_checked=True,
    ui_selectable=False,  # not offered in the custom catalog; belongs to Study only
    columns=(
        _bio_base_cols("Signal")
        + [_signal_color_col()]
        + _provenance_cols()
        + _bio_tail_cols()
    ),
)

CHASSIS = SheetDef(
    name="chassis",
    display_name="Chassis",
    sbol_object_type="ModuleDefinition",
    molecule_type="",
    role="organism_strain",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Chassis Name",
    ui_group="Experimental Resources",
    ui_hint="Organism / strain",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("Chassis")
        + _provenance_cols()
        + _bio_tail_cols()
    ),
)

MEDIA = SheetDef(
    name="media",
    display_name="Media",
    sbol_object_type="ModuleDefinition",
    molecule_type="",
    role="medium",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Media Name",
    ui_group="Experimental Resources",
    ui_hint="",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("Media")
        + _provenance_cols()
        + _bio_tail_cols()
    ),
)

CHEMICALS = SheetDef(
    name="chemicals",
    display_name="Chemical",
    sbol_object_type="ComponentDefinition",
    molecule_type="SmallMolecule",
    role="",
    flapjack_object=None,
    sbh_collections=[],
    name_column="Chemical Name",
    ui_group="Experimental Resources",
    ui_hint="",
    ui_default_checked=True,
    columns=(
        _bio_base_cols("Chemical")
        + [
            ColumnDef(
                name="PubChem ID",
                tooltip="The PubChem Compound ID (CID) for this chemical.",
                sbol_term="edam_data_2639",
                namespace=NS_EDAM,
                col_type="String",
            ),
        ]
        + _provenance_cols()
        + [_degrades_col()]
        + _bio_tail_cols()
    ),
)

STRAIN = SheetDef(
    name="strain",
    display_name="Strain",
    sbol_object_type="ModuleDefinition",
    molecule_type="",
    # An engineered strain, not the unmodified host; chassis keeps organism_strain.
    role="genetically_modified_organism",
    flapjack_object=None,
    sbh_collections=["SBH_chassis_collections", "SBH_plasmids_collections"],
    name_column="Strain Name",
    ui_group="Strains",
    columns=(
        _bio_base_cols("Strain")
        + [
            ColumnDef(
                name="Chassis",
                tooltip="The chassis organism of this strain. Select from the SBH_chassis_collections dropdown.",
                sbol_term="sbol_module",
                namespace=NS_SBOLS,
                col_type="URI",
                sheet_lookup=True,
                lookup_sheet="SBH_chassis_collections",
                from_col="A",
                to_col="B",
            ),
            ColumnDef(
                name="Plasmids",
                tooltip=("The plasmids in this strain. Double-click the cell to open "
                         "the selector and choose one or more from SBH_plasmids_collections."),
                sbol_term="sbol_funcComp",
                namespace=NS_SBOLS,
                col_type="URI",
                sheet_lookup=True,
                lookup_sheet="SBH_plasmids_collections",
                from_col="A",
                to_col="B",
                split_on='","',
                comma_append=True,
            ),
        ]
        + _provenance_cols()
    ),
)

SUPPLEMENT = SheetDef(
    name="supplement",
    display_name="Supplement",
    # ModuleDefinition (not ComponentDefinition): the Chemical column maps to
    # sbol_funcComp, which builds a ModuleDefinition for the row object. Keeping
    # the row as a ModuleDefinition lets funcComp() reuse that same object
    # instead of creating a colliding one (SBOL_ERROR_URI_NOT_UNIQUE).
    sbol_object_type="ModuleDefinition",
    molecule_type="",
    role="supplement",
    flapjack_object=None,
    sbh_collections=["SBH_chemicals_collection"],
    name_column="Supplement Name",
    ui_group="Sample Design",
    columns=(
        _bio_base_cols("Supplement")
        + [
            ColumnDef(
                name="Chemical",
                tooltip="The base chemical compound for this supplement. Select from the SBH_chemicals_collection dropdown.",
                sbol_term="sbol_funcComp",
                namespace=NS_SBOLS,
                col_type="URI",
                sheet_lookup=True,
                lookup_sheet="SBH_chemicals_collection",
                from_col="A",
                to_col="B",
            ),
            ColumnDef(
                name="Concentration",
                tooltip="The concentration of this supplement (include units, e.g. '50 µg/mL').",
                sbol_term="fj_concentration",
                namespace=NS_FJ,
                col_type="String",
            ),
        ]
        + _provenance_cols()
    ),
)

SAMPLE_DESIGN = SheetDef(
    name="sample design",
    display_name="Sample Design",
    sbol_object_type="ModuleDefinition",
    molecule_type="",
    role="sample_design",
    flapjack_object=None,
    sbh_collections=["SBH_strains_collection", "SBH_media_collection"],
    name_column="Sample Design Name",
    ui_group="Sample Design",
    columns=(
        _bio_base_cols("Sample Design")
        + [
            ColumnDef(
                name="Strains",
                tooltip="The strain(s) used in this sample design. Select from the SBH_strains_collection dropdown.",
                sbol_term="sbol_module",
                namespace=NS_SBOLS,
                col_type="URI",
                sheet_lookup=True,
                lookup_sheet="SBH_strains_collection",
                from_col="A",
                to_col="B",
            ),
            ColumnDef(
                name="Medias",
                tooltip="The growth media used in this sample design. Select from the SBH_media_collection dropdown.",
                sbol_term="sbol_module",
                namespace=NS_SBOLS,
                col_type="URI",
                sheet_lookup=True,
                lookup_sheet="SBH_media_collection",
                from_col="A",
                to_col="B",
            ),
            ColumnDef(
                name="Supplements",
                tooltip=("The supplement(s) for this sample design. Double-click the cell "
                         "to open the selector and choose one or more Supplement IDs "
                         "defined on the supplement sheet."),
                sbol_term="sbol_module",
                namespace=NS_SBOLS,
                col_type="URI",
                # Local resolution against the supplement entries in this
                # workbook (Object_ID lookup), not the online SBH collection.
                # split_on="," allows multiple comma-separated IDs.
                object_id_lookup=True,
                split_on='","',
            ),
        ]
        + _provenance_cols()
    ),
)

STUDY = SheetDef(
    name="study",
    display_name="Study",
    sbol_object_type="Collection",
    molecule_type="",
    role="",
    flapjack_object="Study",
    sbh_collections=[],
    name_column=None,
    ui_group="Study",
    # Not part of any template and not offered in the custom catalog.
    ui_selectable=False,
    columns=[
        _name_col("Study"),
        _id_col("Study"),
        _prev_version_col(),
        _desc_col("Study"),
        ColumnDef(
            name="Submission Date",
            tooltip="The date the study was submitted for publication (YYYY-MM-DD).",
            sbol_term="isa_submissionDate",
            namespace=NS_ISA,
            col_type="String",
        ),
        ColumnDef(
            name="Public Release Date",
            tooltip="The date the study data was made publicly available (YYYY-MM-DD).",
            sbol_term="isa_publicReleaseDate",
            namespace=NS_ISA,
            col_type="String",
        ),
        ColumnDef(
            name="Contacts",
            tooltip="Contact person(s) for this study. Enter name and email separated by semicolons.",
            sbol_term="isa_contacts",
            namespace=NS_ISA,
            col_type="String",
        ),
        ColumnDef(
            name="Design Type",
            tooltip="The experimental design type (e.g. factorial design, time series).",
            sbol_term="isa_designType",
            namespace=NS_ISA,
            col_type="String",
        ),
        ColumnDef(
            name="Factor Name",
            tooltip="The name of the experimental factor being varied (e.g. temperature, inducer concentration).",
            sbol_term="isa_factorName",
            namespace=NS_ISA,
            col_type="String",
        ),
        ColumnDef(
            name="Factor Type",
            tooltip="The type of experimental factor (e.g. environmental stress, chemical compound).",
            sbol_term="isa_factorType",
            namespace=NS_ISA,
            col_type="String",
        ),
        _pubmed_col(),
        _doi_col(),
    ],
)

ASSAY = SheetDef(
    name="assay",
    display_name="Assay",
    sbol_object_type="Experiment",
    molecule_type="",
    role="",
    flapjack_object="Assay",
    sbh_collections=[],
    name_column=None,
    ui_group="Study",
    columns=[
        _name_col("Assay"),
        _id_col("Assay"),
        _prev_version_col(),
        _desc_col("Assay"),
        ColumnDef(
            name="Measurement Type",
            tooltip="The type of measurement performed (e.g. fluorescence, absorbance, growth rate).",
            sbol_term="isa_measurementType",
            namespace=NS_ISA,
            col_type="String",
        ),
        ColumnDef(
            name="Technology Type",
            tooltip="The measurement technology used (e.g. flow cytometry, plate reader).",
            sbol_term="isa_technologyType",
            namespace=NS_ISA,
            col_type="String",
        ),
        ColumnDef(
            name="Technology Platform",
            tooltip="The specific instrument or platform used (e.g. BD FACSCanto, BioTek Synergy).",
            sbol_term="isa_technologyPlatform",
            namespace=NS_ISA,
            col_type="String",
        ),
        ColumnDef(
            name="Protocols",
            tooltip="URI(s) of the experimental protocols used for this assay.",
            sbol_term="sbol_wasDerivedFrom",
            namespace=NS_SBOLS,
            col_type="URI",
        ),
        ColumnDef(
            name="Temperature",
            tooltip="Incubation temperature for this assay (include units, e.g. '37 °C').",
            sbol_term="fj_temperature",
            namespace=NS_FJ,
            col_type="String",
        ),
        _pubmed_col(),
        _doi_col(),
    ],
)

SAMPLE = SheetDef(
    name="sample",
    display_name="Sample",
    sbol_object_type="ExperimentalData",
    molecule_type="",
    role="",
    flapjack_object="Sample",
    sbh_collections=["SBH_sampledesigns_collection"],
    name_column=None,
    ui_group="Study",
    columns=[
        _name_col("Sample"),
        _id_col("Sample"),
        ColumnDef(
            name="Row",
            tooltip="Well row position in the plate (e.g. A, B, C).",
            sbol_term="fj_row",
            namespace=NS_FJ,
            col_type="String",
        ),
        ColumnDef(
            name="Column",
            tooltip="Well column position in the plate (e.g. 1, 2, 3).",
            sbol_term="fj_column",
            namespace=NS_FJ,
            col_type="String",
        ),
        ColumnDef(
            name="Assay ID",
            tooltip="The ID of the Assay this sample belongs to.",
            sbol_term="sbol_experimentalData",
            namespace=NS_SBOLS,
            col_type="String",
            # Resolve to the local Assay object created in this workbook.
            object_id_lookup=True,
            parent_lookup=True,
        ),
        ColumnDef(
            name="Sample Design",
            tooltip=("The Sample Design describing the biological conditions for this "
                     "sample. Select from the SBH_sampledesigns_collection dropdown."),
            sbol_term="sbol_wasDerivedFrom",
            namespace=NS_SBOLS,
            col_type="URI",
            sheet_lookup=True,
            lookup_sheet="SBH_sampledesigns_collection",
            from_col="A",
            to_col="B",
        ),
    ],
)

MEASUREMENT = SheetDef(
    name="measurement",
    display_name="Measurement",
    sbol_object_type="",
    molecule_type="",
    role="",
    flapjack_object="Signal",
    sbh_collections=[],
    name_column=None,
    ui_group="Study",
    columns=[
        _name_col("Measurement"),
        _id_col("Measurement"),
        ColumnDef(
            name="Sample ID",
            tooltip="The ID of the Sample this measurement belongs to.",
            sbol_term="fj_sampleId",
            namespace=NS_FJ,
            col_type="String",
        ),
        ColumnDef(
            name="Signal ID",
            tooltip="The ID of the Signal being measured.",
            sbol_term="fj_signalId",
            namespace=NS_FJ,
            col_type="String",
        ),
        ColumnDef(
            name="Time",
            tooltip="Time point of the measurement (include units, e.g. '60 min').",
            sbol_term="fj_time",
            namespace=NS_FJ,
            col_type="String",
        ),
        ColumnDef(
            name="Value",
            tooltip="The measured value at this time point.",
            sbol_term="fj_value",
            namespace=NS_FJ,
            col_type="String",
        ),
    ],
)


# ── Sheet registry ────────────────────────────────────────────────────────────

ALL_SHEETS: dict = {
    "promoter":     PROMOTER,
    "rbs":          RBS,
    "cds":          CDS,
    "terminator":   TERMINATOR,
    "other":        OTHER,
    "ncrna":        NCRNA,
    "rna":          RNA,
    "protein":      PROTEIN,
    "complex":      COMPLEX,
    "signal":       SIGNAL,
    "chassis":      CHASSIS,
    "media":        MEDIA,
    "chemicals":    CHEMICALS,
    "strain":       STRAIN,
    "supplement":   SUPPLEMENT,
    "sample design": SAMPLE_DESIGN,
    "study":        STUDY,
    "assay":        ASSAY,
    "sample":       SAMPLE,
    "measurement":  MEASUREMENT,
}


# ── Pre-made template configurations ─────────────────────────────────────────

TEMPLATE_CONFIGS: dict = {
    "resources": [
        ALL_SHEETS["promoter"],
        ALL_SHEETS["rbs"],
        ALL_SHEETS["cds"],
        ALL_SHEETS["terminator"],
        ALL_SHEETS["other"],
        ALL_SHEETS["ncrna"],
        ALL_SHEETS["rna"],
        ALL_SHEETS["protein"],
        ALL_SHEETS["complex"],
        ALL_SHEETS["chassis"],
        ALL_SHEETS["media"],
        ALL_SHEETS["chemicals"],
    ],
    "strains": [
        ALL_SHEETS["strain"],
    ],
    "sample_design": [
        ALL_SHEETS["sample design"],
        ALL_SHEETS["supplement"],
    ],
    "assay": [
        ALL_SHEETS["assay"],
        ALL_SHEETS["sample"],
        ALL_SHEETS["measurement"],
        ALL_SHEETS["signal"],
    ],
}
