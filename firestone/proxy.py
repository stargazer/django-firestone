"""
This module defines the ``Proxy`` class, which is the main view,
where all the requests are sent to by the url mapper.

Every ``Proxy`` instance can map to lots of handlers, with each handler responsible
for a separate authentication method. For every incoming request, the ``Proxy``
instance will run throuh all handlers, one-by-one, and the first one for whom
the request is authenticated, will serve it. If the request can't
authenticate for any of the handlers, the proxy returns a 403 status code.
The proxy expects that all handlers return an ``HttpResponse`` object.
"""
from django import http

class Proxy(object):
    def __init__(self, *args):
        self.handlers = tuple(args)

    def choose_handler(self, request, *args, **kwargs):
        """
        Returns the handler instance responsible to serve this request
        """
        for handler in self.handlers:
            h = handler()

            if h.authentication.is_authenticated(request, *args, **kwargs):
                # Mimicking what Django's class bades views ``as_view`` method
                # does. The benefit is that I don't have to pass them as input args
                # to any handler methods.
                h.request = request
                h.args = args
                h.kwargs = kwargs

                return h

        return None

    def __call__(self, request, *args, **kwargs):
        h = self.choose_handler(request, *args, **kwargs)
        if h:
            return h.dispatch()

        # This is the only HttpResponse returned outside of the handler.
        return http.HttpResponseForbidden()

