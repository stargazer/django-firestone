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
        self.assertItemsEqual(headers, {})

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


class TestHandleException(TestCase):
    """
    Testing whether the exceptions raised, are handled correctly by function
    ``handle_exception`` and generate the correct Http Response
    object.
    """
    def test_method_not_allowed(self):
        request = RequestFactory().get('/')

        allowed_methods = ()
        try:
            raise exceptions.MethodNotAllowed(allowed_methods)
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response['Allow'], '')
        self.assertItemsEqual(headers, {})
        
        allowed_methods = ('GET', 'POST')
        try:
            raise exceptions.MethodNotAllowed(allowed_methods)
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response['Allow'], ', '.join(allowed_methods))

    def test_bad_request(self):
        request = RequestFactory().get('/')
        
        try:
            raise exceptions.BadRequest
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 400) 
        self.assertEqual(response.content, '')
        self.assertItemsEqual(headers, {})


        content = 'some error here'
        try:
            raise exceptions.BadRequest(content)
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 400) 
        self.assertJSONEqual(response.content, json.dumps(content))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})

        content = {'error1': 'description', 'error2': 'description'}
        try:
            raise exceptions.BadRequest(content)
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 400) 
        self.assertJSONEqual(response.content, json.dumps(content))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})

    def test_gone(self): 
        request = RequestFactory().get('/')
        
        try:
            raise exceptions.Gone
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 410) 
        self.assertItemsEqual(headers, {})

    def test_unprocessable(self): 
        request = RequestFactory().get('/')
        
        try:
            raise exceptions.Unprocessable
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.content, '')
        self.assertItemsEqual(headers, {})

        content = 'some error here'
        try:
            raise exceptions.Unprocessable(content)
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 422) 
        self.assertJSONEqual(response.content, json.dumps(content))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})
        
        content = {'error1': 'description', 'error2': 'description'}
        try:
            raise exceptions.Unprocessable(content)
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 422) 
        self.assertJSONEqual(response.content, json.dumps(content))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})

    def test_unsupported_media_type(self):
        request = RequestFactory().get('/')

        try:
            raise exceptions.UnsupportedMediaType
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 415)
        self.assertItemsEqual(headers, {})

    def test_not_implemented(self):
        request = RequestFactory().get('/')

        try:
            raise exceptions.NotImplemented
        except Exception, e:
            response, headers = exceptions.handle_exception(e, request)
        self.assertEqual(response.status_code, 501)            
        self.assertItemsEqual(headers, {})

    def test_other_exception_debug_false(self):
        # With settings.DEBUG = False, the response should be empty
        request = RequestFactory().get('/')
        settings.DEBUG = False

        try:
            raise TypeError
        except TypeError, e:
            response, headers = exceptions.handle_exception(e, request)

        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.content)
        self.assertItemsEqual(headers, {'content-type': 'text/html; charset=utf-8'})

    def test_other_exception_debug_true(self):
        # With settings.DEBUG = False, the response should be non empty
        request = RequestFactory().get('/')
        settings.DEBUG = True

        try:
            raise TypeError
        except TypeError, e:
            response, headers = exceptions.handle_exception(e, request)

        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.content)
        self.assertItemsEqual(headers, {'content-type': 'text/html; charset=utf-8'})


