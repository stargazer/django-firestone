from django.http import HttpResponse
from django.core.serializers.json import DateTimeAwareJSONEncoder
import json


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
        """
        Returns the serialization format that the ``request``'s ``Accept`` header
        wants. Returns ``DEFAULT_SERIALIZATION_FORMAT`` if header doesn't match any
        of the provided serializaion formats.
        """
        accept_header = self.request.META.get('HTTP_ACCEPT', '')
        if accept_header:
            accept_header = accept_header.split(',')
            accept_header = [value.strip().lower() for value in accept_header]
            for preference in accept_header:
                if preference in self.MAPPER:
                    return preference
        return self.DEFAULT_SERIALIZATION_FORMAT

    def get_serializer(self, ser_format):
        return getattr(self, self.MAPPER[ser_format]) 

    def serialize_to_json(self, data):
        return json.dumps(data, cls=DateTimeAwareJSONEncoder, indent=4), {'Content-Type': 'application/json'}
        #return _serialize_to_json(data)

    def serialize_to_excel(self, data):
        pass
    
    def serialize(self, data, ser_format=''):
        if not ser_format:
            ser_format = self.get_serialization_format()

        serializer = self.get_serializer(ser_format)
        data, headers = serializer(data)
        return data, headers

    def get_response(self, data):
        data, headers = self.serialize(data)
        r = HttpResponse(data)
        for key, value in headers.items():
            r[key] = value
        return r


# TODO: Upon handler class instantiation, set SerializerMixin as a superclass.
