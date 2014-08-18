"""
This module tests the behavior of method
``firestone.handlers.HandlerControlFlow.handle_exception"
"""
from firestone.handlers import BaseHandler
from firestone import exceptions
from django.test import TestCase
from django.test import RequestFactory
from django.conf import settings
from django.core.exceptions import NON_FIELD_ERRORS
import json


def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestHandleException(TestCase):
    """
    Testing whether the exceptions raised, are handled correctly by function
    ``handle_exception`` and generate the correct Http Response
    object.
    """
    def test_method_not_allowed_1(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        allowed_methods = ()
        try:
            raise exceptions.MethodNotAllowed(allowed_methods)
        except Exception, e:
            response, headers = handler.handle_exception(e)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response['Allow'], '')
        self.assertItemsEqual(headers, {})
        
    def test_method_not_allowed_2(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        allowed_methods = ('GET', 'POST')
        try:
            raise exceptions.MethodNotAllowed(allowed_methods)
        except Exception, e:
            response, headers = handler.handle_exception(e)

        self.assertEqual(response.status_code, 405)
        self.assertEqual(response['Allow'], ', '.join(allowed_methods))

    def test_bad_request_1(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        
        try:
            raise exceptions.BadRequest('')
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 400) 
        self.assertJSONEqual(response.content, json.dumps({NON_FIELD_ERRORS: ''}))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})


    def test_bad_request_2(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        content = 'some error here'
        try:
            raise exceptions.BadRequest(content)
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 400) 
        self.assertJSONEqual(response.content, json.dumps({NON_FIELD_ERRORS: content}))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})


    def test_bad_request_3(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        content = {'error1': 'description', 'error2': 'description'}
        try:
            raise exceptions.BadRequest(content)
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 400) 
        self.assertJSONEqual(response.content, json.dumps(content))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})

    def test_gone(self): 
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        
        try:
            raise exceptions.Gone
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 410) 
        self.assertItemsEqual(headers, {})

    def test_unprocessable_1(self): 
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        
        try:
            raise exceptions.Unprocessable
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.content, '')
        self.assertItemsEqual(headers, {})

    def test_unprocessable_2(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        content = 'some error here'
        try:
            raise exceptions.Unprocessable(content)
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 422) 
        self.assertJSONEqual(response.content, json.dumps(content))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})


    def test_unprocessable_3(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        content = {'error1': 'description', 'error2': 'description'}
        try:
            raise exceptions.Unprocessable(content)
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 422) 
        self.assertJSONEqual(response.content, json.dumps(content))
        self.assertItemsEqual(headers, {'content-type': 'application/json'})

    def test_unsupported_media_type(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        try:
            raise exceptions.UnsupportedMediaType
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 415)
        self.assertItemsEqual(headers, {})

    def test_not_implemented(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)

        try:
            raise exceptions.NotImplemented
        except Exception, e:
            response, headers = handler.handle_exception(e)
        self.assertEqual(response.status_code, 501)            
        self.assertItemsEqual(headers, {})

    def test_other_exception_debug_false(self):
        # With settings.DEBUG = False, the response should be empty
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        settings.DEBUG = False

        try:
            raise TypeError
        except TypeError, e:
            response, headers = handler.handle_exception(e)

        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.content)
        self.assertItemsEqual(headers, {'content-type': 'text/html; charset=utf-8'})

    def test_other_exception_debug_true(self):
        # With settings.DEBUG = False, the response should be non empty
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        settings.DEBUG = True

        try:
            raise TypeError
        except TypeError, e:
            response, headers = handler.handle_exception(e)

        self.assertEqual(response.status_code, 500)
        self.assertTrue(response.content)
        self.assertItemsEqual(headers, {'content-type': 'text/html; charset=utf-8'})


