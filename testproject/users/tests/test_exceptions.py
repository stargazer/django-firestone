"""
This module tests the behavior of the module ``firestone.exceptions``
"""
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django import http
import json


class TestAPIExceptionInstantiation(TestCase):

    def test_method_not_allowed(self):
        e = exceptions.MethodNotAllowed([])
        self.assertEqual(e.status, 405)
        self.assertIsInstance(e.http_response, http.HttpResponseNotAllowed)

    def test_method_bad_request(self):
        e = exceptions.BadRequest()
        self.assertEqual(e.status, 400)
        self.assertIsInstance(e.http_response, http.HttpResponseBadRequest)

    def test_gone(self):
        e = exceptions.Gone()
        self.assertEqual(e.status, 410)
        self.assertIsInstance(e.http_response, http.HttpResponseGone)

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
            exp = exceptions.OtherException(e, request)

        self.assertEqual(exp.status, 500)
        self.assertIsInstance(exp.http_response, http.HttpResponseServerError)


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
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res['Allow'], '')
        
        allowed_methods = ('GET', 'POST')
        try:
            raise exceptions.MethodNotAllowed(allowed_methods)
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 405)
        self.assertEqual(res['Allow'], ', '.join(allowed_methods))

    def test_bad_request(self):
        request = RequestFactory().get('/')
        
        try:
            raise exceptions.BadRequest
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 400) 
        self.assertEqual(res.content, '')

        content = 'some error here'
        try:
            raise exceptions.BadRequest(content)
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 400) 
        self.assertJSONEqual(res.content, json.dumps(content))
        self.assertEqual(res['content-type'], 'application/json')

        content = {'error1': 'description', 'error2': 'description'}
        try:
            raise exceptions.BadRequest(content)
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 400) 
        self.assertJSONEqual(res.content, json.dumps(content))
        self.assertEqual(res['content-type'], 'application/json')

    def test_gone(self): 
        request = RequestFactory().get('/')
        
        try:
            raise exceptions.Gone
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 410) 

    def test_unprocessable(self): 
        request = RequestFactory().get('/')
        
        try:
            raise exceptions.Unprocessable
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(res.content, '')

        content = 'some error here'
        try:
            raise exceptions.Unprocessable(content)
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 422) 
        self.assertJSONEqual(res.content, json.dumps(content))
        self.assertEqual(res['content-type'], 'application/json')
        
        content = {'error1': 'description', 'error2': 'description'}
        try:
            raise exceptions.Unprocessable(content)
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 422) 
        self.assertJSONEqual(res.content, json.dumps(content))
        self.assertEqual(res['content-type'], 'application/json')

    def test_unsupported_media_type(self):
        request = RequestFactory().get('/')

        try:
            raise exceptions.UnsupportedMediaType
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 415)            

    def test_not_implemented(self):
        request = RequestFactory().get('/')

        try:
            raise exceptions.NotImplemented
        except Exception, e:
            res = exceptions.handle_exception(e, request)
        self.assertEqual(res.status_code, 501)            

    def test_other_exception(self):
        request = RequestFactory().get('/')

        try:
            raise TypeError
        except TypeError, e:
            res = exceptions.handle_exception(e, request)

        self.assertEqual(res.status_code, 500)


