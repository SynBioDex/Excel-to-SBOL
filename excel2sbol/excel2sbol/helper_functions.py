# Make sure to update the dependency graphic
# https://github.com/SynBioDex/Excel-to-SBOL/blob/master/images/dependency_structure.PNG
# if change are made to modle dependencie
import string
import re


def truthy_strings(to_check):
    """Takes in several variants of True and False and returns a boolean
    True or False

    Args:
        to_check (string,boolean): A string or boolean such as 'True', 'TRUE',
        'tRue', or True

    Raises:
        TypeError: If the value can't be converted to 'true' or 'false'
        an error is raised

    Returns:
        [boolean]: True or False is returned depending on the inputs
    """
    if str(to_check).lower() == 'false':
        return False
    elif str(to_check).lower() == 'true':
        return True
    else:
        raise TypeError


def col_to_num(col_name):
    """takes an excel column name, e.g. AA and converts it to a
    zero indexed number e.g. 26

    Args:
       col_name (string): An excel formatted column name, e.g. AA

    Raises:
        TypeError: Raised if the input is not a string
        ValueError: Raised if the string is longer than three
                    or contains spaces

    Returns:
        num (integer): A zero indexed column index
    """

    if type(col_name) != str:
        # is not a string
        raise TypeError
    elif len(col_name.replace(" ", "")) != len(col_name):
        # contains spaces
        raise ValueError
    elif len(col_name) > 3:
        # too long to be an excel column name
        raise ValueError

    num = 0
    for ltr in col_name:
        if ltr in string.ascii_letters:
            num = num * 26 + (ord(ltr.upper()) - ord('A')) + 1
    num = num - 1
    return (num)


def check_name(nm_to_chck):
    """the function verifies that the names is alphanumeric and
    separated by underscores if that is not the case the special characters are
    replaced by their unicode decimal code number

    Args:
        nm_to_chck (string): the name to be checked

    Returns:
        compliant_name (string): alphanumberic name with special
                                 characters replaced by _u###_
    """

    if not bool(re.match('^[a-zA-Z0-9]+$', nm_to_chck)):
        # replace special characters with numbers
        for ltr in nm_to_chck:
            if ord(ltr) > 122 or ord(ltr) < 48:
                # 122 is the highest decimal code number
                # for common latin ltrs or arabic numbers
                # this helps identify special characters like
                # ä or ñ, which isalnum() returns as true
                # the characters that don't meet this criterion are replaced
                # by their decimal code number separated by an underscore
                nm_to_chck = nm_to_chck.replace(ltr, str(f"_u{ord(ltr)}_"))
                # new_ltr = str(ltr.encode("unicode_escape"))
                # new_ltr = new_ltr.replace(r"b'\\", "").replace("'", "")
                # nm_to_chck = nm_to_chck.replace(ltr, f'_{new_ltr}_')
            elif ord(ltr) == 32:
                nm_to_chck = nm_to_chck.replace(ltr, "_")
            else:
                # remove all letters, numbers and whitespaces
                ltr = re.sub(r'[\w, \s]', '', ltr)
                # this enables replacing all other
                # special characters that are under 122
                if len(ltr) > 0:
                    nm_to_chck = nm_to_chck.replace(ltr, str(f"_u{ord(ltr)}_"))

    if nm_to_chck[0].isnumeric():
        # ensures it doesn't start with a number
        nm_to_chck = f"_{nm_to_chck}"

    return(nm_to_chck)
