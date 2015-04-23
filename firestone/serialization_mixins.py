"""
This module implements the functionality for response serialization.
API handler classes can inherit the functionality of any of these mixins.
"""


class SerializationMixin(object):
    """
    Any API handler that inherits from this Mixin or any of its children
    classes, inherits the ``serialize`` method, which returns the serialized
    response.
    """
    def serialize(self):
        raise NotImplemented

class JSONSerializationMixin(SerializationMixin):
    def serialize(self):
        pass
    
