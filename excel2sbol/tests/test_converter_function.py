import pytest
import utils.converter_function as confun
import os
import tempfile
import rdflib
import rdflib.compare


@pytest.mark.parametrize(
    'file_name, template_name, raising_err, expected',
    [
        (
         "pichia_toolkit_KWK_v002.xlsx",
         'darpa_template_blank_v005_20220222.xlsx',  False,
         'pichia_toolkit_KWK_v002.xml'
        ),
        (
         "does_not_exist.xlsx",
         'darpa_template_blank_v005_20220222.xlsx',  True,
         FileNotFoundError
        )
    ]
)
def test_converter(file_name, template_name, raising_err, expected):
    file_dir = os.path.dirname(__file__)
    file_path_in = os.path.join(file_dir, 'test_files',
                                file_name)
    with tempfile.TemporaryDirectory() as dirpath:
        file_path_out = os.path.join(dirpath, 'sbol_out.xml')

        if raising_err:
            with pytest.raises(expected):
                confun.converter(template_name, file_path_in, file_path_out)

        else:
            confun.converter(template_name, file_path_in, file_path_out)

            expected = os.path.join(file_dir, 'test_files',
                                    expected)
            expected_graph = rdflib.Graph()
            expected_graph.load(expected)
            expected_iso = rdflib.compare.to_isomorphic(expected_graph)
            output_graph = rdflib.Graph()
            output_graph.load(file_path_out)
            output_iso = rdflib.compare.to_isomorphic(output_graph)
            # rdf_diff = rdflib.compare.graph_diff(expected_iso, output_iso)
            assert output_iso == expected_iso
