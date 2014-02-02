"""
The ``deserializers`` module exposes the classes responsible for
deserializing the request bodies of incoming requests to python deta
structures, according to the ``Content-type`` header
"""
import exceptions
import json


def _json_deserializer(data):
    try:
        return json.loads(data)
    except ValueError:
        raise



MAPPER = {
    'application/json': _json_deserializer,
}        
def _get_deserializer(content_type):
    """
    Get the deserializer for the given ``content_type``
    """
    content_type = content_type.lower() 

    for key, value in MAPPER.items():
        if content_type.startswith(key):
            return value

    return None       

def deserialize(data, content_type):
    """
    Deserialized ``data``, according to ``content_type``
    """
    if not content_type:
        raise exceptions.UnsupportedMediaType
    
    ds = _get_deserializer(content_type) 
    if not ds:
        raise exceptions.UnsupportedMediaType

    try:
        return ds(data)
    except ValueError:
        raise exceptions.BadRequest

def deserialize_request_body(request, *args, **kwargs):
    """
    Deserializes the request body, according to its Content-Type header
    """
    try:
        return deserialize(request.body, request.META.get('CONTENT_TYPE', None)) 
    except exceptions.UnsupportedMediaType:
        raise



