# check if function exists in thing
from inspect import getmembers, isfunction
import excel_sbol_utils.library as eu

# term = "add"
# func_list = [o[0] for o in getmembers(eu) if isfunction(o[1])]


class rowobj():

    def __init__(self, A, B, C):
        self.A = A
        self.B = B
        self.C = C


class switch():
    func_list = func_list = [o[0] for o in getmembers(eu) if isfunction(o[1])]

    def switch(self, rowobj, sbolterm):
        if sbolterm in self.func_list:
            res = getattr(eu, sbolterm)(rowobj)
            print(res)


row_obj = rowobj('one', 2, 3)
sw = switch()
sw.switch(row_obj, 'add')


# if term in func_list:
#     tot = getattr(eu, term)(2, 4)
#     print(tot)

# can maybe make a class with all the properties and then pass an object of that class to the switch statemnt (which may or may not be its own class)
# look at inheritance
# think about how to get the object to excel utils
# continue to build out this simple example first