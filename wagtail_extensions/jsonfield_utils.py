

def jsonfield_path_split(path):
    """
    Split a Django dunder field path targeting a `JSONField` into core
    components: json field name, path in json doc.

    For example:
            "data__a__b" => ('data', ['a', 'b'])
    """
    splits = path.split('__')
    field_name = splits[0]
    json_path = splits[1:]
    return (field_name, json_path)
