# run by typing 'pytest' into the terminal
# for more detailed output use 'pytest -v -s'
import pytest
import excel2sbol.column_functions as cf
import os


class Test_sbol_methods:

    @pytest.mark.parametrize(
        'sbol_term, nm_url, cell_val, raising_err, expected',
        [
            ("Not_applicable", 'nm_url', 'cell_val', False, 'fake_NA'),
            ("add_new", 'nm_url', 'cell_val', False, 'fake_add_new')
        ]
    )
    def test_switch(self, sbol_term, nm_url, cell_val, raising_err, expected,
                    sbol_component, sbol_doc, monkeypatch):

        def fake_NA(self):
            return "fake_NA"

        def fake_add_new(self):
            return "fake_add_new"

        monkeypatch.setattr(cf.sbol_methods, 'Not_applicable', fake_NA)
        monkeypatch.setattr(cf.sbol_methods, 'add_new', fake_add_new)

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)
        if raising_err:
            with pytest.raises(expected):
                x.switch(sbol_term)
        else:
            assert x.switch(sbol_term) == expected

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, expected',
        [
            ('nm_url', 'atgcgcgcgc', False, 'atgcgcgcgc'),
            ('nm_url', 'atGC GCA', False, 'atgcgca'),
            ('nm_url', 'at1gcgcgcgc', True, TypeError),
            ('nm_url', 5, True, TypeError),
            # ('nm_url', 'attgz', True, TypeError),
            ('nm_url', 'ättgc', True, TypeError),
            ('nm_url', 'atuuc', False, 'atuuc')
        ]
    )
    def test_sbol_sequence(self, nm_url, cell_val, raising_err,
                           expected, sbol_component, sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)

        if raising_err:
            with pytest.raises(expected):
                x.sbol_sequence()

        else:
            x.sbol_sequence()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions[f'http://examples.org/{sbol_component.name}/1']
            seq = sbol_doc.sequences[f'http://examples.org/{sbol_component.name}_sequence/1']

            assert seq.elements == expected and str(comp.sequence) == f'http://examples.org/{sbol_component.name}_sequence/1'

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, expected',
        [
            ('nm_url', 'Any 1 descript with wεird stuff!', False,
             'Any 1 descript with wεird stuff!'),
            ('nm_url', 'Any odd description', False, 'Any odd description'),
            ('nm_url', 5, True, TypeError),
            ('nm_url', '5005', True, TypeError)
        ]
    )
    def test_dcterms_description(self, nm_url, cell_val,
                                 raising_err, expected, sbol_component,
                                 sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)
        if raising_err:
            with pytest.raises(expected):
                x.dcterms_description()

        else:
            x.dcterms_description()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions[f'http://examples.org/{sbol_component.name}/1']
            assert comp.description == expected

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, expected1, expected2',
        [
            ('nm_url', "testname", False, "testname", "testname"),
            ('nm_url', "test_name", False, "test_name", "test_name"),
            ('nm_url', "_test_name", False, "_test_name", "_test_name"),
            ('nm_url', "test_name12", False, "test_name12", "test_name12"),
            ('nm_url', "12test_name", False, "12test_name", "_12test_name"),
            ('nm_url', "test_name%", False, "test_name%", "test_name_u37_"),
            ('nm_url', "test_näme", False, "test_näme", "test_n_u228_me"),
            ('nm_url', "tεst_name", False, "tεst_name", "t_u949_st_name"),
            ('nm_url', 576, True, TypeError, "")
        ]
    )
    def test_sbol_displayId(self, nm_url, cell_val,
                            raising_err, expected1, expected2,
                            sbol_component, sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)
        if raising_err:
            with pytest.raises(expected1):
                x.sbol_displayId()

        else:
            x.sbol_displayId()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions['http://examples.org/test_comp_name/1']
            assert comp.name == expected1 and comp.displayId == expected2

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, roles, expected',
        [
            ('nm_url', False, False, ["0000316", '0000167'],
             ['0000316', '0000167']),
            ('nm_url', False, False, [], []),
            ('nm_url', True, False, ["0000316"], ['0000988', '0000316']),
            ('nm_url', True, False, [], ['0000988']),
            ('nm_url', "False", False, ["0000316"], ['0000316']),
            ('nm_url', "FALSE", False, [], []),
            ('nm_url', "TrUe", False, ["0000316"], ['0000988', '0000316']),
            ('nm_url', "TRUE", False, [], ['0000988']),
            ('nm_url', 0, False, ["0000316"], ['0000316']),
            ('nm_url', 1, False, [], ['0000988']),
            ('nm_url', "random stuff", True, ["0000316"], TypeError),
            ('nm_url', 576, True, [], TypeError)
        ]
    )
    def test_sbol_roleCircular(self, nm_url, cell_val, raising_err, roles,
                               expected, sbol_component, sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)
        if len(roles) > 0:
            for role in roles:
                sbol_component.roles = sbol_component.roles + [f'http://identifiers.org/so/SO:{role}']

        if raising_err:
            with pytest.raises(expected):
                x.sbol_roleCircular()

        else:
            expected = [f'http://identifiers.org/so/SO:{role}' for role in expected]
            x.sbol_roleCircular()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions['http://examples.org/test_comp_name/1']
            assert set(comp.roles) == set(expected)

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, roles, expected',
        [
            ('nm_url', "http://purl.obolibrary.org/obo/SO_0000167",
             False, ["0000316"], ['0000316', '0000167']),
            ('nm_url', "http://purl.obolibrary.org/obo/SO_0000167", False, [],
             ['0000167']),
            ('nm_url', "http://purl.obolibrary.org/obo/SO_0000139", False,
             ["0000316", '0000167'], ['0000139', '0000316', '0000167']),
            ('nm_url', "http://purl.obolibrary.org/obo/SO_000013", True, ["0000316"], ValueError),
            ('nm_url', "random stuff", True, ["0000316"], ValueError),
            ('nm_url', 576, True, [], TypeError)
        ]
    )
    def test_sbol_role(self, nm_url, cell_val, raising_err, roles,
                       expected, sbol_component, sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)
        if len(roles) > 0:
            for role in roles:
                sbol_component.roles = sbol_component.roles + [f'http://purl.obolibrary.org/obo/SO_{role}']

        if raising_err:
            with pytest.raises(expected):
                x.sbol_role()

        else:
            expected = [f'http://purl.obolibrary.org/obo/SO_{role}' for role in expected]
            x.sbol_role()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions['http://examples.org/test_comp_name/1']
            assert set(comp.roles) == set(expected)

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, expected',
        [
            ('nm_url', "4932", False, 'https://identifiers.org/taxonomy:4932'),
            ('nm_url', 4932, False, 'https://identifiers.org/taxonomy:4932'),
            ('nm_url', "23", False, 'https://identifiers.org/taxonomy:23'),
            ('nm_url', 23, False, 'https://identifiers.org/taxonomy:23'),
            ('nm_url', 'Hello', True, ValueError),
            ('nm_url', 1.5, False, 'https://identifiers.org/taxonomy:1'),
            ('nm_url', 1.0, False, 'https://identifiers.org/taxonomy:1'),
            ('nm_url', 1, False, 'https://identifiers.org/taxonomy:1'),
            ('nm_url', True, True, TypeError)
        ]
    )
    def test_sbh_targetOrganism(self, nm_url, cell_val, raising_err, expected,
                                sbol_component, sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)

        if raising_err:
            with pytest.raises(expected):
                x.sbh_targetOrganism()

        else:
            x.sbh_targetOrganism()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions['http://examples.org/test_comp_name/1']
            assert comp.targetOrganism == expected

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, expected',
        [
            ('nm_url', "4932", False, 'https://identifiers.org/taxonomy:4932'),
            ('nm_url', 4932, False, 'https://identifiers.org/taxonomy:4932'),
            ('nm_url', "23", False, 'https://identifiers.org/taxonomy:23'),
            ('nm_url', 23, False, 'https://identifiers.org/taxonomy:23'),
            ('nm_url', 'Hello', True, ValueError),
            ('nm_url', 1.5, False, 'https://identifiers.org/taxonomy:1'),
            ('nm_url', 1.0, False, 'https://identifiers.org/taxonomy:1'),
            ('nm_url', 1, False, 'https://identifiers.org/taxonomy:1'),
            ('nm_url', True, True, TypeError)
        ]
    )
    def test_sbh_sourceOrganism(self, nm_url, cell_val, raising_err, expected,
                                sbol_component, sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)

        if raising_err:
            with pytest.raises(expected):
                x.sbh_sourceOrganism()

        else:
            x.sbh_sourceOrganism()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions['http://examples.org/test_comp_name/1']
            assert comp.sourceOrganism == expected

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, pubmedExpected, expected',
        [
            ('nm_url', "https://pubmed.ncbi.nlm.nih.gov/24295448/", False,
             True, 'https://pubmed.ncbi.nlm.nih.gov/24295448'),
            ('nm_url', "http://parts.igem.org/Part:BBa_K2273000", False, False,
             'http://parts.igem.org/Part:BBa_K2273000'),
            ('nm_url', "https://www.addgene.org/87906/", False, False,
             'https://www.addgene.org/87906'),
            ('nm_url', "https://www.ncbi.nlm.nih.gov/nuccore/M11180.2", False,
             False, 'https://www.ncbi.nlm.nih.gov/nuccore/M11180.2'),
            ('nm_url', 'Hello', True, False, ValueError),
            ('nm_url', 1.5, True, False, TypeError),
            ('nm_url', 10, True, False, TypeError),
            ('nm_url', True, True, False, TypeError)
        ]
    )
    def test_sbh_dataSource(self, nm_url, cell_val, raising_err,
                            pubmedExpected, expected, sbol_component,
                            sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)

        if raising_err:
            with pytest.raises(expected):
                x.sbh_dataSource()

        else:
            x.sbh_dataSource()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions['http://examples.org/test_comp_name/1']
            if pubmedExpected:
                identi = os.path.split(expected)[1]
                assert comp.wasDerivedFrom[0] == expected and comp.OBI_0001617 == identi
            else:
                assert comp.wasDerivedFrom[0] == expected

    @pytest.mark.parametrize(
        'nm_url, cell_val, raising_err, expected',
        [
            ('nm_url', "https://synbiohub.org/public/Excel2SBOL/direct/1", False,
             'https://synbiohub.org/public/Excel2SBOL/direct/1'),
            ('nm_url', "https://synbiohub.org/public/Excel2SBOL/Unknown/1",
             False, 'https://synbiohub.org/public/Excel2SBOL/Unknown/1'),
            ('nm_url', "https://pubmed.ncbi.nlm.nih.gov/24295448/",
             True, ValueError),
            ('nm_url', 'Hello', True, ValueError),
            ('nm_url', 1.5, True, TypeError),
            ('nm_url', 10, True, TypeError),
            ('nm_url', True, True, TypeError)
        ]
    )
    def test_sbh_alteredSequence(self, nm_url, cell_val, raising_err,
                                 expected, sbol_component, sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)

        if raising_err:
            with pytest.raises(expected):
                x.sbh_alteredSequence()

        else:
            x.sbh_alteredSequence()
            sbol_doc.addComponentDefinition(sbol_component)

            comp = sbol_doc.componentDefinitions['http://examples.org/test_comp_name/1']
            assert comp.wasGeneratedBy[0] == expected

    @pytest.mark.parametrize(
        'nm_url, sbol_term, cell_val, raising_err, expected',
        [
            ('https://wiki.synbiohub.org/wiki/Terms/synbiohub#',
             'sbh_designNotes', 'No Kex recognition site', False,
             'No Kex recognition site'),
            ('https://wiki.synbiohub.org/wiki/Terms/synbiohub#',
             'sbh_designNotes', 1.5, False, "1.5"),
            ('https://wiki.synbiohub.org/wiki/Terms/synbiohub#',
             'sbh_designNotes', "12 test_näme%", False, "12 test_näme%"),
            ('http://sbols.org/v2#', 'sbol_roleCircular', True, False, "True")
        ]
    )
    def test_add_new(self, nm_url, sbol_term, cell_val, raising_err,
                     expected, sbol_component, sbol_doc):

        x = cf.sbol_methods(nm_url, sbol_component, sbol_doc, cell_val)
        x.sbol_term = sbol_term

        if raising_err:
            with pytest.raises(expected):
                x.add_new()

        else:
            x.add_new()
            sbol_doc.addComponentDefinition(sbol_component)
            sbol_term_sfx = sbol_term.split("_", 1)[1]

            comp = sbol_doc.componentDefinitions['http://examples.org/test_comp_name/1']
            comp_attr = getattr(comp, sbol_term_sfx)
            assert comp_attr == expected


@pytest.mark.parametrize(
    'column_dict_entry, raising_err, expected',
    [
        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'FALSE', 'Replacement Lookup': 'FALSE',
             'Sheet Name': '', 'From Col': '', 'To Col': ''}, False, 'no_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'else', 'Replacement Lookup': 'FALSE',
             'Sheet Name': '', 'From Col': '', 'To Col': ''}, True, TypeError
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': False, 'Replacement Lookup': 'FALSE',
             'Sheet Name': '', 'From Col': '', 'To Col': ''}, False, 'no_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'FALSE', 'Replacement Lookup': False,
             'Sheet Name': '', 'From Col': '', 'To Col': ''}, False, 'no_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': False, 'Replacement Lookup': False,
             'Sheet Name': '', 'From Col': '', 'To Col': ''}, False, 'no_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': 'TRUE',
             'Sheet Name': 'Replacement', 'From Col': 'A', 'To Col': 'B'},
            False, 'replacement_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': True, 'Replacement Lookup': 'TRUE',
             'Sheet Name': 'Replacement', 'From Col': 'A', 'To Col': '2'},
            False, 'replacement_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': True,
             'Sheet Name': 'Replacement', 'From Col': 'a', 'To Col': 2}, False,
            'replacement_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': True, 'Replacement Lookup': True,
             'Sheet Name': 'Replacement', 'From Col': 'A', 'To Col': 'B'},
            False, 'replacement_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': 'FALSE',
             'Sheet Name': 'Simple', 'From Col': 'A', 'To Col': 'B'}, False,
            'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': True, 'Replacement Lookup': 'FALSE',
             'Sheet Name': 'Simple', 'From Col': 'A', 'To Col': 'B'}, False,
            'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': False,
             'Sheet Name': 'Simple', 'From Col': 'A', 'To Col': 'B'}, False,
            'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': True, 'Replacement Lookup': False,
             'Sheet Name': 'Simple', 'From Col': 'A', 'To Col': 'B'}, False,
            'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': 'FALSE',
             'Sheet Name': 'NA_Between', 'From Col': 'A', 'To Col': 'D'},
            False, 'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': 'FALSE',
             'Sheet Name': 'NA_Reverse', 'From Col': 'D', 'To Col': 'A'},
            False, 'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': 'FALSE',
             'Sheet Name': 'Simple_Reverse', 'From Col': 'B', 'To Col': 'A'},
            False, 'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': 'FALSE',
             'Sheet Name': 'Row_3_Start', 'From Col': 'C', 'To Col': 'B'},
            False, 'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': 'FALSE',
             'Sheet Name': 'Blank col between', 'From Col': 'C',
             'To Col': 'A'}, False, 'norm_dict'
        ),

        (
            {'SBOL Term': 'sbol_term', 'Namespace URL': 'nm_url',
             'Sheet Lookup': 'TRUE', 'Replacement Lookup': 'FALSE',
             'Sheet Name': 'Doesnt exist', 'From Col': 'A', 'To Col': 'B'},
            True, ValueError
        )
    ]
)
def test_column_class(column_dict_entry, raising_err, expected,
                      norm_dict, replacement_dict):
    file_dir = os.path.dirname(__file__)
    file_path_in = os.path.join(file_dir, 'test_files',
                                'Column_Class_test.xlsx')
    if raising_err:
        with pytest.raises(expected):
            cf.column(file_path_in, column_dict_entry)

    else:
        x = cf.column(file_path_in, column_dict_entry)

        if expected == 'no_dict':
            assert x.sbol_term == 'sbol_term'
            assert x.namespace_url == 'nm_url'
            assert x.replacement_lookup is False
            with pytest.raises(AttributeError):
                x.lookup_dict
        elif expected == 'norm_dict':
            assert x.sbol_term == 'sbol_term'
            assert x.namespace_url == 'nm_url'
            assert x.replacement_lookup is False
            assert x.lookup_dict == norm_dict

        elif expected == 'replacement_dict':
            assert x.sbol_term == 'sbol_term'
            assert x.namespace_url == 'nm_url'
            assert x.replacement_lookup is True
            assert x.lookup_dict == replacement_dict
