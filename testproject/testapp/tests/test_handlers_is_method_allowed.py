"""
This module tests the handler's ``is_method_allowed`` method.
"""

from firestone.handlers import BaseHandler
from firestone.handlers import ModelHandler                     
from firestone.exceptions import MethodNotAllowed
from django.test import TestCase
from django.test import RequestFactory
from django.http.response import HttpResponseNotAllowed


class TestBaseHandlerIsMethodAllowed(TestCase):
    def test_is_method_allowed(self):
        # Create GET request
        request = RequestFactory().get('whateverpath/')
        # Initialize the handler
        handler = BaseHandler()
        handler.http_methods = ('GET', 'POST', )

        # Call handler method ``is_method_allowed``
        self.assertTrue(handler.is_method_allowed(request))

        # Create POST request
        request = RequestFactory().post('whateverpath/')
        # Call handler method ``is_method_allowed``
        self.assertTrue(handler.is_method_allowed(request))

        # Create DELETE request
        request = RequestFactory().delete('whateverpath/')
        # Call handler method ``is_method_allowed``
        self.assertRaises(MethodNotAllowed, handler.is_method_allowed, request)

        # Create PUT request
        request = RequestFactory().put('whateverpath/')
        # Call handler method ``is_method_allowed``
        self.assertRaises(MethodNotAllowed, handler.is_method_allowed, request)
    
class TestModelHandlerIsMethodAllowed(TestCase):        
    def test_is_method_allowed(self):
        # Create GET request
        request = RequestFactory().get('whateverpath/')
        # Initialize the handler
        handler = ModelHandler()
        handler.http_methods = ('GET', 'POST', )
             
        # Call handler method ``is_method_allowed``
        self.assertTrue(handler.is_method_allowed(request))

        # Create POST request
        request = RequestFactory().post('whateverpath/')
        # Call handler method ``is_method_allowed``
        self.assertTrue(handler.is_method_allowed(request))

        # Create DELETE request
        request = RequestFactory().delete('whateverpath/')
        # Call handler method ``is_method_allowed``
        self.assertRaises(MethodNotAllowed, handler.is_method_allowed, request)

        # Create PUT request
        request = RequestFactory().put('whateverpath/')
        # Call handler method ``is_method_allowed``
        self.assertRaises(MethodNotAllowed, handler.is_method_allowed, request)
 

        
        
