# Read the format given by Accept Header.
# IF supported, output to that format. If not supported, fallback to default
# serializer. Along with the serialized response, return the response's Content-type

import json

def _serialize_to_json(data):
    """
    Serializes ``data`` into JSON, and returns a tuple
       serialized data, HttpResponse headers as dictionary key-values
    """
    return json.dumps(data), {'content_type': 'application/json'}

DEFAULT_SERIALIZER = _serialize_to_json
def _get_serializer(request, *args, **kwargs):
    """
    Returns the function that will serialize the data
    """
    return DEFAULT_SERIALIZER

def serialize(data, request, *args, **kwargs):
    """
    Selects the appropriate serializer, calls it, and returns its result
    """
    s = _get_serializer(request, *args, **kwargs)
    return s(data)

