class JsonTypes:
    types = {
        "int": int,
        "float": float,
        "bool": bool,
        "string": str,
        "iarray": list,
        "farray": list,
        "carray": list,
        "sarray": list,
        "dict": dict,
        "object": object,
        "enum": dict,
    }

    @staticmethod
    def is_valid_type(value):
        return isinstance(value, (int,float,bool,str,list,dict,object))

    @staticmethod
    def get_type(value):
        return JsonTypes.types.get(value)
