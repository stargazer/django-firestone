from authentication import Authentication
from authentication import NoAuthentication
from serializers import SerializerMixin
from preserialize import serialize as preserializer
import deserializers
import exceptions
from django.conf import settings
from django.db import connection
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.signing import TimestampSigner
from endless_pagination.paginators import LazyPaginator
from itsdangerous import TimedJSONWebSignatureSerializer


class HandlerMetaClass(type):
    def __new__(meta, name, bases, attrs):
        """
        Metaclass magic for preprocessing some of the handler class's
        parameters.
        """
        # The handler class's ``authentication`` parameter is a class. Here we
        # make sure that this class becomes a superclass for the handler, so
        # that the handler will inherit its functionality, and will therefore
        # be able to use its ``is_authenticated`` method.
        if name not in ('BaseHandler', 'ModelHandler'):
            authentication = attrs.pop('authentication', None)
            if not authentication:
                bases += (NoAuthentication,)
            elif isinstance(authentication, Authentication):
                bases += (authentication,)
            else:
                bases += (authentication,)

        # Extend handler class with ``SerializerMixin`` class, so that it
        # inherits its methods
        bases += (SerializerMixin,)

        cls = type.__new__(meta, name, bases, attrs)

        # Uppercase all HTTP methods
        cls.http_methods = [method.upper() for method in cls.http_methods]

        # Transform to sets
        cls.post_body_fields = set(cls.post_body_fields)
        cls.put_body_fields = set(cls.put_body_fields)

        # Make sure all method names declared in ``filters`` are defined in the
        # class
        for f in cls.filters:
            if not hasattr(cls, f):
                raise ImproperlyConfigured(
                    '%s.filters is improperly configured' % name
                )

        return cls


class HandlerControlFlow(object):
    """
    This class describes the basic control flow and outer shell operations of
    any handler.
    Basically the very generic high-level behavior layout is defined here. Its
    more fine-grained parts are defined in classes ``BaseHandler`` and
    ``ModelHandler``.

    Don't subclass directly in a concrete handler class.
    """

    def dispatch(self):
        """
        Handler's entry point. Coordinates pre and post processing actions, as
        well as selects and calls the main action method.
        I would advice against overriding this method.

        Returns:
            http.HttpResponse object.
        """
        try:
            self.preprocess()
            data, pagination = self.process()
            dic = self.postprocess(
                data, pagination,
            )

            # If you want to alter the response object, override handler's
            # ``get_response`` method
            res = self.get_response(dic)

        except Exception, e:
            res = self.handle_exception(e)

        return res

    def preprocess(self):
        """
        Invoked by ``dispatch``.
        Preprocesses the request.

        Returns:
            None
        Raises:
            exceptions.MethodNotAllowed: if request method is not allowed
            exceptions.UnsupportedMediaType: if content-type is not supported
            exceptions.BadRequest: if request body is not valid according to
            content-type
        """
        self.authentication_hook()

        try:
            self.is_method_allowed()
        except exceptions.MethodNotAllowed:
            raise

        if self.request.method.upper() not in ('POST', 'PUT'):
            return

        # Transform request body to python data structures
        try:
            self.deserialize_body()
        except (exceptions.UnsupportedMediaType, exceptions.BadRequest):
            raise

        # Remove disallowed request body fields
        self.cleanse_body()
        # Validate request body
        self.validate()

    def process(self):
        """
        Invoked by ``dispatch``.
        Calls the method that corresponds to the HTTP method, computes the
        result, and returns.

        Returns:
            (data, pagination): ``data`` is the result of the operation
            and ``pagination`` is a dictionary with some pagination data.
            If no pagination was performed, ``pagination`` is {}.
        """
        data = getattr(self, self.request.method.lower())()
        data, pagination = self.paginate(data)
        return data, pagination

    def postprocess(self, data, pagination):
        """
        Invoked by ``dispatch``.
        Postprocesses the data result of the operation.

        Args:
            data: Result of operation
            pagination: Dictionary with pagination data
        Returns:
            Whole response data dictionary
        """
        self.inject_data_hook(data)
        # Serialize ``data`` to python data structures
        python_data = self.serialize_to_python(data)
        # finalize any pending data processing
        self.finalize_pending(data)
        # Package the python_data to a dictionary
        return self.package(python_data, pagination)

    def handle_exception(self, e):
        """
        Invoked by ``dispatch``
        Handles any exceptions that might have been raised

        Args:
            e: Exception instance
        Returns:
            (http_response, headers): ``http_response`` is an HttpResponse
            instance. ``headers`` is a dictionary of key-value pairs to be used
            as headers on the HttpResponse object.
        """
        if isinstance(e, exceptions.APIException):
            return e.get_response(self.request)
        else:
            exc = exceptions.OtherException(self.request)
            return exc.get_response(self.request)


class BaseHandler(HandlerControlFlow):
    """
    This class describes a Base handler's operation.
    """
    __metaclass__ = HandlerMetaClass

    # Override to define the handler's output representation. It should follow
    # the syntax of ``django-preserialize`` templates.
    # See <https://github.com/bruth/django-preserialize#conventions>
    template = {}

    # List of allowed HTTP methods.
    # GET, POST, PUT, PLURAL_PUT, DELETE, PLURAL_DELETE
    http_methods = []

    # authentication method: Should be an instance of any of the mixins in the
    # ``authentication`` module, other than ``Authentication``
    authentication = None

    # Parameters applicable for ``SignatureAuthentication`` mixin
    signer = TimestampSigner()  # Signing class
    sig_param = 's'             # Signature querysting parameter
    max_age_param = 'm'         # Max-age querystring parameter

    # Parameter applicatible for ``JWTAuthentication`` mixin. It defines the
    # signing class
    jwt_signer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY)

    # Allowed request body fields for POST and PUT requests
    post_body_fields = put_body_fields = []

    # Filters, declared as strings. Each string indicates the method name of
    # each filter. Every method's signature is ``(self, data)``
    # The method should define all its logic, and return a subset of ``data``.
    # This generic scheme, requires that we write some code for every filter
    # method, but is very flexible and powerful.
    filters = []

    # Default item per page, when pagination is requested
    items_per_page = 10

    # Defines whether metadata should be returned when pagination is used.
    # Generating metadata can, at times, perform costly queries.
    pagination_metadata = True

    # Filename of Excel attachment in case a request needs the response data
    # serialized to an excel file. Can be a string or a callable that returns a
    # string
    excel_filename = 'file.xls'

    def authentication_hook(self):
        """
        Invoked by ``preprocess``
        Hook that adds ``authentication`` related data to the ``request``
        object. For example, on a handler with SignatureAuthentication, it
        could set the ``request.user`` parameter according to some querystring
        parameter.

        Returns:
            None
        """
        pass

    def is_method_allowed(self):
        """
        Invoked by ``preprocess``.
        Checks whether the handler allowed the request's HTTP method.

        Returns:
            True
        Raises:
            exceptions.MethodNotAllowed: if request method is not allowed
        """
        if self.request.method.upper() not in self.http_methods:
            raise exceptions.MethodNotAllowed(self.http_methods)
        return True

    def deserialize_body(self):
        """
        Invoked by ``preprocess``.
        If the request body is valid, according to ``Content-type`` header,
        it is deserialized to python data structures, and assigned to
        ``request.data``.

        Returns:
            None
        Raises:
            exceptions.UnsupportedMediaType: if content-type is not supported
            exceptions.BadRequest: If request body is not valid according to
            content-type
        """
        try:
            self.request.data = deserializers.deserialize_request_body(
                self.request,
                *self.args,
                **self.kwargs
            )
        except (exceptions.UnsupportedMediaType, exceptions.BadRequest):
            raise

    def cleanse_body(self):
        """
        Invoked by ``preprocess``.
        Scans request body and only lets the allowed fields go through.


        Returns:
            None
        """
        if self.request.method.upper() == 'POST':
            if isinstance(self.request.data, dict):
                for key in self.request.data.keys():
                    if key not in self.post_body_fields:
                        self.request.data.pop(key)

            if isinstance(self.request.data, list):
                for dic in self.request.data:
                    for key in dic.keys():
                        if key not in self.post_body_fields:
                            dic.pop(key)

        elif self.request.method.upper() == 'PUT':
            for key in self.request.data.keys():
                if key not in self.put_body_fields:
                    self.request.data.pop(key)

    def inject_data_hook(self, data):
        """
        Invoked by ``postprocess``
        Hook that adds extra fields or data to ``data``. Override to add
        functionality.

        Args:
            data: Result of operation
        Returns:
            Modified ``data``.
        """
        return data

    def serialize_to_python(self, data):
        """
        Invoked by ``postprocess``.
        Serializes ``data`` to python data structures, according to the
        handler's ``template`` attribute, or request-level field selection
        defined by querystring parameter ``field``.

        Args:
            data: Result of the handler's operation
        Returns:
            Serialized data.
        """
        # NOTE: The request level field selection doesn not work if the
        # handler's ``template`` attribute uses ``django-preserialize``'s
        # pseudo selectors
        # See
        # <https://github.com/bruth/django-preserialize#my-model-has-a-ton-of-fields-and-i-dont-want-to-type-them-all-out-what-do-i-do>
        # It only works when the ``fields`` are defined one by one in a list.
        field_selection = set(self.request.GET.getlist('field'))
        if field_selection:
            intersection = field_selection.intersection(
                set(self.template['fields'])
            )
            template = {key: value for key, value in self.template.items()}
            template['fields'] = intersection
            return preserializer.serialize(data, **template)

        return preserializer.serialize(data, **self.template)

    def finalize_pending(self, data):
        """
        Invoked by ``postprocess``
        Performs any pending DELETE operations, in case of DELETE requests.
        Override to add functionality.

        Args:
            Result of the handler's action
        Returns:
            None
        """
        if self.request.method.upper() == 'DELETE':
            data.delete()

    def package(self, data, pagination):
        """
        Invoked by ``postprocess``.
        Wraps the ``data`` and ``pagiantion`` data a dictionary.

        Args:
            data: Data result of the handler's operation, serialized in python
            data structures
            pagination: Dictionary with pagination data
        Returns:
            Dictionary
        """
        count = 1
        if isinstance(data, (dict, list, tuple, set)):
            count = len(data)

        ret = {'data': data, 'count': count}

        if pagination:
            ret['pagination'] = pagination
        if settings.DEBUG:
            ret['debug'] = self.debug_data()
        return ret

    def debug_data(self):
        """
        Invoked by ``package``.

        Returns:
            Dictionary of debugging data about this request.
        """
        # Readable version of ``connection.queries``
        readable_connection_queries = [
            {
                'time': item['time'],
                'sql': item['sql'].replace('"', '')
            }
            for item in connection.queries
        ]

        return {
            'total_query_time': sum(
                [float(dic['time']) for dic in connection.queries]
            ),
            'query_count': len(connection.queries),
            'query_log': readable_connection_queries,
        }

    def patch_response(self, response, headers={}):
        """
        Invoked by ``dispatch``. Wraps data and headers in an HttpResponse
        object. Override to add more headers or modify any response attribute.

        Args:
            data: Data serialized in text
            headers: Dictionary of key-value pairs, that will be used as
            response headers.
        Returns:
            http.HttpResponse object.
        """
        for key, value in headers.items():
            response[key] = value
        return response

    def get(self):
        """
        Invoked by ``dispatch``.
        Action method for GET requests. Override to add functionality.
        """
        raise exceptions.NotImplemented

    def post(self):
        """
        Invoked by ``dispatch``.
        Action method for POST requests. Override to add functionality.
        """
        raise exceptions.NotImplemented

    def put(self):
        """
        Invoked by ``dispatch``.
        Action method for PUT requests. Override to add funcionality.
        """
        raise exceptions.NotImplemented

    def delete(self):
        """
        Invoked by ``dispatch``.
        Action method for DELETE requests. Override to add functionality.
        """
        raise exceptions.NotImplemented

    def get_data(self):
        """
        (Should be) Invoked by ``get``, ``delete``, and ``validate``

        Returns:
            Dataset of the current operation. To do so, it uses methods
            ``get_data_item`` and ``get_data_set``.
        Raises:
            exceptions.Gone
            exceptions.MethodNotAllowed
        """
        try:
            data = self.get_data_item()
        except exceptions.Gone:
            raise
        if data is None:
            # Since we are here, we know that it's definitely a plural request.
            # First check whether it is allowed.
            if self.is_catastrophic():
                raise exceptions.MethodNotAllowed(self.http_methods)
            # And then retrieve the actual data.
            data = self.get_data_set()

        return data

    def is_catastrophic(self):
        """
        Invoked by ``get_data``.
        Checks whether dangerous methods (Plural PUT, PLURAL DELETE) are
        allowed.

        Returns:
            True if method is catastrophic and not allowed
            False if allowed.
        """
        if (self.request.method.upper() == 'PUT'
            and 'PLURAL_PUT' not in self.http_methods) \
            or (self.request.method.upper() == 'DELETE'
                and 'PLURAL_DELETE' not in self.http_methods):
            return True
        return False

    def get_data_item(self):
        """
        Invoked by ``get_data``.

        It should return the data item for the operation if such exists,
        None otherwise.
        Override to add functionality.
        """
        raise exceptions.NotImplemented

    def get_data_set(self):
        """
        Invoked by ``get_data``.

        It should return returns the data set for operation.
        Override to add functionality.
        """
        raise exceptions.NotImplemented

    def validate(self):
        """
        Invoked by ``preprocess``.
        Simple hook for extra request body validations.

        Returns:
            None.
        """
        pass

    def filter_data(self, data):
        """
        Invoked by  ``get_data_set``, which only exists for the
        ``ModelHandler`` class. On a ``BaseHandler`` it should be called
        explicitly.
        It is defined it here, since it's generic enough to be used by any type
        of handler. Applies all the filters declared in ``self.filters``, and
        returns the result.

        Args:
            data: Initial working set of the handler
        Returns:
            Result of all filter applications

        """
        for f in self.filters:
            data = getattr(self, f)(data)
        return data

    def order(self, data):
        """
        Invoked by ``get_data_set``, which only exists for the ``ModelHandler``
        class. On a ``BaseHandler`` it should be called explicitly.
        Typically ordering is indicated by the ``order`` querystring parameter.

        Args:
            data: Filtered working set of the handler
        Returns:
            Ordered data.
        """
        order = self.request.GET.get('order', None)
        if order:
            return self.order_data(data, order)

        return data

    def order_data(self, data, order):
        """
        Invoked by ``order``
        Override to specify ordering logic.

        Args:
            order: Value of querystring parameter ``order``
        Returns:
            Ordered data
        """
        return data

    def paginate(self, data):
        """
        Invoked by ``process``.
        Typically pagination is indicated by the ``page`` and ``ipp``
        querystring parameters. ``page`` indicates the requested page, and
        ``ipp`` indicates the items per page (default is
        ``self.items_per_page``).

        Args:
            data: Result of the handler's data operation
        Returns:
            (data_page, metadata), where ``data_page`` is the page returned
            and ``metadata`` is a dictionary containing extra pagination data.
            If data is not paginable, or invalid pagination data has been
            given, it returns (data, {})
        """
        page = self.request.GET.get('page', None)
        if page:
            return self.paginate_data(data, page)

        return data, {}

    def paginate_data(self, data, page):
        """
        Invoked by ``paginate``.
        Override to specify paging logic.

        Args:
            data: Result of the handler's data operation
            page: Value of querystring parameter ``page``
        Returns:
            (data, {})
        """
        return data, {}


class ModelHandler(BaseHandler):
    """
    This class describes a Model handler's operation.
    """

    # Override to define the handler's model
    model = None

    def get(self):
        """
        Invoked by ``dispatch``.
        Action method for GET requests.

        Returns:
            Model instance or queryset
        Raises:
            Raises exceptions.Gone
        """
        return self.get_data()

    def post(self):
        """
        Invoked by ``dispatch``
        Action method for POST requests.

        Returns:
            Model instance or list of model instances
        Raises:
            TODO
        """
        # For Bulk POST requests, I could have used ``bulk_create``.
        # This has many drawbacks though
        # (https://docs.djangoproject.com/en/dev/ref/models/querysets/#bulk-create),
        # so I've gone for the more conservative approach of one query per
        # item.
        # TODO: What kind of errors do I contemplate for here? How do I handle
        # them?
        if isinstance(self.request.data, self.model):
            self.request.data.save(force_insert=True)
        else:
            for instance in self.request.data:
                instance.save(force_insert=True)
        return self.request.data

    def put(self):
        """
        Invoked by ``dispatch``
        Action method for PUT requests.

        Returns:
            Model instance or list of model instances
        Raises:
            TODO
        """
        # TODO: What kind of errors do I contemplate for here? How do I handle
        # them?
        if isinstance(self.request.data, self.model):
            self.request.data.save(force_update=True)
        else:
            for instance in self.request.data:
                instance.save(force_update=True)
        return self.request.data

    def delete(self):
        """
        Invoked by ``dispatch``
        Action method for DELETE requests. It doesn't perform the actual delete
        query. We still want to keep the data intact, in order to output them
        in the response. Method ``finalize`` performs the delete action.

        Returns:
            Model instance or queryset
        Raises:
            exceptions.Gone
        """
        return self.get_data()

    def get_data_item(self):
        """
        Invoked by ``get_data``.

        Returns:
            A model instance, if indicated correctly by kwargs, or None
            otherwise.
        Raises:
            exceptions.Gone
        """
        if self.kwargs:
            try:
                return self.get_working_set().get(**self.kwargs)
            except (self.model.DoesNotExist, ValueError, TypeError):
                raise exceptions.Gone

        return None

    def get_data_set(self):
        """
        Invoked by ``get_data``.

        Returns:
            Dataset for plural operations. To do so, it uses methods
            ``get_working_set``, ``filter_data`` and ``order``.
        """
        data = self.get_working_set()
        filtered_data = self.filter_data(data)
        ordered_data = self.order(filtered_data)

        return ordered_data

    def get_working_set(self):
        """
        Invoked by ``get_data_set``.

        Returns:
            Default queryset for the ModelHandler, on top of which other
            filters should be chained, in order to limit the data view.
        """
        return self.model.objects.all()

    def validate(self):
        """
        Invoked by ``preprocess``.
        Extra request body validation step. It should map the contents of
        ``request.data``(which at this point are python data structures) to
        ``self.model`` instances, and validate them.

        Returns:
            None
        Raises:
            exceptions.BadRequest
        """
        if self.request.method.upper() == 'POST':
            if isinstance(self.request.data, dict):
                self.request.data = self.model(**self.request.data)

            elif isinstance(self.request.data, list):
                self.request.data = map(
                    lambda item: self.model(**item), self.request.data
                )
        elif self.request.method.upper() == 'PUT':
            # Find the relevant dataset on which the ``update`` will be applied
            dataset = self.get_data()

            # Now update it/them
            if isinstance(dataset, self.model):
                for key, value in self.request.data.items():
                    setattr(dataset, key, value)
            else:
                def update(instance):
                    for key, value in self.request.data.items():
                        setattr(instance, key, value)

                [update(instance) for instance in dataset]

            self.request.data = dataset

        try:
            self.clean_models()
        except exceptions.BadRequest:
            raise

    def clean_models(self):
        """
        Invoked by ``validate``
        Calls ``full_clean()`` on all model instances in ``request.data``.

        Returns:
            None
        Raises:
            exceptions.BadRequest: When ``full_clean`` first throws a
            ValidationError. The exceptions.BadRequest exception is raised at
            the very first time that we encounter a ValidationError.
        """
        # TODO: Add the exclude parameter in the signature of the method.
        # Call full_clean with ``exclude``, so that we can exclude any models
        # fields we want from the validation.
        for element in isinstance(self.request.data, self.model) \
                and [self.request.data] or self.request.data:
            try:
                element.full_clean()
            except ValidationError, e:
                # When a ValidationError exception e is raised by
                # ``model.clean_fields``, it has the parameter:
                # e.message_dict = {'field1': 'error string',
                #                   'field2':  'error string, ...}
                # When it's raised by ``clean`` e has the parameter:
                # e.message_dict = {NON_FIELD_ERRORS: [<error string>]}
                raise exceptions.BadRequest(e.message_dict)

    def paginate_data(self, data, page):
        """
        Invoked by ``paginate``.

        Args:
            page: Value of querystring parameter ``page``
        Returns:
            (data_page, {'total_pages': <total pages>,
                         'total_items': <total items>})
            If for some reason we can't paginate data, or
            ``pagination_metadata`` is ``False``, returns (data, {})
        """
        ipp = self.request.GET.get('ipp', None) or self.items_per_page
        try:
            ipp = int(ipp)
        except ValueError:
            ipp = self.items_per_page

        if not self.pagination_metadata:
            paginator = LazyPaginator(data, ipp)
        else:
            paginator = Paginator(data, ipp)

        try:
            data_page = paginator.page(page)
        except (EmptyPage, PageNotAnInteger, TypeError):
            # TypeError: in case ``data`` is a single model instance
            return data, {}

        try:
            metadata = {
                'total_pages': paginator.num_pages,
                'total_items': paginator.count
            }
        except NotImplementedError:
            metadata = {}

        return data_page, metadata
