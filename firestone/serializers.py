from django.http import HttpResponse
from django.core.serializers.json import DateTimeAwareJSONEncoder
import json

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
def _get_serializer(ser_format=DEFAULT_SERIALIZATION_FORMAT):
    """
    Returns the serialization function
    """
    return MAPPER.get(ser_format, MAPPER[DEFAULT_SERIALIZATION_FORMAT])

def _get_serialization_format(request):
    """
    Returns the serialization format that the ``request``'s ``Accept`` header
    wants. Returns ``DEFAULT_SERIALIZATION_FORMAT`` if header doesn't match any
    of the provided serializaion formats.
    """
    accept_header = request.META.get('HTTP_ACCEPT', '')
    if accept_header:
        accept_header = accept_header.split(',')
        accept_header = [value.strip().lower() for value in accept_header]
        for preference in accept_header:
            if preference in MAPPER:
                return preference
    return DEFAULT_SERIALIZATION_FORMAT

def serialize(data, ser_format=DEFAULT_SERIALIZATION_FORMAT):
    """
    Serializes ``data`` to ``ser_format``.
    
    Returns a tuple of (serialized_data, headers_dict)
    """
    s = _get_serializer(ser_format)
    return s(data)


class SerializerMixin(object):
    DEFAULT_SERIALIZATION_FORMAT = 'application/json'
    MAPPER = {
        'application/json': 'serialize_to_json',
        'application/vnd.ms-excel': 'serialize_to_excel',
    }

    def get_serialization_format(self):
        return _get_serialization_format(self.request)

    def get_serializer(self, ser_format):
        return getattr(self, self.MAPPER[ser_format]) 

    def serialize_to_json(self, data):
        return json.dumps(data, cls=DateTimeAwareJSONEncoder, indent=4), {'Content-Type': 'application/json'}
        #return _serialize_to_json(data)

    def serialize_to_excel(self, data):
        pass
    
    def get_response(self, data, headers):
        r = HttpResponse(data)
        for key, value in headers.items():
            r[key] = value
        return r

    def serialize(self, data):
        ser_format = self.get_serialization_format()
        serializer = self.get_serializer(ser_format)
        data, headers = serializer(data)

        return self.get_response(data, headers)

        # TODO: Return HttpResponse object. If we want additional headers,
        # override handler's serialize method.


# TODO: Upon handler class instantiation, set SerializerMixin as a superclass.
