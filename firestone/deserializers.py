"""
The ``deserializers`` module exposes the classes responsible for
deserializing the request bodies of incoming requests to python deta
structures, according to the ``Content-type`` header
"""
import exceptions
import json
import urlparse


def _json_deserializer(data):
    try:
        return json.loads(data)
    except ValueError:
        raise


def _form_encoded_data_deserializer(data):
    # param ``data`` is a string (querystring format)
    try:
        # dic is in the form ``key: [value]``
        dic = urlparse.parse_qs(data, strict_parsing=True)
    except ValueError:
        raise

    # I transform ``dic`` in the form ``key: value``, by taking only the first
    # vaule of each key
    return {key: value[0] for key, value in dic.iteritems()}

MAPPER = {
    'application/json': _json_deserializer,
    'application/x-www-form-urlencoded': _form_encoded_data_deserializer,
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
        raise exceptions.BadRequest('Invalid data')


def deserialize_request_body(request, *args, **kwargs):
    """
    Deserializes the request body, according to its Content-Type header
    """
    try:
        return deserialize(request.body,
                           request.META.get('CONTENT_TYPE', None))
    except (exceptions.UnsupportedMediaType, exceptions.BadRequest):
        raise
