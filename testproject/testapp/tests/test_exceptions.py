"""
This module tests the behavior of the module ``firestone.exceptions``
"""
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.conf import settings
from django import http
import json


class TestAPIException(TestCase):

    def test_method_api_exception(self):
        request = RequestFactory().get('/')
        e = exceptions.APIException()

        self.assertRaises(
            NotImplementedError,
            e.get_response,
            request
        )


class TestMethodNotAllowed(TestCase):        
    def test_method_not_allowed(self):
        request = RequestFactory().get('/')
        e = exceptions.MethodNotAllowed([])
        self.assertEqual(e.status, 405)

        response= e.get_response(request)
        self.assertIsInstance(response, http.HttpResponseNotAllowed)


class TestBadRequest(TestCase):
    def test_bad_request(self):
        request = RequestFactory().get('/')
        e = exceptions.BadRequest()
        self.assertEqual(e.status, 400)

        response = e.get_response(request)
        self.assertIsInstance(response, http.HttpResponseBadRequest)


class TestGone(TestCase):
    def test_gone(self):
        request = RequestFactory().get('/')
        e = exceptions.Gone()
        self.assertEqual(e.status, 410)
        
        response = e.get_response(request)
        self.assertIsInstance(response, http.HttpResponseGone)


class TestUnprocessable(TestCase):
    def test_unprocessable(self):
        e = exceptions.Unprocessable()
        self.assertEqual(e.status, 422)


class TestUnsupportedMedia(TestCase):
    def test_unsupported_media_type(self):
        e = exceptions.UnsupportedMediaType()
        self.assertEqual(e.status, 415)


class TestNotAcceptable(TestCase):
    def test_not_acceptable(self):
        request = RequestFactory().get('/')
        e = exceptions.NotAcceptable()

        response = e.get_response(request)
        self.assertIsInstance(response, http.HttpResponse)
        self.assertEqual(response.status_code, 406)


class TestNotImplemented(TestCase):
    def test_not_implemented(self):
        e = exceptions.NotImplemented()
        self.assertEqual(e.status, 501)


class TestOtherException(TestCase):
    def test_other_exception(self):
        request = RequestFactory().get('/')

        try:
            raise TypeError()
        except Exception, e:
            exp = exceptions.OtherException(request)
        self.assertEqual(exp.status, 500)
        
        response = exp.get_response(request)
        self.assertIsInstance(response, http.HttpResponseServerError)

    def test_other_exception_email_crashes(self):
        request = RequestFactory().get('/')
        
        settings.DEBUG = False
        settings.EMAIL_CRASHES = True

        try:
            raise TypeError()
        except Exception, e:
            exp = exceptions.OtherException(request)
        self.assertEqual(exp.status, 500)

        response = exp.get_response(request)
        self.assertIsInstance(response, http.HttpResponseServerError)


