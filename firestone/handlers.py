from django.views.generic import base


class Handler(base.View):
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

    def deserialize(self):
        pass

    def debug_data(self):
        pass

    def exception_handler(self):
        pass




class ExampleHandler(Handler, 
                     NoAuthenticationMixin, 
                     JSONSerializer):
    def get(self):
        pass

    def post(self):
        pass


