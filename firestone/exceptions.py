"""
This module exposes all the Exception classes that the ``django-firestone`` can
handle, as well as the exception handler.

When we don't want to catch and handle an exception but rather return the
corresponding HttpResponse, we should simply let the ``handle_exception``
function handle it.

Any exceptions other than the ones declared here (say, a python statement
raises a TypeError) that the ``handle_exception`` will handle, will be turned
into a Server error response.
"""
from serializers import serialize 
from django import http
from django.conf import settings
from django.views.debug import ExceptionReporter   
import sys


class APIException(Exception):
    def __init__(self):
        self.headers = {}

    def get_http_response_and_headers(self):
        return http.HttpResponse(), self.headers


class MethodNotAllowed(APIException):
    def __init__(self, allowed_methods=()):
        self.status=405
        self.allowed_methods = allowed_methods
        self.headers = {}

    def get_http_response_and_headers(self):
        return http.HttpResponseNotAllowed(self.allowed_methods), self.headers


class BadRequest(APIException):
    def __init__(self, errors=None):
        self.status = 400
        self.errors = errors
        self.body, self.headers = errors and serialize(errors) or ('', {})

    def get_http_response_and_headers(self):
        return http.HttpResponseBadRequest(self.body), self.headers


class Gone(APIException):
    def __init__(self):
        self.status = 410
        self.headers = {}

    def get_http_response_and_headers(self):        
        return http.HttpResponseGone(), self.headers


class Unprocessable(APIException):
    def __init__(self, errors=None):
        self.status = 422
        self.errors = errors
        self.body, self.headers = errors and serialize(errors) or ('', {})

    def get_http_response_and_headers(self):
        return http.HttpResponse(self.body, status=self.status), self.headers


class UnsupportedMediaType(APIException):
    def __init__(self):
        self.status = 415
        self.headers = {}

    def get_http_response_and_headers(self):        
        return http.HttpResponse(status=self.status), self.headers


class NotImplemented(APIException):
    def __init__(self):
        self.status = 501
        self.headers = {}
    
    def get_http_response_and_headers(self):
        return http.HttpResponse(status=self.status), self.headers


class OtherException(Exception):
    def __init__(self, request):
        """
        @param e: Some Exception instance

        Any exceptions that was left uncaught and is not an instance of
        ``APIException``, is handled here. We consider it a Server Error.
        If DEBUG==True, we return an error in the response. Else, we email the
        administrator.
        """
        self.status = 500
        self.request = request

    def get_http_response_and_headers(self):
        exc_type, exc_value, traceback = sys.exc_info()
        reporter = ExceptionReporter(
            self.request, 
            exc_type, 
            exc_value,
            traceback.tb_next
        )
        html = reporter.get_traceback_html()

        if settings.DEBUG:
            http_response = http.HttpResponseServerError(
                html,
            )
        else:
            http_response = http.HttpResponseServerError()
            # TODO: and send email

        headers = {'content-type': 'text/html; charset=utf-8'}
        return http_response, headers


# TODO: This function is obsolete, since the
# HandlerControlFlow.handle_exception is used instead. Delete it,and remove its
# corresponding tests.
def handle_exception(e, request):
    # If exception ``e`` is of type APIException, we simply return the
    # corresponding HttpResponse object.
    if isinstance(e, APIException):
        return e.get_http_response_and_headers()

    # Else, we make it an OtherException, and return a HttpResponse 500 object
    else:
        exc = OtherException(request)
        return exc.get_http_response_and_headers()

