"""
This module implements the functionality for request body deserialization.
API handler classes can inherit the functionality of any of these mixins.
"""
from django.utils.six.moves.urllib_parse import parse_qs
import json


def _json_deserializer(data):
    try:
        return json.loads(data)
    except ValueError:
        raise


def _form_encoded_data_deserializer(data):
    # param ``data`` is a string (querystring format)
    try:
        # dic is in the form ``key: [value]``
        dic = parse_qs(data, strict_parsing=True)
    except ValueError:
        raise

    # I transform ``dic`` in the form ``key: value``, by taking only the first
    # vaule of each key
    return {key: value[0] for key, value in dic.items()}

MAPPER = {
    'application/json': _json_deserializer,
    'application/x-www-form-urlencoded': _form_encoded_data_deserializer,
}


def _get_deserializer(content_type):
    content_type = content_type.lower()

    for key, value in MAPPER.items():
        if content_type.startswith(key):
            return value

    return None


class DeserializationMixin(object):
    """
    Provides functionality for deserializing the request body, according to the
    request's ``Content-type`` header
    """
    def deserialize(self):
        """
        Deserializes the request body, according to the request's Content-type.

        Returns Python data structures.
        Raises TypeError, ValueError
        """
        content_type = self.request.META.get('CONTENT_TYPE')
        if not content_type:
            raise TypeError

        deserializer = _get_deserializer(content_type)

        try:
            return deserializer(self.request.body)
        except ValueError:
            raise
