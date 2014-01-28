from authentication import Authentication
from authentication import NoAuthentication
from authentication import DjangoAuthentication
from django import http
from preserialize.serialize import serialize

class HandlerMeta(type):
    def __new__(meta, name, bases, attrs):
        """
        Metaclass magic for preprocessing some of the handler class's
        paramaters.
        """
        cls = type.__new__(meta, name, bases, attrs)

        # Uppercase all HTTP methods
        cls.http_methods = [method.upper() for method in cls.http_methods]

        # Making sure that the handler's ``authentication`` parameter is
        # initialized correctly
        if not cls.authentication:
            cls.authentication = NoAuthentication()
        elif isinstance(cls.authentication, Authentication):
            pass
        else:
            cls.authentication = cls.authentication()

        return cls


class HandlerDataFlow():
    """
    This class describes the basic data flow and outer shell operations of any handler. 
    Basically the generic behavior is set here, whereas more specific behavior is described in
    its child classes.
    
    Don't inherit directly from this class.
    """
    __metaclass__ = HandlerMeta

    # Override to define the handler's output representation. It should follow
    # the syntax of ``django-preserialize`` templates.
    # See <https://github.com/bruth/django-preserialize#conventions>
    template = {}     

    # List of allowed HTTP methods.
    http_methods = []

    # authentication method: Should be an instance of any of the classes in the
    # ``authentication`` module, other than ``Authentication``
    authentication = None

    def execute(self, request, *args, **kwargs):
        """
        Entry point. Coordinates pre and post processing actions, as well as
        selects and calls the main action method.
        Don't override this method.

        Normally the ``View.dispatch`` method, simply checks whether the
        request's HTTP method is allowed, and if yes, invokes the corresponding
        view method that carries out the operation. 
        In this case though, they are many more checks and validations that I'd
        like to perform before actually invoking the corresponding view method.
        All these are performed in the ``preprocess``.
        Once this is done, I then call ``dispatch``.
        """
        error = self.is_method_allowed(request, *args, **kwargs)
        if isinstance(error, http.HttpResponse):
            return error

        action = getattr(self, request.method.lower())
        data = action(request, *args, **kwargs)

        final_data = self.postprocess(request, data, *args, **kwargs)

        # create response and return it
        return HttpResponse(final_data)

    def is_method_allowed(self, request, *args, **kwargs):
        """
        Is the request method allowed? If not, returns an
        HTTPResponse object, which ``dispatch`` will let bubble up.
        """
        # Is this type of request allowed?
        if request.method.upper() not in self.http_methods:
            return http.HttpResponseNotAllowed(self.http_methods)

    def preprocess(self, request, *args, **kwargs):
        """
        Preprocess the request
        """
        pass

    def postprocess(self, request, data, *args, **kwargs):
        """
        Postprocess the data result
        """
        data = self.serialize_to_python(request, data)   

        # serialize to JSON

        return data

    def serialize_to_python(self, request, data):
        """
        @param request: Incoming HTTPRequest object
        @param data   : Result of the handler's action

        Serializes the output of a handler's action to python data structures, 
        according to the definition of the handler's ``template`` variable, or
        to reqeust level field selection, by querystring parameter ``field``.
        """
        # NOTE: The request level field selection doesn not work if the
        # handler's ``template`` attribute uses ``django-preserialize``'s
        # pseudo selectors
        # See <https://github.com/bruth/django-preserialize#my-model-has-a-ton-of-fields-and-i-dont-want-to-type-them-all-out-what-do-i-do>
        # It only works when the ``fields`` are defined one by one in a list.
        field_selection = set(request.GET.getlist('field'))
        if field_selection:
            intersection = field_selection.intersection(set(self.template['fields']))
            template = {key: value for key, value in self.template.items()}
            template['fields'] = intersection
            return serialize(data, **template)

        return serialize(data, **self.template)
 
class BaseHandler(HandlerDataFlow):
    """
    This class describes a handler's real operation.
    """
    def get_data(self, request, *args, **kwargs):
        """
        Returns the data of the current operation. To do so, it uses methods
        ``get_data_item`` and ``get_data_set``.
        
        Applies for both BaseHandler and ModelHandler.
        """
        data = self.get_data_item(request, *args, **kwargs)
        if data is None:
            data = self.get_data_set(request, *args, **kwargs)
        return data

    def get_data_item(self, request, *args, **kwargs):
        """
        Returns the data item for singular operations. Returns None if not
        applicable.
        
        Applies for both BaseHandler and ModelHandler.
        """
        return None

    def get_data_set(self, request, *args, **kwargs):
        """
        Returns the dataset for plural operations. To do so, it uses method
        ``get_working_set``.
        
        Applies for both BaseHandler and ModelHandler.
        """
        return self.get_working_set(request, *args, **kwargs)

    def get_working_set(self, request, *args, **kwargs):
        """
        Returns the operation's base dataset.
        """
        return None


class ModelHandler(BaseHandler):
    """
    This class describes a Model handler's operation.

    Returns the model instance if indicated correctly by kwargs, or raises
    self.ObjectDoesNotExist
    """
    
    # Override to define the handler's model
    model = None

    def get_data_item(self, request, *args, **kwargs):
        for field in kwargs.keys():
            if self.model._meta.get_field(field).unique:
                value = kwargs.get(field)
                if value is not None:
                    return self.get_working_set(self, request, *args, **kwargs).get(**{field: value})

    def get_working_set(self, request, *args, **kwargs):
        """
        Returns the default queryset for the ModelHandler, on top of which other filters
        should be chained, in order to limit the data view.
        """
        return self.model.objects.all()


"""
Example of BaseHandler
class RandomHandler(BaseHandler):
    user_template = {
        'fields': ['id', 'domain', 'email'],
    }
    push_template = {
        'fields': ['id', 'creator'],
        'related': {
            'creator': user_template
        },
    }
    nouncy_template = {
        'fields': ['id', 'title', 'pushes', 'user'],
        'related': {
            'pushes': push_template,
            'user'  : user_template,
        },
    }
    # Say this handler outputs a dictionary like 
    # {'a': <value>, 'b': <value>, 'c': <Nouncy>}
    template = {
        'fields': ['a', 'b', 'nouncy'],
        'related': {
            'nouncy': nouncy_template,
        }
    }            
"""
"""
Example of ModelHandler
class ContactHandler(ModelHandler):
    model = Contact

    media_template = {
        'exclude': ['user',],
    }
    template = {
        'exclude': ['user',],
        'related': {
            'media': media_template,
        },
    }
"""
