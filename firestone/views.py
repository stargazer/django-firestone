

class View():
    def __init__(self, args):
        if not isinstance(args, list):
            args = args,
        self.handlers = tuple(args)

    def __call__(self, request, *args, **kwargs):
        for handler in self.handlers:
            h = handler()
            if h.authentication.is_authenticated(request, *args, **kwargs):
                return h.execute(request, *args, **kwargs)

                        
