from authentication import Authentication
from authentication import NoAuthentication
from authentication import SessionAuthentication
import serializers 
import deserializers
import exceptions
from django import http
from django.conf import settings
from django.db import connection
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
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

        # Make sure all method names declared in ``filters`` are defined in the
        # class
        for f in cls.filters:
            if not hasattr(cls, f):
                raise ImproperlyConfigured('%s.filters is improperly configured' % name)
    
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

    # Filters, declared as strings. Each string indicate the method name of
    # each filter. Every method accepts parameters:
    #   ``(self, data, request, *args, **kwargs)``
    # It should define all its logic, and return a subset of ``data``.
    # This generic scheme, requires that we write some code for every filter,
    # but is very flexible and powerful.
    filters = []

    # Default item per page, when pagination is requested
    items_per_page = 10

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
            data, pagination = self.process(request, *args, **kwargs)
            
            # postprocess
            response_data, headers = self.postprocess(
                data, pagination, request, *args, **kwargs
            )
        except Exception, e:
            # If exception, return the appropriate http. HttpResponse object
            return exceptions.handle_exception(e, request)

        return self.response(response_data, headers)

    def preprocess(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``.
        Preprocesses the request.
        """
        self.authentication_hook(request, *args, **kwargs)

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

    def authentication_hook(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``

        Hook that adds ``authentication`` related data to the ``request``
        object. For example, on a handler with SignatureAuthentication, it
        could set the ``request.user`` parameter according to some querystring
        parameter.
        """
        pass

    def is_method_allowed(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``.

        If the request method is allowed, returns True.
        
        Raises ``exceptions.MethodNotAllowed`` exception otherwise.
        """
        if request.method.upper() not in self.http_methods:
            raise exceptions.MethodNotAllowed(self.http_methods)
        return True

    def deserialize_body(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``.

        If the request body is valid, according to ``Content-type`` header,
        it is deserialized to python data structures, and assigned to
        ``request.data``.

        Raises ``exceptions.UnsupportedMediaType`` or
        ``exceptions.BadRequest``.
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

    def process(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``.

        Calls the method that corresponds to the HTTP method, computes the
        result, and returns.
        
        Returns the tuple ``data, pagination``, where ``pagination`` is a
        dictionary with some pagination data. If no pagination was performed,
        ``pagination`` is {}.
        """
        data = getattr(self, request.method.lower())(request, *args, **kwargs)
        data, pagination = self.paginate(ordered_data, request, *args, **kwargs)
        return data, pagination

    def postprocess(self, data, pagination, request, *args, **kwargs):
        """
        Invoked by ``dispatch``.
        
        @param data         : Result of the handler's action
        @param pagination   : Dictionary with pagination data

        Postprocesses the data result of the operation.
        """
        # Serialize ``data`` to python data structures
        python_data = self.serialize_to_python(data, request)   
        # finalize any pending data processing
        self.finalize(data, request, *args, **kwargs)
        # Package the python_data to a dictionary
        pack = self.package(python_data, pagination, request, *args, **kwargs)
        # Return serialized response plus any http headers, like
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
 
    def package(self, data, pagination, request, *args, **kwargs):
        """
        Invoked by ``postprocess``.

        @param pagination   : Dictionary with pagination data

        Returns the ``data`` packed in a dictionary along with other metadata
        """
        count = 1
        if isinstance(data, (dict, list, tuple, set)):
            count = len(data)

        ret = {'data': data, 'count': count}

        if pagination:
            ret['pagination'] = pagination
        if settings.DEBUG:
            ret['debug'] = self.debug_data(self, data, request, *args, **kwargs)
        return ret

    def finalize(self, data, request, *args, **kwargs):
        """
        Invoked by ``postprocess``

        @data: Result of the handler's action

        Deletes the data, in case of DELETE requests.
        """
        if request.method.upper() == 'DELETE':
            data.delete()

    def debug_data(self, data, request, *args, **kwargs):
        """
        Invoked by ``package``

        @data: Data dictionary.
        
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

    def response(self, data, headers={}):
        """
        Invoked by ``dispatch``

        @param data: Serialized data into text
        @param headers: Dictionary of key-value pairs, that will be used as
        response headers.

        Returns an ``http.HttpResponse`` object
        """
        res = http.HttpResponse(data)
        for key, value in headers.items():
            res[key] = value
        return res


class BaseHandler(HandlerControlFlow):
    """
    This class describes a base handler's real operation.
    """
    def get(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``

        Action method for GET requests
        """
        raise exceptions.NotImplemented
    
    def post(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``

        Action method for POST requests
        """
        raise exceptions.NotImplemented

    def put(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``

        Action method for PUT requests
        """
        raise exceptions.NotImplemented

    def delete(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``

        Action method for DELETE requests
        """
        raise exceptions.NotImplemented

    def validate(self, request, *args, **kwargs):
        """
        Simple hook for extra request body validations.
        """
        pass

    def filter_data(self, data, request, *args, **kwargs):
        """
        Invoked by  ``ModelHandler.get_data_set``. 
        On a ``BaseHandler`` it should be called explicitly. 
        I have defined it here, since it's generic enough to be 
        used by any type of handler.

        Applies all the filters declared in ``self.filters``, and returns the
        result.
        """
        for f in self.filters:
            data = getattr(self, f)(data, request, *args, **kwargs)
        return data            

    def order(self, data, request, *args, **kwargs):
        """
        Invoked by ``get_data_set``.

        Typically ordering is indicated by the ``order`` querystring parameter.
        Returns the ordered data.
        """
        order = request.GET.get('order', None)
        if order:
            return self.order_data(data, order, request, *args, **kwargs)

        return data

    def order_data(self, data, order, request, *args, **kwargs):
        """
        Invoked by ``order``

        @param order: ``order`` parameter value

        Override to specify ordering logic.
        """
        return data

    def paginate(self, data, request, *args, **kwargs):
        """
        Invoked by ``process``.

        Typically pagination is indicated by the ``page`` and ``ipp``
        querystring parameters. ``page`` indicates the requested page, and
        ``ipp`` indicates the items per page (default is ``self.items_per_page``).

        Returns (data_page, total_dict). ``total_dict`` is a dictionary
        containing extra pagination data. If data is not paginable, or invalid
        pagination data has been given, returns (data, {})
        """
        page = request.GET.get('page', None)
        if page:
            return self.paginate_data(data, page, request, *args, **kwargs)

        return data, {}

    def paginate_data(self, data, page, request, *args, **kwargs):
        """
        Invoked by ``paginate``.

        @param page: ``page`` parameter value

        Override to specify paging logic.
        """
        return data, {}


class ModelHandler(BaseHandler):
    """
    This class describes a Model handler's operation.
    """
    # Override to define the handler's model
    model = None

    def get(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``.

        Action method for GET requests.

        Raises ``exceptions.Gone``        
        """
        return self.get_data(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``

        Action method for POST requests. 
        For Bulk POST requests, I could have used ``bulk_create``. 
        This has many drawbacks though
        (https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create),
        so I've gone for the more conservative approach of one query per item.
        """
        # TODO: What kind of errors do I contemplate for here? How do I handle
        # them?
        if isinstance(request.data, self.model):
            request.data.save(force_insert=True)
        else:
            for instance in request.data:
                instance.save(force_insert=True)
        return request.data            

    def put(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``
        
        Action method for PUT requests.
        """
        # TODO: What kind of errors do I contemplate for here? How do I handle
        # them?
        if isinstance(request.data, self.model):
            request.data.save(force_update=True)
        else:
            for instance in request.data:
                instance.save(force_update=True)
        return request.data

    def delete(self, request, *args, **kwargs):
        """
        Invoked by ``dispatch``

        Action method for DELETE requests. It doesn't perform the actual delete
        query. We still want to keep the data intact, in order to output them
        in the response. Method ``finalize`` does so.
        """
        return self.get_data(request, *args, **kwargs)

    def get_data(self, request, *args, **kwargs):
        """
        Invoked by ``get``.

        Returns the data of the current operation. To do so, it uses methods
        ``get_data_item`` and ``get_data_set``. 
        
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

        Returns a model instance, if indicated correctly by kwargs, or None
        otherwise.

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

    def get_data_set(self, request, *args, **kwargs):        
        """
        Invoked by ``get_data``.

        Returns the dataset for plural operations. To do so, it uses methods
        ``get_working_set``, ``filter_data`` and ``order``.
        """
        data = self.get_working_set(request, *args, **kwargs)
        filtered_data = self.filter_data(data, request, *args, **kwargs)
        ordered_data = self.order(filtered_data, request, *args, **kwargs)

        return ordered_data

    def get_working_set(self, request, *args, **kwargs):
        """
        Invoked by ``get_data_set``.

        Returns the default queryset for the ModelHandler, on top of which other filters
        should be chained, in order to limit the data view.
        """
        return self.model.objects.all()

    def validate(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``.

        Raises ``exceptions.BadRequest``

        Extra request body validation step. It should map the contents of
        ``request.data``(which at this point are python data structures) to
        ``self.model`` instances, and validate them.
        """
        if request.method.upper() == 'POST':
            if isinstance(request.data, dict):
                request.data = self.model(**request.data)

            elif isinstance(request.data, list):
                request.data = map(lambda item: self.model(**item), request.data)                    
                

        elif request.method.upper() == 'PUT':
            # Find the relevant dataset on which the ``update`` will be applied
            dataset = self.get_data(request, *args, **kwargs)            

            # Now update it/them
            if isinstance(dataset, self.model):
                for key, value in request.data.items():
                    setattr(dataset, key, value)
            else:
                def update(instance):
                    for key, value in request.data.items():
                        setattr(instance, key, value)

                [update(instance) for instance in dataset]
            
            request.data = dataset

        try:
            self.clean_models(request, *args, **kwargs)        
        except exceptions.BadRequest:
            raise

    def clean_models(self, request, *args, **kwargs):
        """
        Invoked by ``preprocess``

        Calls full_clean() on the model instances in ``request.data``. Raises
        a ``exceptions.BadRequest`` exception at the first error.
        """
        for element in isinstance(request.data, self.model) and [request.data] or request.data:
            try:
                element.full_clean()
            except ValidationError, e:  
                # When a ValidationError exception e is raised by model.clean_fields, it has
                # the parameter:
                # e.message_dict = {'field1': 'error string', 'field2':  'error string, ...}
                # When it's raised by ``clean`` e has the parameter:
                # e.message_dict = {NON_FIELD_ERRORS: [<error string>]}
                raise exceptions.BadRequest(e.message_dict)

    def paginate_data(self, data, page, request, *args, **kwargs):
        """
        Invoked by ``paginate``.

        @param page: ``page`` parameter value

        Returns data_page, {'pages': <total pages>, 'items': <total items>}
        If for some reason we can't paginate data, returns (data, {})
        """
        ipp = request.GET.get('ipp', None) or self.items_per_page
        try:
            ipp = int(ipp)
        except ValueError:
            ipp = self.items_per_page

        paginator = Paginator(data, ipp)

        try:
            data_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger, TypeError):
            # TypeError: in case ``data`` is a single model instance
            return data, {}

        return data_page, {'total_pages': paginator.num_pages, 'total_items': paginator.count}



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
