import json
from django.core.serializers.json import DateTimeAwareJSONEncoder

def _serialize_to_json(data):
    """
    Serializes ``data`` into JSON, and returns a tuple
       serialized data, HttpResponse headers as dictionary key-values
    """
    return json.dumps(data, cls=DateTimeAwareJSONEncoder, indent=4), {'content-type': 'application/json'}

def _serialize_to_excel(data):
    return '', {
        'content-type': 'application/vnd.ms-excel',
        'content-disposition': 'attachment'
    } 

DEFAULT_SERIALIZATION_FORMAT = 'application/json'
MAPPER = {
    'application/json': _serialize_to_json,
    'application/vnd.ms-excel': _serialize_to_excel,
}        
def _get_serializer(ser_format=''):
    """
    Returns the serialization function
    """
    return MAPPER.get(ser_format, MAPPER[DEFAULT_SERIALIZATION_FORMAT])

def _get_serialization_format(request, *args, **kwargs):
    """
    Returns the serialization format that the ``request``'s ``Accept`` header
    wants. Returns ``DEFAULT_SERIALIZATION_FORMAT`` if header doesn't match any
    of the provided serializaion formats.
    """
    accept_header = request.META.get('HTTP_ACCEPT', '')
    if accept_header:
        accept_header = accept_header.split(',')
        accept_header = [value.strip() for value in accept_header]
        for preference in accept_header:
            if preference in MAPPER:
                return preference
    return DEFAULT_SERIALIZATION_FORMAT

def serialize(data, ser_format=''):
    """
    Serializes ``data`` to ``ser_format``.
    
    Returns a tuple of (serialized_data, headers_dict)
    """
    s = _get_serializer(ser_format)
    return s(data)

def serialize_response_data(data, request, *args, **kwargs):
    """
    Serializes ``data`` to a serialization format that ``request`` demands
    
    Returns a tuple of (serialized_data, headers_dict)
    """
    ser_format = _get_serialization_format(request)
    return serialize(data, ser_format)
