def col_to_excel(col):
    """
    Converts the column number to the excel column name (A, B, ... AA  etc)

    Parameters
    ----------
    col : INTEGER
        The number of the column to convert. Note that 1 converts to A

    Returns
    -------
    excel_col : STRING
        The string which describes the name of the column in Excel
        
    Example
    -------
    print(col_to_excel(9))

    """
    excel_col = ""
    div = col 
    
    while div>0:
        (div, mod) = divmod(div-1, 26) # will return (x, 0 .. 25)
        excel_col = chr(mod + 65) + excel_col

    return excel_col
