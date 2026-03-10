from collections import namedtuple


class TypesUiMarkups:
    PACK = 0
    GRID = 1


class TkinterMarkup:
    def __init__(self, typename, requiredFields, **kwargs):
        self.typename = typename
        self.fields = tuple(requiredFields) + tuple(kwargs.keys())
        self.defaults = kwargs
        self.NamedTuple = namedtuple(typename, self.fields)

    def __call__(self, **kwargs):
        allKwargs = self.defaults.copy()
        allKwargs.update(kwargs)
        missingFields = [field for field in self.fields if field not in allKwargs]
        if missingFields and len(missingFields) > len(self.fields) - len(self.defaults):
            raise ValueError("Not all required fields are provided.")
        return self.NamedTuple(**allKwargs)


MARCUP = TkinterMarkup(
    typename='Markup', requiredFields=["element", "type"],
    padx=None, pady=None, side=None, fill=None, expand=None, anchor=None,  # pack
    row=None, column=None, sticky=None                                     # grid
)
