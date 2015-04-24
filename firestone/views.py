from deserializer.mixins import DeserializationMixin
from django.views.generic import base


class APIView(base.View,
              DeserializationMixin):
    output_template = {}
    post_body_fields = []
    put_body_fields = []

    # Every HTTP verb method, should return an ``HTTPResponse`` object.
    def get(self, request, *args, **kwargs):
        raise NotImplemented

    def post(self, request, *args, **kwargs):
        raise NotImplemented

    def put(self, request, *args, **kwargs):
        raise NotImplemented

    def delete(self, request, *args, **kwargs):
        raise NotImplemented

    def head(self, request, *args, **kwargs):
        raise NotImplemented

    def patch(self, request, *args, **kwargs):
        raise NotImplemented

    def trace(self, request, *args, **kwargs):
        raise NotImplemented

    def option(self, request, *args, **kwargs):
        return super(BaseHandler, self, request, *args, **kwargs).\
            options(request, *args, **kwargs)
