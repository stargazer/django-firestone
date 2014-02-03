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

            # I could very well mimic the behavior of Django's class based
            # views ``as_view`` method, which assigns request, args, kwargs to
            # the view/handler instance. But there really is no reason, since I
            # pass them to every method as arguments.
            # h.request = request
            # h.args = args
            # h.kwargs = kwargs
            if h.authentication.is_authenticated(request, *args, **kwargs):
                return h

        return None

    def __call__(self, request, *args, **kwargs):
        h = self.choose_handler(request, *args, **kwargs)
        if h:
            return h.dispatch(request, *args, **kwargs)

        # This is the only HttpResponse returned outside of the handler.
        return http.HttpResponseForbidden()
                        
