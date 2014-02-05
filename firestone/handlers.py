from authentication import Authentication
from authentication import NoAuthentication
from authentication import DjangoAuthentication
import serializers 
import deserializers
import exceptions
from django import http
from django.conf import settings
from django.db import connection
from preserialize import serialize as preserializer


class HandlerMetaClass(type):
    def __new__(meta, name, bases, attrs):
        """
        Metaclass magic for preprocessing some of the handler class's
        parameters.
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

        # Transform to sets
        cls.post_body_fields = set(cls.post_body_fields)
        cls.put_body_fields = set(cls.put_body_fields)

        return cls


class HandlerControlFlow(object):
    """
    This class describes the basic control flow and outer shell operations of any handler. 
    Basically the generic behavior is set here, whereas more specific behavior
    that corresponds to HTTP methods are  described in its subclasses.
    
    Don't subclass it.
    """
    __metaclass__ = HandlerMetaClass

    # Override to define the handler's output representation. It should follow
    # the syntax of ``django-preserialize`` templates.
    # See <https://github.com/bruth/django-preserialize#conventions>
    template = {}     

    # List of allowed HTTP methods.
    http_methods = []

    # authentication method: Should be an instance of any of the classes in the
    # ``authentication`` module, other than ``Authentication``
    authentication = None

    # Allowed request body fields for POST and PUT requests
    post_body_fields = put_body_fields = []    

    def dispatch(self, request, *args, **kwargs):
        """
        Entry point. Coordinates pre and post processing actions, as well as
        selects and calls the main action method.
        It needs to return an http.HttpResponse object.

        Don't override this method.
        """
        try:
            # preprocess
            self.preprocess(request, *args, **kwargs)
            # process
            data = getattr(self, request.method.lower())(request, *args, **kwargs)
            # postprocess
            data, headers = self.postprocess(data, request, *args, **kwargs)
        except Exception, e:
            # If exception, return the appropriate http. HttpResponse object
            return exceptions.handle_exception(e, request)

        # create and return response
        res = http.HttpResponse(data)
        for key, value in headers.items():
            res[key] = value
        return res

    def preprocess(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``.
        Preprocesses the request.
        """
        # Is the request method allowed?
        try:
            self.is_method_allowed(request, *args, **kwargs)
        except exceptions.MethodNotAllowed:
            raise
        
        if request.method.upper() not in ('POST', 'PUT'):
            return

        # Transform request body to python data structures
        try:
            self.deserialize_body(request, *args, **kwargs)
        except (exceptions.UnsupportedMediaType, exceptions.BadRequest):
            raise

        # Remove disallawed request body fields
        self.cleanse_body(request, *args, **kwargs)
        # Validate request body
        self.validate(request, *args, **kwargs)

    def is_method_allowed(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``.

        Is the request method allowed? Returns True, else raises an
        ``exceptions.MethodNotAllowed`` exception.
        """
        if request.method.upper() not in self.http_methods:
            raise exceptions.MethodNotAllowed(self.http_methods)
        return True

    def deserialize_body(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``.

        Is the request body valid according the ``Content-type`` header? 
        If yes, deserializes to python data structures and assigns to
        ``request.data``.
        Else raises ``exceptions.UnsupportedMediaType`` or ``exceptions.BadRequest``.
        """
        try:
            request.data = deserializers.deserialize_request_body(request, *args, **kwargs)
        except (exceptions.UnsupportedMediaType, exceptions.BadRequest):
            raise

    def cleanse_body(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``.

        Scans request body and only lets the allowed fields go through.
        Modifies ``request.data`` in place.
        """
        if request.method.upper() == 'POST':
            if isinstance(request.data, dict):
                for key in request.data.keys():
                    if key not in self.post_body_fields:
                        request.data.pop(key)

            if isinstance(request.data, list):
                for dic in request.data:
                    for key in dic.keys():
                        if key not in self.post_body_fields:
                            dic.pop(key)

        elif request.method.upper() == 'PUT':
            for key in request.data.keys():
                if key not in self.put_body_fields:
                    request.data.pop(key)

    def validate(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``.

        Extra request body validation step. For ModelHandler subclasses it
        should map ``request.data`` to model instances. For BaseHandler
        subclasses, it's a simple hook.
        """
        pass

    def postprocess(self, data, request, *args, **kwargs):
        """
        Invoked by ``dispatch``.
        
        @param data   : Result of the handler's action

        Postprocesses the data result of the operation.
        """
        # Serialize to python
        data = self.serialize_to_python(data, request)   
        # Package it to a dictionary
        pack = self.package(data, request, *args, **kwargs)
        # Returns serialized response plus any http headers, like
        # ``content-type`` that need to be passed in the HttpResponse instance.
        serialized, headers = serializers.serialize_response_data(pack, request, *args, **kwargs)
        
        return serialized, headers

    def serialize_to_python(self, data, request):
        """
        Invoked by ``postprocess``.

        @param data   : Result of the handler's action

        Serializes ``data`` to python data structures, according to the
        handler's ``template`` attribute, or request-level field selection
        defined by querystring parameter ``field``.
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
            return preserializer.serialize(data, **template)

        return preserializer.serialize(data, **self.template)
 
    def package(self, data, request, *args, **kwargs):
        """
        Invoked by ``postprocess``

        @data: Python data structures, as returned by ``serialize_to_python``.

        Returns the ``data`` packed in a dictionary along with other metadata
        """
        count = 1
        if isinstance(data, (dict, list, tuple, set)):
            count = len(data)

        ret = {'data': data, 'count': count}
        if settings.DEBUG:
            ret['debug'] = self.debug_data(self, data, request, *args, **kwargs)
        return ret

    def debug_data(self, data, request, *args, **kwargs):
        """
        Invoked by ``package``

        @data: Dictionary with ``data`` and ``count`` keys.
        
        Returns the ``data`` dictionary enriched with debugging data or stats
        about this request.
        """
        time_per_query = [float(dic['time']) for dic in connection.queries if 'time' in dic]
        
        # Tweaking ``connection.queries`` to increase query readability
        connection.queries = [{
                'time': item['time'], 
                'sql': item['sql'].replace('"', '')
            } 
            for item in connection.queries
        ]
        
        return {               
            'total_query_time': sum(time_per_query),
            'query_count': len(connection.queries),
            'query_log': connection.queries,
        }


class BaseHandler(HandlerControlFlow):
    """
    This class describes a handler's real operation.
    """
    def get(self, request, *args, **kwargs):
        return self.get_data(request, *args, **kwargs)

    def get_data(self, request, *args, **kwargs):
        """
        Invoked by ``get``.

        Returns the data of the current operation. To do so, it uses methods
        ``get_data_item`` and ``get_data_set``.
        
        Applies for both BaseHandler and ModelHandler.

        Raises ``exceptions.Gone``
        """
        try:
            data = self.get_data_item(request, *args, **kwargs)
        except exceptions.Gone:
            raise
        if data is None:
            data = self.get_data_set(request, *args, **kwargs)
        return data

    def get_data_item(self, request, *args, **kwargs):
        """
        Invoked by ``get_data``.

        Returns the data item for singular operations. Returns None if not
        applicable.
        
        Applies for both BaseHandler and ModelHandler.
        """
        return None

    def get_data_set(self, request, *args, **kwargs):        
        """
        Invoked by ``get_data``.

        Returns the dataset for plural operations. To do so, it uses method
        ``get_working_set``.
        
        Applies for both BaseHandler and ModelHandler.
        """
        return self.get_working_set(request, *args, **kwargs)

    def get_working_set(self, request, *args, **kwargs):
        """
        Invoked by ``get_data_set``.

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
        """
        Invoked by ``get_data``.

        Raises ``exceptions.Gone``
        """
        for field in kwargs.keys():
            if self.model._meta.get_field(field).unique:
                value = kwargs.get(field)
                if value is not None:
                    try:
                        return self.get_working_set(self, request, *args, **kwargs).get(**{field: value})
                    except (self.model.DoesNotExist, ValueError, TypeError):
                        raise exceptions.Gone

    def get_working_set(self, request, *args, **kwargs):
        """
        Invoked by ``get_data_set``.

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
