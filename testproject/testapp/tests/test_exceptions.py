"""
This module tests the behavior of the module ``firestone.exceptions``
"""
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.conf import settings
from django import http
import json


class TestAPIExceptionInstantiation(TestCase):

    def test_method_api_exception(self):
        e = exceptions.APIException()

        response, headers = e.get_http_response_and_headers()
        self.assertIsInstance(response, http.HttpResponse)
        self.assertItemsEqual(headers, {})

    def test_method_not_allowed(self):
        e = exceptions.MethodNotAllowed([])
        self.assertEqual(e.status, 405)


        response, headers = e.get_http_response_and_headers()
        self.assertIsInstance(response, http.HttpResponseNotAllowed)
        self.assertItemsEqual(headers, {})

    def test_bad_request(self):
        e = exceptions.BadRequest()
        self.assertEqual(e.status, 400)

        response, headers = e.get_http_response_and_headers()
        self.assertIsInstance(response, http.HttpResponseBadRequest)
        self.assertItemsEqual(headers, {'content-type': 'application/json'})

    def test_gone(self):
        e = exceptions.Gone()
        self.assertEqual(e.status, 410)
        
        response, headers = e.get_http_response_and_headers()
        self.assertIsInstance(response, http.HttpResponseGone)
        self.assertItemsEqual(headers, {})

    def test_unprocessable(self):
        e = exceptions.Unprocessable()
        self.assertEqual(e.status, 422)

    def test_unsupported_media_type(self):
        e = exceptions.UnsupportedMediaType()
        self.assertEqual(e.status, 415)

    def test_not_implemented(self):
        e = exceptions.NotImplemented()
        self.assertEqual(e.status, 501)

    def test_other_exception(self):
        request = RequestFactory().get('/')

        try:
            raise TypeError()
        except Exception, e:
            exp = exceptions.OtherException(request)
        self.assertEqual(exp.status, 500)
        
        response, headers = exp.get_http_response_and_headers()
        self.assertIsInstance(response, http.HttpResponseServerError)
        self.assertItemsEqual(headers, {'content-type': 'text/html; charset=utf-8'})


