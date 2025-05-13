import pytest
import sbol2


@pytest.fixture()
def sbol_doc():
    # invoked once per test function
    sbol2.Config.setOption('sbol_typed_uris', False)
    doc = sbol2.Document()
    yield doc


@pytest.fixture()
def sbol_component():
    # invoked once per test function
    comp_nm = 'test_comp_name'
    sbol2.Config.setOption('sbol_typed_uris', False)
    comp = sbol2.ComponentDefinition(comp_nm, sbol2.BIOPAX_DNA)
    comp.name = comp_nm
    yield comp


@pytest.fixture()
def norm_dict():
    expected_dict = {'A': {'To_This': 1}, 'B': {'To_This': 2},
                     'C': {'To_This': 3}, 'D': {'To_This': 4},
                     'E': {'To_This': 5}, 'F': {'To_This': 6},
                     'G': {'To_This': 7}, 'H': {'To_This': 8},
                     'I': {'To_This': 9}, 'J': {'To_This': 10},
                     'K': {'To_This': 11}, 'L': {'To_This': 12},
                     'M': {'To_This': 13}, 'N': {'To_This': 14},
                     'O': {'To_This': 15}, 'P': {'To_This': 16},
                     'Q': {'To_This': 17}, 'R': {'To_This': 18},
                     'S': {'To_This': 19}, 'T': {'To_This': 20},
                     'U': {'To_This': 21}, 'V': {'To_This': 22},
                     'W': {'To_This': 23}, 'X': {'To_This': 24},
                     'Y': {'To_This': 25}, 'Z': {'To_This': 26}
                     }
    return(expected_dict)


@pytest.fixture()
def replacement_dict():
    expected_dict = {'A': {'To_This': '1{REPLACE_HERE}1'},
                     'B': {'To_This': '2{REPLACE_HERE}2'},
                     'C': {'To_This': '3{REPLACE_HERE}3'},
                     'D': {'To_This': '4{REPLACE_HERE}4'},
                     'E': {'To_This': '5{REPLACE_HERE}5'},
                     'F': {'To_This': '6{REPLACE_HERE}6'},
                     'G': {'To_This': '7{REPLACE_HERE}7'},
                     'H': {'To_This': '8{REPLACE_HERE}8'},
                     'I': {'To_This': '9{REPLACE_HERE}9'},
                     'J': {'To_This': '10{REPLACE_HERE}10'},
                     'K': {'To_This': '11{REPLACE_HERE}11'},
                     'L': {'To_This': '12{REPLACE_HERE}12'},
                     'M': {'To_This': '13{REPLACE_HERE}13'},
                     'N': {'To_This': '14{REPLACE_HERE}14'},
                     'O': {'To_This': '15{REPLACE_HERE}15'},
                     'P': {'To_This': '16{REPLACE_HERE}16'},
                     'Q': {'To_This': '17{REPLACE_HERE}17'},
                     'R': {'To_This': '18{REPLACE_HERE}18'},
                     'S': {'To_This': '19{REPLACE_HERE}19'},
                     'T': {'To_This': '20{REPLACE_HERE}20'},
                     'U': {'To_This': '21{REPLACE_HERE}21'},
                     'V': {'To_This': '22{REPLACE_HERE}22'},
                     'W': {'To_This': '23{REPLACE_HERE}23'},
                     'X': {'To_This': '24{REPLACE_HERE}24'},
                     'Y': {'To_This': '25{REPLACE_HERE}25'},
                     'Z': {'To_This': '26{REPLACE_HERE}26'}
                     }
    return(expected_dict)
