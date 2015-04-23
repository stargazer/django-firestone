from django.views.generic import base


class BaseHandler(base.View):
    output_template = {}
    post_body_fields = []
    put_body_fields = []

    # Every HTTP verb method, should return an ``HTTPResponse`` object.
    def get(self):
        raise NotImplemented

    def post(self):
        raise NotImplemented

    def put(self):
        raise NotImplemented

    def delete(self):
        raise NotImplemented

    def head(self):
        raise NotImplemented

    def patch(self):
        raise NotImplemented

    def trace(self):
        raise NotImplemented

    def option(self):
        return super(APIView, self).\
               options(self.request, self.args, self.kwargs)



class ExampleHandler(BaseHandler, 
                     NoAuthenticationMixin, 
                     JSONSerializer):
    def get(self):
        pass

    def post(self):
        pass


