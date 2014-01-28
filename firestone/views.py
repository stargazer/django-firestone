class View(object):
    def __init__(self, *args):
        self.handlers = tuple(args)

    def __call__(self, request, *args, **kwargs):
        for handler in self.handlers:
            h = handler()

            # Mimics the behavior of Django's class based views ``as_view`` method
            h.request = request
            h.args = args
            h.kwargs = kwargs

            if h.authentication.is_authenticated(request, *args, **kwargs):
                return h.execute(request, *args, **kwargs)

                        
