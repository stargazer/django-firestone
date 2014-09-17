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
from firestone import serializers
from django import http
from django.conf import settings
from django.views.debug import ExceptionReporter
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.mail import EmailMessage
import sys


class APIException(Exception):
    def __init__(self):
        pass

    def get_response(self, request):
        raise NotImplementedError


class MethodNotAllowed(APIException):
    def __init__(self, allowed_methods=()):
        self.status = 405
        self.allowed_methods = allowed_methods

    def get_response(self, request):
        return http.HttpResponseNotAllowed(self.allowed_methods)


class BadRequest(APIException):
    def __init__(self, errors=None):
        """
        Entering here, ``errors`` might be:
            1) Dictionary:
            {
                    <field1>: <error>,
                    <field2>: <error>,
                    ...
                    '__all__': [<error>,]
            }
            or String:
                    '<error>'

        We process it and make sure it's always a dictionary. So the latter
        case would become:
            {
                    '__all__': ['<error>']
            }
        """
        self.status = 400
        # If it's a string, make it a dictionary
        if isinstance(errors, basestring):
            errors = {NON_FIELD_ERRORS: (errors,)}
        self.errors = errors

    def get_response(self, request):
        s = serializers.SerializerMixin()
        s.request = request

        body, headers = s.serialize(self.errors,
                                    s.DEFAULT_SERIALIZATION_FORMAT)

        res = http.HttpResponseBadRequest(body)
        for key, value in headers.items():
            res[key] = value
        return res


class Gone(APIException):
    def __init__(self):
        self.status = 410

    def get_response(self, request):
        return http.HttpResponseGone()


class Unprocessable(APIException):
    def __init__(self, errors=None):
        self.status = 422
        self.errors = errors

    def get_response(self, request):
        body, headers = ('', {})
        if self.errors:
            s = serializers.SerializerMixin()
            s.request = request

            body, headers = s.serialize(self.errors,
                                        s.DEFAULT_SERIALIZATION_FORMAT)

        res = http.HttpResponse(body, status=self.status)
        for key, value in headers.items():
            res[key] = value
        return res


class UnsupportedMediaType(APIException):
    def __init__(self):
        self.status = 415

    def get_response(self, request):
        return http.HttpResponse(status=self.status)


class NotAcceptable(APIException):
    """
    When the response's data cannot be serialized into the requested
    serialization format, as set in the request's Accept Header
    """
    def __init__(self):
        self.status = 406

    def get_response(self, request):
        return http.HttpResponse(status=self.status)


class NotImplemented(APIException):
    def __init__(self):
        self.status = 501

    def get_response(self, request):
        return http.HttpResponse(status=self.status)


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

    def get_response(self, request):
        exc_type, exc_value, traceback = sys.exc_info()
        reporter = ExceptionReporter(
            request,
            exc_type,
            exc_value,
            traceback.tb_next
        )
        html = reporter.get_traceback_html()
        http_response = http.HttpResponseServerError()

        if settings.DEBUG:
            http_response = http.HttpResponseServerError(
                html,
                content_type='text/html; charset=utf-8'
            )
        elif getattr(settings, 'EMAIL_CRASHES', False):
            # Send Email Crash Report
            subject = 'django-firestone crash report'
            message = EmailMessage(
                subject=settings.EMAIL_SUBJECT_PREFIX + subject,
                body=html,
                from_email=settings.SERVER_EMAIL,
                to=[admin[1] for admin in settings.ADMINS]
            )
            message.content_subtype = 'html'
            message.send(fail_silently=True)

        return http_response
