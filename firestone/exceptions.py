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
    pass

class MethodNotAllowed(APIException):
    def __init__(self, allowed_methods=()):
        self.status = 405
        self.http_response = http.HttpResponseNotAllowed(allowed_methods)

class BadRequest(APIException):
    def __init__(self, errors=None):
        self.status = 400
        self.errors = errors

        errors, headers = errors and serialize(errors) or ('', {})
        self.http_response = http.HttpResponseBadRequest(errors)
        for key, value in headers.items():
            self.http_response[key] = value

class Gone(APIException):
    def __init__(self):
        self.status = 410
        self.http_response = http.HttpResponseGone()

class Unprocessable(APIException):
    def __init__(self, errors=None):
        self.status = 422
        self.errors = errors

        errors, headers = errors and serialize(errors) or ('', {})
        self.http_response = http.HttpResponse(errors, status=422)
        for key, value in headers.items():
            self.http_response[key] = value

class UnsupportedMediaType(APIException):
    def __init__(self):
        self.status = 415
        self.http_response = http.HttpResponse(status=415)

class NotImplemented(APIException):
    def __init__(self):
        self.status = 501
        self.http_response = http.HttpResponse(status=501)

class OtherException(Exception):
    def __init__(self, e, request):
        """
        @param e: Some Exception instance

        Any exceptions that was left uncaught and is not an instance of
        ``APIException``, is handled here. We consider it a Server Error.
        If DEBUG==True, we return an error in the response. Else, we email the
        administrator.
        """
        self.status = 500
        exc_type, exc_value, traceback = sys.exc_info()
        reporter = ExceptionReporter(
            request, 
            exc_type, 
            exc_value,
            traceback.tb_next
        )
        html = reporter.get_traceback_html()

        if settings.DEBUG:
            self.http_response = http.HttpResponseServerError(
                html,
                content_type='text/html; charset=utf-8'
            )
        else:
            self.http_response = http.HttpResponseServerError()
            # and send email

def handle_exception(e, request):
    # If exception ``e`` is of type APIException, we simply return the
    # corresponding HttpResponse object.
    if isinstance(e, APIException):
        return e.http_response

    # Else, we make it an OtherException, and return a HttpResponse 500 object
    else:
        exc = OtherException(e, request)
        return exc.http_response

