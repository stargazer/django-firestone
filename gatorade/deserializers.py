"""
The ``deserializers`` module exposes the classes responsible for
deserializing the request bodies of incoming requests to python deta
structures, according to the ``Content-type`` header
"""
import json


class Deserializer(object):
    """
    """
    # Keeps track of which callable is responsible to deserialize every
    # supported ``Content-type``.
    MAPPER = {}
    
    @classmethod
    def get_deserializer(cls, request):
        """
        Returns the Deserializer subclass that's responsible to deserialize the
        given request body.
        Raises ValueError if given no Content-type, or an unsupported
        Content-type is given.
        """
        content_type = request['META'].get('CONTENT_TYPE')
        if content_type:
            deserializer = cls.MAPPER.get(content_type)
            if deserializer:
                return deserializer
        raise ValueError

    @classmethod
    def register(cls, content_type, deserializer):
        """
        @param: Sontent-type string
        @param: Dererializer class
       
        Registers the given ``deserializer`` callable as responsible for
        deserializing the Content-type given by ``content_type``
        """
        cls.MAPPER[content_type] = deserializer

def json_deserializer(request):
    """
    Deserializes the request body of Content-type ``application/json`` to a
    python data structure, and returns it.

    Raw request body data are read from ``request.body``
    See https://docs.djangoproject.com/en/1.5/ref/request-response/#django.http.HttpRequest.body
    """
    return json.loads(request.body)

Deserializer.register(json_deserializer, 'application/json')

###### Example usage
## Get serializer callable
# deserializer = Deserializer.get_deserializer()
## Deserialize request body and assign it to ``request.data``
#request.data = deserializer(request)



