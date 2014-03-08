"""
This module tests the handler's ``is_method_allowed`` method.
"""

from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler                     
from firestone.exceptions import MethodNotAllowed
from django.test import TestCase
from django.test import RequestFactory
from django.http.response import HttpResponseNotAllowed


def init_handler(handler, request, *args, **kwargs):
    # Mimicking the initialization of the handler instance
    handler.request = request
    handler.args = args
    handler.kwargs = kwargs
    return handler


class TestBaseHandlerIsMethodAllowed(TestCase):
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(BaseHandler(), request)
        handler.http_methods = ('GET', 'POST', )

        self.handler = handler

    def test_is_method_allowed(self):
        handler = self.handler
        #GET 
        handler.request = RequestFactory().get('/')
        self.assertTrue(handler.is_method_allowed())

        # POST
        handler.request = RequestFactory().post('whateverpath/')
        self.assertTrue(handler.is_method_allowed())

        # DELETE
        handler.request = RequestFactory().delete('whateverpath/')
        self.assertRaises(MethodNotAllowed, handler.is_method_allowed)

        # PUT
        handler.request = RequestFactory().put('whateverpath/')
        self.assertRaises(MethodNotAllowed, handler.is_method_allowed)
    
class TestModelHandlerIsMethodAllowed(TestCase):        
    def setUp(self):
        request = RequestFactory().get('/')
        handler = init_handler(ModelHandler(), request)
        handler.http_methods = ('GET', 'POST', )

        self.handler = handler

    def test_is_method_allowed(self):
        handler = self.handler
        # GET
        handler.request = RequestFactory().get('whateverpath/')
        self.assertTrue(handler.is_method_allowed())

        # POST
        handler.request = RequestFactory().post('whateverpath/')
        self.assertTrue(handler.is_method_allowed())

        # DELETE
        handler.request = RequestFactory().delete('whateverpath/')
        self.assertRaises(MethodNotAllowed, handler.is_method_allowed)

        # PUT
        handler.request = RequestFactory().put('whateverpath/')
        self.assertRaises(MethodNotAllowed, handler.is_method_allowed)
 

        
        
