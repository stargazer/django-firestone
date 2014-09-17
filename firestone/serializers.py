from django.http import HttpResponse
from django.core.serializers.json import DateTimeAwareJSONEncoder
import tablib
import json
import StringIO


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
        Returns the serialization format that the ``request``'s ``Accept``
        header wants. Returns ``DEFAULT_SERIALIZATION_FORMAT`` if header
        doesn't match any of the provided serializaion formats.
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
        return (
            json.dumps(data, cls=DateTimeAwareJSONEncoder,
                       ensure_ascii=False, indent=4),
            {'Content-Type': 'application/json; charset=utf-8'}
        )

    def serialize_to_excel(self, data):
        from firestone.exceptions import NotAcceptable
        from firestone.exceptions import Unprocessable

        # At this point, ``data`` should have the form of
        # {'data': <data>, 'debug': <debug>, ...}.
        # We are only interested in the data['data']
        if not isinstance(data, dict) or 'data' not in data:
            # This should never happen
            raise Unprocessable('Fatal Error. Cannot process')

        data = data['data']
        # data should only be a dictionary or list(of dictionaries),
        # otherwise we can't serialize to excel
        if not isinstance(data, list) and not isinstance(data, dict):
            raise NotAcceptable()

        # if ``data`` is a dictionary, we make it into a list
        if isinstance(data, dict):
            data = [data, ]

        def process(value):
            # Returns a clean representation of ``value``
            if isinstance(value, dict):
                return ', '.join([
                    '%s: %s' % (process(k), process(v))
                    for k, v in value.items()
                ])
            elif isinstance(value, list) \
                or isinstance(value, tuple) \
                    or isinstance(value, set):
                return ', '.join([process(element) for element in value])

            try:
                return str(value)
            except UnicodeEncodeError:
                return unicode(value)

        # Excel Sheet headers. We lay them out, in the order they are defined
        # in the handler's ``template['fields']`` attribute
        headers = [
            field for field in self.template['fields'] if field in data[0]
        ]

        # We layout the values into a list of tuples, with each tuple element
        # corresponding to a header
        values = []
        for element in data:
            values.append(
                [process(element.get(key)) for key in headers]
            )

        # Create the tablib dataset
        dataset = tablib.Dataset(*values, headers=headers, title='Sheet')
        # Export to excel
        stream = StringIO.StringIO()
        stream.write(dataset.xls)

        filename = self.excel_filename
        if not isinstance(filename, basestring):
            filename = filename()

        return stream.getvalue(), {
            'Content-Type': 'application/vnd.ms-excel',
            'Content-Disposition': 'attachment; filename=%s;' % filename
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
