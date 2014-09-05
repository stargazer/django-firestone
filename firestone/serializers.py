from django.http import HttpResponse
from django.core.serializers.json import DateTimeAwareJSONEncoder
import json


class SerializerMixin(object):
    """
    Can be used as a standalone class to instansiate objects(as long as they
    have a ``request`` attribute), or as a Mixin for handler classes.
    """
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
        return '', {
            'content-type': 'application/vnd.ms-excel',
            'content-disposition': 'attachment'
        } 
        
    def serialize(self, data, ser_format=''):
        """
        Serializes ``data`` and returns  tuple of:
            (``serialized data``, ``headers`` for the HttpResponse object)

        if ``ser_format`` is not provided, the serialization format is set
        according to the requests's Accept Header
        """
        if not ser_format:
            ser_format = self.get_serialization_format()

        serializer = self.get_serializer(ser_format)
        data, headers = serializer(data)
        return data, headers

    def get_response(self, data):
        """
        Serializers ``data`` and returns the appropriate HttpResponse object
        """
        data, headers = self.serialize(data)
        r = HttpResponse(data)
        for key, value in headers.items():
            r[key] = value
        return r


# TODO: Upon handler class instantiation, set SerializerMixin as a superclass.
